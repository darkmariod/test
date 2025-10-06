# gc_service.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

class GoogleCalendar:
    def __init__(self, creds_file, calendar_ids):
        creds = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.service = build("calendar", "v3", credentials=creds)
        self.calendar_ids = calendar_ids  # dict con las sedes

    def create_event(self, sede, nombre, telefono, email, servicio, barbero, fecha, hora):
        # Convertir hora a formato datetime ISO
        fecha_hora_inicio = datetime.datetime.combine(fecha, hora)
        fecha_hora_fin = fecha_hora_inicio + datetime.timedelta(minutes=45)

        event = {
            "summary": f"Cita: {servicio} con {barbero}",
            "description": f"Cliente: {nombre}\nTel: {telefono}\nEmail: {email}\nSede: {sede}",
            "start": {"dateTime": fecha_hora_inicio.isoformat(), "timeZone": "America/Guayaquil"},
            "end": {"dateTime": fecha_hora_fin.isoformat(), "timeZone": "America/Guayaquil"},
        }

        sede_id = self.calendar_ids.get(sede)
        if not sede_id:
            raise ValueError(f"Sede '{sede}' no tiene calendar_id asignado")

        event = self.service.events().insert(calendarId=sede_id, body=event).execute()
        return event
