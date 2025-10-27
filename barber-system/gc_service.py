from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time, date
from zoneinfo import ZoneInfo
import os
import json

# Zona horaria de Ecuador
TZ = ZoneInfo("America/Guayaquil")
UTC = ZoneInfo("UTC")


class GoogleCalendar:
    def __init__(self, creds_file: str = "credentials.json"):
        """
        Inicializa el servicio de Google Calendar.
        🔹 Usa la variable de entorno GOOGLE_CREDENTIALS_JSON (Railway)
        🔹 Usa el archivo local credentials.json si estás en desarrollo
        """
        creds_env = os.getenv("GOOGLE_CREDENTIALS_JSON")

        try:
            if creds_env:
                print("✅ Cargando credenciales desde entorno (Railway)")
                # Cargar el JSON como diccionario
                creds_info = json.loads(creds_env)
                creds = service_account.Credentials.from_service_account_info(
                    creds_info,
                    scopes=["https://www.googleapis.com/auth/calendar"]
                )
            else:
                print("⚙️ Cargando credenciales locales desde archivo")
                creds = service_account.Credentials.from_service_account_file(
                    creds_file,
                    scopes=["https://www.googleapis.com/auth/calendar"]
                )

            self.service = build("calendar", "v3", credentials=creds)
        except Exception as e:
            print("❌ Error al inicializar Google Calendar:", e)
            raise


    # ======================================================
    # UTILIDADES INTERNAS
    # ======================================================
    def _to_utc_iso(self, dt_local: datetime) -> str:
        """Convierte un datetime local a ISO en UTC."""
        if dt_local.tzinfo is None:
            dt_local = dt_local.replace(tzinfo=TZ)
        return dt_local.astimezone(UTC).isoformat()

    def _list_events(self, calendar_id: str, start_local: datetime, end_local: datetime) -> list:
        """Obtiene eventos dentro de un rango local (se envían como UTC al API)."""
        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=self._to_utc_iso(start_local),
            timeMax=self._to_utc_iso(end_local),
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return events.get("items", [])

    def _event_interval(self, event: dict) -> tuple[datetime, datetime]:
        """Retorna (start_utc, end_utc) SIEMPRE 'aware'."""
        if "dateTime" in event.get("start", {}):
            start = event["start"]["dateTime"]
            end = event["end"]["dateTime"]
            s = datetime.fromisoformat(start.replace("Z", "+00:00"))
            e = datetime.fromisoformat(end.replace("Z", "+00:00"))
            if s.tzinfo is None:
                s = s.replace(tzinfo=UTC)
            if e.tzinfo is None:
                e = e.replace(tzinfo=UTC)
            return s.astimezone(UTC), e.astimezone(UTC)

        start_date = event["start"]["date"]
        end_date = event["end"]["date"]
        s_local = datetime.fromisoformat(start_date).replace(tzinfo=TZ)
        e_local = datetime.fromisoformat(end_date).replace(tzinfo=TZ)
        return s_local.astimezone(UTC), e_local.astimezone(UTC)

    @staticmethod
    def _overlaps(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
        """True si hay cruce entre intervalos (todos en UTC)."""
        return a_start < b_end and a_end > b_start

    # ======================================================
    # DISPONIBILIDAD DE HORAS
    # ======================================================
    def get_available_hours(
        self,
        calendar_id: str,
        fecha: date,
        apertura_h: int = 10,
        cierre_h: int = 19,
        slot_every_min: int = 30
    ) -> list[str]:
        """Devuelve todas las horas disponibles (10:00 a 19:30 cada 30 min)."""
        start_day = datetime(fecha.year, fecha.month, fecha.day, apertura_h, 0, tzinfo=TZ)
        end_day = datetime(fecha.year, fecha.month, fecha.day, cierre_h, 30, tzinfo=TZ)

        minutos_total = int((end_day - start_day).total_seconds() // 60)
        all_slots = [
            (start_day + timedelta(minutes=m)).strftime("%H:%M")
            for m in range(0, minutos_total + 1, slot_every_min)
        ]

        events = self._list_events(calendar_id, start_day, end_day)
        busy_blocks = [self._event_interval(e) for e in events]

        for e in events:
            summary = (e.get("summary") or "").lower()
            if any(x in summary for x in ("no disponible", "vacaciones", "fuera de oficina", "permiso")):
                return []

        disponibles = []
        for slot in all_slots:
            hora_dt = datetime.strptime(slot, "%H:%M").time()
            start_local = datetime.combine(fecha, hora_dt).replace(tzinfo=TZ)
            end_local = start_local + timedelta(minutes=slot_every_min)

            s_utc = start_local.astimezone(UTC)
            e_utc = end_local.astimezone(UTC)

            ocupado = any(self._overlaps(s_utc, e_utc, b0, b1) for (b0, b1) in busy_blocks)
            if not ocupado:
                disponibles.append(slot)

        return disponibles

    # ======================================================
    # CREAR EVENTO
    # ======================================================
    def create_event(
        self,
        calendar_id: str,
        nombre: str,
        telefono: str,
        email: str,
        servicio: str,
        fecha: date,
        hora: time,
        duracion_min: int = 60
    ):
        """Crea un evento en el calendario."""
        if hora < time(10, 0) or hora > time(19, 30):
            raise ValueError("Solo se puede agendar entre 10:00 y 19:30.")

        start_local = datetime.combine(fecha, hora).replace(tzinfo=TZ)
        end_local = start_local + timedelta(minutes=duracion_min)

        existing = self._list_events(calendar_id, start_local, end_local)
        for e in existing:
            e_start, e_end = self._event_interval(e)
            if self._overlaps(start_local.astimezone(UTC), end_local.astimezone(UTC), e_start, e_end):
                raise ValueError("⚠️ Ya existe una cita para este barbero en ese horario.")

        event = {
            "summary": f"{servicio} - {nombre}",
            "description": (
                f"Cliente: {nombre}\n"
                f"Teléfono: {telefono}\n"
                f"Correo: {email}\n"
                f"Servicio: {servicio}"
            ),
            "start": {"dateTime": start_local.isoformat(), "timeZone": str(TZ)},
            "end": {"dateTime": end_local.isoformat(), "timeZone": str(TZ)},
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": "popup", "minutes": 30},
                    {"method": "popup", "minutes": 10},
                ],
            },
        }

        self.service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates="none"
        ).execute()
