import streamlit as st
import datetime as dt
from zoneinfo import ZoneInfo
from gc_service import GoogleCalendar

st.set_page_config(page_title="Reservas Barbería", page_icon="💈")

st.title("💈 Barbería - Reserva tu cita")

gc = GoogleCalendar()

# Formulario
with st.form("reserva_form"):
    nombre = st.text_input("Nombre completo")
    email = st.text_input("Correo electrónico (obligatorio)")
    fecha = st.date_input("Selecciona el día", dt.date.today())
    hora = st.time_input("Selecciona la hora", dt.time(9, 0))  # por defecto 09:00
    duracion = st.number_input("Duración en horas", min_value=1, max_value=3, value=1)

    submitted = st.form_submit_button("Reservar cita")

if submitted:
    if not email:
        st.error("⚠️ El correo electrónico es obligatorio.")
    else:
        start = dt.datetime.combine(fecha, hora).replace(tzinfo=ZoneInfo("America/Guayaquil"))
        end = start + dt.timedelta(hours=duracion)

        result = gc.create_event(
            name_event=f"Cita Barbería - {nombre}",
            start_time=start,
            end_time=end,
            timezone="America/Guayaquil",
            email=email
        )

        if result["status"] == "success":
            st.success(result["message"])
            st.markdown(f"[Ver en Google Calendar]({result['event_link']})")
        else:
            st.error(result["message"])
