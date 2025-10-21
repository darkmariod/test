from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time

class GoogleCalendar:
    def __init__(self, creds_file: str):
        """Inicializa la conexión con Google Calendar usando credenciales de servicio."""
        self.creds_file = creds_file
        self.service = self._create_service()

    def _create_service(self):
        """Crea el cliente autenticado para interactuar con la API de Calendar."""
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        return build("calendar", "v3", credentials=creds)

    # ──────────────────────────────────────────────
    # ✅ Verifica disponibilidad sin solapamientos
    # ──────────────────────────────────────────────
    def is_available(self, calendar_id, fecha, hora):
        """Verifica si el barbero está disponible a la hora solicitada."""
        if hora < time(9, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 09:00 y las 19:00 horas.")

        start_time = datetime.combine(fecha, hora)
        end_time = start_time + timedelta(hours=1)

        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=(start_time - timedelta(minutes=59)).isoformat() + "Z",
            timeMax=(end_time + timedelta(minutes=59)).isoformat() + "Z",
            singleEvents=True
        ).execute()

        for e in events.get("items", []):
            if "start" not in e or "end" not in e:
                continue

            summary = e.get("summary", "").lower()
            # Si el evento indica que está ocupado, bloqueado o no disponible
            if any(palabra in summary for palabra in ["no disponible", "ocupado", "bloqueado"]):
                return False

            ev_start_raw = e["start"].get("dateTime") or e["start"].get("date")
            ev_end_raw = e["end"].get("dateTime") or e["end"].get("date")
            if not ev_start_raw or not ev_end_raw:
                continue

            if "T" not in ev_start_raw:
                event_start = datetime.combine(fecha, time(0, 0))
                event_end = datetime.combine(fecha, time(23, 59))
            else:
                event_start = datetime.fromisoformat(ev_start_raw.replace("Z", "+00:00"))
                event_end = datetime.fromisoformat(ev_end_raw.replace("Z", "+00:00"))

            if start_time < event_end and end_time > event_start:
                return False

        return True

    # ──────────────────────────────────────────────
    # ✅ Crear evento e invitar al cliente y barberos
    # ──────────────────────────────────────────────
    def create_event(self, calendar_id, nombre, telefono, email, servicio, barberos, fecha, hora, duracion_min=60):
        """Crea un evento en el calendario del barbero seleccionado."""
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
            sendUpdates="all"
        ).execute()

    # ──────────────────────────────────────────────
    # 🔎 Horas disponibles (filtra eventos bloqueados)
    # ──────────────────────────────────────────────
    def get_available_hours(self, calendar_id, fecha):
        """Devuelve horas disponibles excluyendo las ocupadas o bloqueadas."""
        horas_posibles = [time(h, 0) for h in range(9, 20)]
        disponibles = []

        for h in horas_posibles:
            try:
                if self.is_available(calendar_id, fecha, h):
                    disponibles.append(f"{h.hour}:00")
            except ValueError:
                continue

        return disponibles
