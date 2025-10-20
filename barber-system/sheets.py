from google.oauth2 import service_account
from googleapiclient.discovery import build

class SheetsService:
    def __init__(self, creds_file: str, sheet_id: str):
        creds = service_account.Credentials.from_service_account_file(
            creds_file,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet_id = sheet_id

    def add_row(self, data):
        body = {"values": [data]}
        self.service.spreadsheets().values().append(
            spreadsheetId=self.sheet_id,
            range="Citas!A1",
            valueInputOption="RAW",
            body=body
        ).execute()
