from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

class GoogleCalendar:
    def __init__(self, creds_file: str, calendar_id: str):
        creds = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.service = build("calendar", "v3", credentials=creds)
        self.calendar_id = calendar_id

    def is_time_available(self, start_time: datetime.datetime, end_time: datetime.datetime) -> bool:
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=start_time.isoformat() + "Z",
            timeMax=end_time.isoformat() + "Z",
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        events = events_result.get("items", [])
        return len(events) == 0

    def add_event(self, start_time: datetime.datetime, end_time: datetime.datetime, summary: str, description: str, email: str):
        event = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time.isoformat(), "timeZone": "America/Guayaquil"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "America/Guayaquil"},
            "attendees": [{"email": email}],
        }
        return self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
