from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

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
        service = build('calendar', 'v3', credentials=credentials)
        return service

    def get_events(self, date=None):
        # Obtener eventos
        if not date:
            events = self.service.events().list(
                calendarId=self.calendarid
            ).execute()
        else:
            start_date = f"{date}T00:00:00Z"
            end_date = f"{date}T23:59:59Z"
            events = self.service.events().list(
                calendarId=self.calendarid,
                timeMin=start_date,
                timeMax=end_date
            ).execute()
        return events.get('items', [])

    def get_event_by_date(self, start_date, end_date):
        # Obtener evento
        event = self.service.events().list(
            calendarId=self.calendarid,
            timeMin=start_date,
            timeMax=end_date
        ).execute()
        # devolver el id del evento
        return event["items"][0]["id"]

    def get_start_times(self, date):
        events = self.get_events(date)
        start_times = []
        for event in events:
            start_time = event['start']['dateTime']
            parsed_start_time = datetime.fromisoformat(start_time[:-6])
            hours_minutes = parsed_start_time.strftime("%H:%M")
            start_times.append(hours_minutes)
        return start_times

    def create_event(self, name_event, start_time, end_time, timezone, attendees=None):
        # Crear un evento
        event = {
            'summary': name_event,
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
        }

        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        try:
            created_event = self.service.events().insert(
                calendarId=self.calendarid,
                body=event
            ).execute()
        except HttpError as error:
            raise Exception(f"An error has occurred: {error}")

        return created_event

    def update_event(self, event_id, summary=None, start_time=None, end_time=None):
        # Actualizar un evento
        event = self.service.events().get(
            calendarId=self.calendarid,
            eventId=event_id
        ).execute()

        if summary:
            event['summary'] = summary
        if start_time:
            event['start']['dateTime'] = start_time
        if end_time:
            event['end']['dateTime'] = end_time

        updated_event = self.service.events().update(
            calendarId=self.calendarid,
            eventId=event_id,
            body=event
        ).execute()

        return updated_event

    def delete_event(self, event_id):
        # Eliminar un evento
        self.service.events().delete(
            calendarId=self.calendarid,
            eventId=event_id
        ).execute()

 
 