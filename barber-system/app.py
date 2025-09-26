import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
from gc_service import GoogleCalendar  # tu clase en gc_service.py

# ================= CONFIGURACIÓN GOOGLE CALENDAR =================
CREDENTIALS = "credentials.json"
CALENDAR_ID = "mariodanielq.p@gmail.com"
gc = GoogleCalendar(CREDENTIALS, CALENDAR_ID)

# ================= VARIABLES =================
servicios_raw = [
    "Perfil de cejas con guillet y gel de afeitar - 1.00 USD",
    "Afeitado o Perfilación de barba - 3.00 USD",
    "Corte Clásico con máquina - 5.00 USD",
    "Corte Clásico a tijera - 5.00 USD",
    "Freestyle (diseño personalizado) - 7.00 USD",
    "Semi Ondulado (ondas) - desde 20.00 USD",
    "VIP: Corte + Barba + Cejas + bebida de cortesía - 8.00 USD",
]

# Destacar VIP con emoji 🌟
servicios = []
for s in servicios_raw:
    if "VIP" in s:
        servicios.append(f"🌟 {s}")
    else:
        servicios.append(s)

empleados = ["Josué", "Ariel"]

# ================= CONFIG STREAMLIT =================
st.set_page_config(page_title="Seven Barber Club", page_icon="✂️", layout="centered")
st.image("assets/banner.png")
st.title("Seven Barber Club")
st.text("📍 Av. Unidad Nacional ente Juan Montalvo y Carabobo")

# ================= MENÚ =================
selected = option_menu(
    menu_title=None,
    options=["Servicios", "Reseñas", "Portafolio", "Detalles"],
    icons=["scissors", "chat-dots", "file-text", "pin"],
    orientation="horizontal",
)

# ================= SERVICIOS =================
if selected == "Servicios":
    st.subheader("Reservar cita")
    col1, col2 = st.columns(2)

    nombre = col1.text_input("Tu nombre")
    email = col2.text_input("Tu email")
    fecha = col1.date_input("Fecha")
    hora = col2.selectbox("Hora disponible", ["09:00", "10:00", "11:00", "12:00",
                                             "14:00","15:00","16:00", "17:00",
                                             "18:00", "19:00","20:00"])
    servicio = col1.selectbox("Servicio", servicios)
    empleado = col2.selectbox("Barbero", empleados)
    nota = col1.text_area("💬 Nota (opcional)")

    if st.button("Mostrar resumen"):
        st.markdown("### 📝 Resumen de tu reserva")
        st.markdown(f"**Nombre:** {nombre}")
        st.markdown(f"**Fecha:** {fecha}")
        st.markdown(f"**Hora:** {hora}")
        st.markdown(f"**Servicio:** {servicio}")
        st.markdown(f"**Barbero:** {empleado}")
        if nota:
            st.markdown(f"**Nota:** {nota}")

        if st.button("Confirmar reserva"):
            start = datetime.combine(fecha, datetime.strptime(hora, "%H:%M").time())
            end = start + timedelta(hours=1)

            try:
                gc.create_event(
                    name_event=f"Reserva: {servicio} con {empleado} - {nombre}",
                    start_time=start.isoformat(),
                    end_time=end.isoformat(),
                    timezone="America/Guayaquil"
                )
                st.success(f"✅ Reserva confirmada para {nombre} el {fecha} a las {hora} con {empleado} ({servicio}).")
            except Exception as e:
                st.error(f"❌ Error al crear la reserva: {str(e)}")
