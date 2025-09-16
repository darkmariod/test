from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleCalendar:
    def __init__(self, credentials_file, calendarid):
        self.credentials_file = credentials_file
        self.calendarid = calendarid
        self.service = self._create_service()

    def _create_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=credentials)

    def create_event(self, name_event, start_time, end_time, timezone, attendees=None):
        """Crea un evento en Google Calendar"""
        event = {
            'summary': name_event,
            'start': {'dateTime': start_time, 'timeZone': timezone},
            'end': {'dateTime': end_time, 'timeZone': timezone},
        }

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        try:
            created_event = self.service.events().insert(
                calendarId=self.calendarid,
                body=event
            ).execute()
            return created_event
        except HttpError as error:
            raise Exception(f"❌ Error creando evento: {error}")
