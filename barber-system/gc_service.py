from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleCalendar:
    def __init__(self, credentials_file, calendar_id):
        self.credentials_file = credentials_file
        self.calendar_id = calendar_id
        self.service = self._create_service()

    def _create_service(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        return build('calendar', 'v3', credentials=credentials)

    def create_event(self, name_event, start_time, end_time, timezone):
        event = {
            'summary': name_event,
            'start': {'dateTime': start_time, 'timeZone': timezone},
            'end': {'dateTime': end_time, 'timeZone': timezone},
        }
        created_event = self.service.events().insert(
            calendarId=self.calendar_id,
            body=event
        ).execute()
        return created_event
