from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

class GoogleCalendar:
    def __init__(self, creds_file, calendar_ids):
        self.creds_file = creds_file
        self.calendar_ids = calendar_ids  # dict {sede: calendar_id}
        self.service = self._create_service()

    def _create_service(self):
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=creds)

    def is_available(self, sede, fecha, hora):
        """Verifica si hay disponibilidad en esa sede, fecha y hora."""
        calendar_id = self.calendar_ids[sede]
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

        # Si hay eventos, no está disponible
        return len(events.get('items', [])) == 0

    def create_event(self, sede, nombre, telefono, email, servicio, barbero, fecha, hora):
        """Crea evento en el calendario correspondiente."""
        calendar_id = self.calendar_ids[sede]
        start_time = datetime.combine(fecha, hora)
        end_time = start_time + timedelta(hours=1)
        start_iso = start_time.isoformat()
        end_iso = end_time.isoformat()

        disponible = self.is_available(sede, fecha, hora)
        if not disponible:
            raise ValueError("🚫 El barbero ya tiene una cita o actividad en esa hora.")

        descripcion = f"Cliente: {nombre}\nTeléfono: {telefono}\nCorreo: {email}\nBarbero: {barbero}"
        evento = {
            'summary': f"{servicio} - {nombre}",
            'description': descripcion,
            'start': {'dateTime': start_iso, 'timeZone': 'America/Guayaquil'},
            'end': {'dateTime': end_iso, 'timeZone': 'America/Guayaquil'}
        }

        self.service.events().insert(calendarId=calendar_id, body=evento).execute()

    def get_events(self, sede, date):
        """Obtiene todos los eventos del día en esa sede."""
        calendar_id = self.calendar_ids[sede]
        start = datetime.combine(date, datetime.min.time()).isoformat() + "Z"
        end = datetime.combine(date, datetime.max.time()).isoformat() + "Z"

        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start,
            timeMax=end,
            singleEvents=True
        ).execute()

        return events.get('items', [])
