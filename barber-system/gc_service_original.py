from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo

# Zona horaria local (ajusta si cambia la ciudad)
TZ = ZoneInfo("America/Guayaquil")

class GoogleCalendar:
    def __init__(self, creds_file: str):
        """Inicializa la conexión con Google Calendar usando credenciales de servicio."""
        self.creds_file = creds_file
        self.service = self._create_service()

    def _create_service(self):
        """Crea el cliente autenticado para interactuar con la API de Calendar."""
        creds = service_account.Credentials.from_service_account_file(
            self.creds_file,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        return build("calendar", "v3", credentials=creds)

    # ---------- Utilidades internas ----------
    def _to_utc_iso(self, dt_local: datetime) -> str:
        """Convierte datetime con TZ local a ISO8601 en UTC (RFC3339) para la API."""
        if dt_local.tzinfo is None:
            dt_local = dt_local.replace(tzinfo=TZ)
        dt_utc = dt_local.astimezone(ZoneInfo("UTC"))
        return dt_utc.isoformat()

    def _list_events(self, calendar_id: str, start_local: datetime, end_local: datetime) -> list:
        """Obtiene eventos entre 'start_local' y 'end_local' respetando TZ local."""
        time_min = self._to_utc_iso(start_local)
        time_max = self._to_utc_iso(end_local)

        events = self.service.events().list(
            calendarId=calendar_id,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        return events.get("items", [])

    def _event_interval(self, event: dict) -> tuple:
        """
        Retorna (start_aware_utc, end_aware_utc).
        Soporta eventos de día completo (date) y con hora (dateTime).
        """
        # start
        if "dateTime" in event.get("start", {}):
            start = datetime.fromisoformat(event["start"]["dateTime"].replace("Z", "+00:00"))
        else:
            # all-day: bloquea todo el día (00:00 a 23:59:59)
            # Google devuelve date en formato YYYY-MM-DD (sin hora)
            d = datetime.fromisoformat(event["start"]["date"])
            start = d.replace(tzinfo=ZoneInfo("UTC"))  # comienza a 00:00 UTC

        # end
        if "dateTime" in event.get("end", {}):
            end = datetime.fromisoformat(event["end"]["dateTime"].replace("Z", "+00:00"))
        else:
            # all-day: termina al inicio del día siguiente
            d = datetime.fromisoformat(event["end"]["date"])
            end = d.replace(tzinfo=ZoneInfo("UTC"))

        return (start, end)

    def _overlaps(self, a_start, a_end, b_start, b_end) -> bool:
        """True si [a_start, a_end) solapa con [b_start, b_end)."""
        return a_start < b_end and a_end > b_start

    # ---------- Disponibilidad por hora ----------
    def get_available_hours(self, calendar_id: str, fecha, apertura_h=9, cierre_h=19, duracion_min=60) -> list:
        """
        Devuelve una lista de strings "HH:00" con las horas disponibles para 'fecha'
        en el calendario 'calendar_id', considerando:
          - Agenda existente (evita solapamientos)
          - Horario de trabajo [apertura_h, cierre_h)
          - Duración del servicio en minutos
        """
        # Construir inicio y fin del día en TZ local
        day_start_local = datetime(fecha.year, fecha.month, fecha.day, 0, 0, tzinfo=TZ)
        day_end_local   = datetime(fecha.year, fecha.month, fecha.day, 23, 59, tzinfo=TZ)

        # Obtener todos los eventos del día (en UTC desde Google)
        events = self._list_events(calendar_id, day_start_local, day_end_local)
        busy_utc_blocks = []
        for e in events:
            e_start, e_end = self._event_interval(e)
            busy_utc_blocks.append((e_start, e_end))

        # Generar slots candidatos (local)
        available = []
        # Último inicio permitido para un slot de 'duracion_min' dentro de cierre_h
        last_start = cierre_h * 60 - duracion_min
        for minutes in range(apertura_h * 60, last_start + 1, 60):
            h = minutes // 60
            m = minutes % 60
            start_local = datetime(fecha.year, fecha.month, fecha.day, h, m, tzinfo=TZ)
            end_local = start_local + timedelta(minutes=duracion_min)

            # Convertir a UTC para comparar con eventos de Google
            start_utc = start_local.astimezone(ZoneInfo("UTC"))
            end_utc = end_local.astimezone(ZoneInfo("UTC"))

            # Verificar solapamiento con cualquier evento ocupado
            is_free = True
            for b_start, b_end in busy_utc_blocks:
                if self._overlaps(start_utc, end_utc, b_start, b_end):
                    is_free = False
                    break

            if is_free:
                available.append(f"{h:02d}:00")

        return available

    # ---------- Verificación puntual ----------
    def is_available(self, calendar_id: str, fecha, hora: time, apertura_h=9, cierre_h=19, duracion_min=60) -> bool:
        """
        True si el barbero (calendar_id) NO tiene eventos que solapen
        con [fecha+hora, fecha+hora+duracion].
        También valida que la hora esté dentro del rango laboral.
        """
        if hora < time(apertura_h, 0) or hora > time(cierre_h, 0):
            raise ValueError(f"⏰ Solo se pueden agendar entre las {apertura_h}:00 y las {cierre_h}:00 horas.")

        start_local = datetime.combine(fecha, hora).replace(tzinfo=TZ)
        end_local = start_local + timedelta(minutes=duracion_min)

        events = self._list_events(calendar_id, start_local, end_local)
        for e in events:
            e_start, e_end = self._event_interval(e)
            # Convertimos nuestro intervalo a UTC para comparar
            s_utc = start_local.astimezone(ZoneInfo("UTC"))
            e_utc = end_local.astimezone(ZoneInfo("UTC"))
            if self._overlaps(s_utc, e_utc, e_start, e_end):
                return False
        return True

    # ---------- Crear evento ----------
    def create_event(self, calendar_id, nombre, telefono, email, servicio, barberos, fecha, hora, duracion_min=60):
        """
        Crea un evento en el calendario del barbero seleccionado e invita al cliente y barberos de la sede.
        - calendar_id: correo del barbero principal.
        - barberos: lista de correos ['correo1@gmail.com', 'correo2@gmail.com']
        - duracion_min: duración del servicio (por defecto 60 minutos)
        """
        # Validar horario laboral
        if hora < time(9, 0) or hora > time(19, 0):
            raise ValueError("⏰ Solo se pueden agendar citas entre las 9:00 y las 19:00 horas.")

        start_local = datetime.combine(fecha, hora).replace(tzinfo=TZ)
        end_local = start_local + timedelta(minutes=duracion_min)

        event = {
            "summary": f"{servicio} - {nombre}",
            "description": (
                f"Cliente: {nombre}\n"
                f"Teléfono: {telefono}\n"
                f"Correo: {email}\n"
                f"Servicio: {servicio}\n"
                f"Duración: {duracion_min} minutos"
            ),
            "start": {"dateTime": start_local.isoformat(), "timeZone": str(TZ)},
            "end": {"dateTime": end_local.isoformat(), "timeZone": str(TZ)},
            "attendees": [{"email": email}] + [{"email": b} for b in barberos],
        }

        self.service.events().insert(
            calendarId=calendar_id,
            body=event,
            sendUpdates="all"
        ).execute()
