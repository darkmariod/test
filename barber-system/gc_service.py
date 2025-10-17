from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time

class GoogleCalendar:
    def __init__(self, creds_file: str):
        """
        Inicializa la conexión con Google Calendar usando credenciales de servicio.
        """
        self.creds_file = creds_file
        self.service = self._create_service()

    def _create_service(self):
        """
        Crea el cliente autenticado para interactuar con la API de Calendar.
        """
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        return build("calendar", "v3", credentials=creds)

    # ──────────────────────────────────────────────
    # ✅ Verifica disponibilidad sin solapamientos
    # ──────────────────────────────────────────────
    def is_available(self, calendar_id, fecha, hora):
        """
        Verifica si el barbero está disponible en la fecha y hora solicitada.
        Detecta solapamientos con cualquier evento existente.
        Reglas:
          - Atiende de 09:00 a 19:00 (inclusive el inicio de cada hora).
          - Cada cita dura 60 minutos por defecto (lo puedes variar en create_event).
        """
        if hora < time(9, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 09:00 y las 19:00 horas.")

        start_time = datetime.combine(fecha, hora)
        end_time = start_time + timedelta(hours=1)

        # Buscar eventos alrededor de ese bloque de 1h para detectar solapamientos
        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=(start_time - timedelta(minutes=59)).isoformat() + "Z",
            timeMax=(end_time + timedelta(minutes=59)).isoformat() + "Z",
            singleEvents=True
        ).execute()

        for e in events.get("items", []):
            # Validación defensiva
            if "start" not in e or "end" not in e:
                continue

            # Convertir a datetime (asumiendo que vienen con 'Z'; se normaliza a tz-aware)
            ev_start_raw = e["start"].get("dateTime") or e["start"].get("date")
            ev_end_raw = e["end"].get("dateTime") or e["end"].get("date")
            if not ev_start_raw or not ev_end_raw:
                continue

            # Cuando es evento "de día completo" vendrá como 'date' (00:00 a 00:00 del día siguiente)
            if "T" not in ev_start_raw:
                # Evento de día completo: lo consideramos como ocupado todo el día
                # Interpretar como [00:00, 23:59]
                event_start = datetime.combine(fecha, time(0, 0))
                event_end = datetime.combine(fecha, time(23, 59))
            else:
                event_start = datetime.fromisoformat(ev_start_raw.replace("Z", "+00:00"))
                event_end = datetime.fromisoformat(ev_end_raw.replace("Z", "+00:00"))

            # Verifica si los intervalos se cruzan: [start_time, end_time) vs evento
            if start_time < event_end and end_time > event_start:
                return False

        return True

    # ──────────────────────────────────────────────
    # ✅ Crear evento e invitar a barberos y cliente
    # ──────────────────────────────────────────────
    def create_event(self, calendar_id, nombre, telefono, email, servicio, barberos, fecha, hora, duracion_min=60):
        """
        Crea un evento en el calendario del barbero seleccionado e invita al cliente y barberos de la sede.
        - calendar_id: correo del barbero principal (donde se inserta el evento).
        - barberos: lista de correos ['correo1@gmail.com', 'correo2@gmail.com'] (asistentes/invitados).
        - duracion_min: duración del servicio (por defecto 60 minutos).
        """
        if hora < time(9, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 09:00 y las 19:00 horas.")

        start_time = datetime.combine(fecha, hora)
        end_time = start_time + timedelta(minutes=duracion_min)

        event = {
            "summary": f"{servicio} - {nombre}",
            "description": (
                f"Cliente: {nombre}\n"
                f"Teléfono: {telefono}\n"
                f"Correo: {email}\n"
                f"Servicio: {servicio}\n"
                f"Duración: {duracion_min} minutos"
            ),
            "start": {"dateTime": start_time.isoformat(), "timeZone": "America/Guayaquil"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "America/Guayaquil"},
            "attendees": [{"email": email}] + [{"email": b} for b in barberos],
        }

        self.service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates="all"  # envía invitaciones por correo
        ).execute()

    # ──────────────────────────────────────────────
    # 🔎 (Opcional) Horas disponibles para un día
    # ──────────────────────────────────────────────
    def get_available_hours(self, calendar_id, fecha):
        """
        Devuelve una lista de horas disponibles (strings 'HH:00') entre 09:00 y 19:00
        para el calendario indicado y la fecha dada.
        Útil para que el select de horas del formulario muestre solo las libres.
        """
        horas_posibles = [time(h, 0) for h in range(9, 20)]  # 9..19 inclusive
        disponibles = []

        # Obtenemos todos los eventos del día de una sola consulta
        day_start = datetime.combine(fecha, time(0, 0))
        day_end = datetime.combine(fecha, time(23, 59))

        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=day_start.isoformat() + "Z",
            timeMax=day_end.isoformat() + "Z",
            singleEvents=True
        ).execute()

        # Construimos una lista de intervalos ocupados
        ocupados = []
        for e in events.get("items", []):
            ev_start_raw = e["start"].get("dateTime") or e["start"].get("date")
            ev_end_raw = e["end"].get("dateTime") or e["end"].get("date")
            if not ev_start_raw or not ev_end_raw:
                continue

            if "T" not in ev_start_raw:
                ev_start = datetime.combine(fecha, time(0, 0))
                ev_end = datetime.combine(fecha, time(23, 59))
            else:
                ev_start = datetime.fromisoformat(ev_start_raw.replace("Z", "+00:00"))
                ev_end = datetime.fromisoformat(ev_end_raw.replace("Z", "+00:00"))
            ocupados.append((ev_start, ev_end))

        # Para cada hora posible, validamos que NO se solape con ningún bloque ocupado
        for h in horas_posibles:
            start = datetime.combine(fecha, h)
            end = start + timedelta(hours=1)
            solapa = False
            for (evs, eve) in ocupados:
                if start < eve and end > evs:
                    solapa = True
                    break
            if not solapa:
                disponibles.append(f"{h.hour}:00")

        return disponibles
