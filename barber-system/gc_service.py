from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time

class GoogleCalendar:
    def __init__(self, creds_file):
        self.creds_file = creds_file
        self.service = self._create_service()

    def _create_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        return build("calendar", "v3", credentials=creds)

    def is_available(self, calendar_id, fecha, hora):
        """Verifica si hay disponibilidad y que la hora esté entre 10:00 y 19:00."""
        if hora < time(10, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 10:00 y 19:00 horas.")

        start_time = datetime.combine(fecha, hora)
        end_time = start_time + timedelta(hours=1)

        start_iso = start_time.isoformat() + "Z"
        end_iso = end_time.isoformat() + "Z"

        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_iso,
            timeMax=end_iso,
            singleEvents=True
        ).execute()

        return len(events.get("items", [])) == 0

    def create_event(self, calendar_id, nombre, telefono, email, servicio, barberos, fecha, hora):
        """
        Crea evento e invita al cliente + todos los barberos de la sede.
        barberos: lista de correos ['correo1@gmail.com', 'correo2@gmail.com']
        """
        if hora < time(10, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 10:00 y 19:00 horas.")

        start_time = datetime.combine(fecha, hora)
        end_time = start_time + timedelta(hours=1)

        event = {
            "summary": f"{servicio} - {nombre}",
            "description": f"Cliente: {nombre}\nTeléfono: {telefono}\nCorreo: {email}",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "America/Guayaquil"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "America/Guayaquil"},
            "attendees": [{"email": email}] + [{"email": b} for b in barberos],
        }

        self.service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates="all"  # envía invitaciones a todos los asistentes
        ).execute()
