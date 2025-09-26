import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
from gc_service import GoogleCalendar

# ================= CONFIGURACIÓN GOOGLE CALENDAR =================
CREDENTIALS = "credentials.json"
CALENDAR_ID = "mariodanielq.p@gmail.com"  # tu calendario real
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
servicios = [f"🌟 {s}" if "VIP" in s else s for s in servicios_raw]

empleados = ["Josué", "Ariel"]

# Horarios de atención
horarios = {
    "Lunes": "09:00 - 21:00",
    "Martes": "09:00 - 21:00",
    "Miércoles": "09:00 - 21:00",
    "Jueves": "09:00 - 21:00",
    "Viernes": "09:00 - 21:00",
    "Sábado": "09:00 - 21:00",
    "Domingo": "09:00 - 21:00"
}

# ================= CONFIG STREAMLIT =================
st.set_page_config(page_title="Seven Barber Club", page_icon="✂️", layout="centered")
st.image("assets/banner.png")
st.title("Seven Barber Club")
st.text("📍 Av. Unidad Nacional entre Juan Montalvo y Carabobo")

# ================= MENÚ =================
selected = option_menu(
    menu_title=None,
    options=["Servicios", "Reseñas", "Portafolio", "Detalles"],
    icons=["scissors", "chat-dots", "file-text", "pin"],
    orientation="horizontal",
)

# ================= PORTAFOLIO =================
if selected == "Portafolio":
    st.image("assets/corte-1.jpg", caption="Degradado básico")
    st.image("assets/corte-2.jpg", caption="Corte más barba")
    st.image("assets/corte-3.jpg", caption="Raya personalizada")

# ================= DETALLES =================
if selected == "Detalles":
    st.image("assets/map.JPG")
    st.markdown("[📍 Ver dirección en Google Maps](https://www.google.com/maps)")

    st.subheader("💈 Barberos")
    c1, c2 = st.columns(2)
    c1.image("assets/barber-1.png", caption="Josué")
    c2.image("assets/barber-2.png", caption="Ariel")

    st.markdown("### 🕒 Horarios de Atención")
    col1, col2 = st.columns(2)
    for dia, hora in horarios.items():
        col1.markdown(f"**📅 {dia}**")
        col2.markdown(f"⏰ {hora}")

    st.markdown("📞 <b>098 840 2541</b>", unsafe_allow_html=True)
    st.markdown("📷 [Instagram](https://www.instagram.com)")

# ================= RESEÑAS =================
if selected == "Reseñas":
    st.image("assets/opinion1.JPG")
    st.image("assets/opinion2.JPG")

# ================= SERVICIOS =================
if selected == "Servicios":
    st.subheader("Reservar cita")
    col1, col2 = st.columns(2)

    nombre = col1.text_input("Tu nombre")
    email = col2.text_input("Tu email")
    fecha = col1.date_input("Fecha")
    hora = col2.selectbox("Hora disponible", ["09:00","10:00","11:00","12:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00"])
    servicio = col1.selectbox("Servicio", servicios)
    empleado = col2.selectbox("Barbero", empleados)
    nota = col1.text_area("💬 Nota (opcional)")

    if st.button("Reservar"):
        start = datetime.combine(fecha, datetime.strptime(hora, "%H:%M").time())
        end = start + timedelta(hours=1)

        try:
            # Crear evento en Google Calendar
            gc.create_event(
                name_event=f"Reserva: {servicio} con {empleado} - {nombre}",
                start_time=start.isoformat(),
                end_time=end.isoformat(),
                timezone="America/Guayaquil"
            )
            st.success(f"✅ Reserva confirmada para {nombre} el {fecha} a las {hora} con {empleado} ({servicio}).")
        except Exception as e:
            st.error(f"❌ Error al crear la reserva: {str(e)}")
