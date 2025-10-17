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
        """
        Verifica si el barbero está disponible en la fecha y hora solicitada.
        Detecta solapamientos con cualquier evento existente.
        """
        if hora < time(10, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 10:00 y las 19:00 horas.")

        start_time = datetime.combine(fecha, hora)
        end_time = start_time + timedelta(hours=1)

        # Buscar eventos en un rango amplio para detectar solapamientos
        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=(start_time - timedelta(minutes=59)).isoformat() + "Z",
            timeMax=(end_time + timedelta(minutes=59)).isoformat() + "Z",
            singleEvents=True
        ).execute()

        for e in events.get("items", []):
            if "start" not in e or "end" not in e:
                continue
            event_start = datetime.fromisoformat(e["start"]["dateTime"].replace("Z", "+00:00"))
            event_end = datetime.fromisoformat(e["end"]["dateTime"].replace("Z", "+00:00"))
            # Verifica si los intervalos se cruzan
            if start_time < event_end and end_time > event_start:
                return False
        return True

    # ──────────────────────────────────────────────
    # ✅ Crear evento e invitar a barberos y cliente
    # ──────────────────────────────────────────────
    def create_event(self, calendar_id, nombre, telefono, email, servicio, barberos, fecha, hora, duracion_min=60):
        """
        Crea un evento en el calendario del barbero seleccionado e invita al cliente y barberos de la sede.
        - calendar_id: correo del barbero principal.
        - barberos: lista de correos ['correo1@gmail.com', 'correo2@gmail.com']
        - duracion_min: duración del servicio (por defecto 60 minutos)
        """
        if hora < time(10, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 10:00 y las 19:00 horas.")

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

        # Crear evento en el calendario y enviar invitaciones
        self.service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates="all"
        ).execute()
