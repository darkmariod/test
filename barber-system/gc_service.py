from __future__ import print_function
import os.path
import datetime as dt
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendar:
    def __init__(self, calendar_id="mariodanielq.p@gmail.com"):
        self.creds = None
        self.calendar_id = calendar_id

        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())

        self.service = build("calendar", "v3", credentials=self.creds)

    def is_slot_available(self, start_time, end_time, timezone="America/Guayaquil"):
        """Verifica si hay disponibilidad en el rango de hora"""
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        return len(events) == 0  # True si está libre

    def create_event(self, name_event, start_time, end_time, timezone, email):
        """Crea un evento si hay disponibilidad"""
        if not email:
            return {"status": "error", "message": "⚠️ El correo electrónico es obligatorio."}

        if not self.is_slot_available(start_time, end_time, timezone):
            return {"status": "error", "message": "❌ Lo sentimos, esa hora ya está reservada. Elige otra."}

        event = {
            "summary": name_event,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": timezone,
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": timezone,
            },
            "attendees": [{"email": email}],
        }

        created_event = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()

        return {
            "status": "success",
            "message": f"✅ Tu cita fue reservada el {start_time.strftime('%d/%m/%Y')} de {start_time.strftime('%H:%M')} a {end_time.strftime('%H:%M')}.",
            "event_link": created_event.get("htmlLink")
        }
