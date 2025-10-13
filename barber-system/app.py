import streamlit as st
from datetime import datetime
from streamlit_option_menu import option_menu
from gc_service import GoogleCalendar
from PIL import Image

# ================== CONFIGURACIÓN DE PÁGINA ==================
st.set_page_config(page_title="WabiSabi Barber", layout="wide")

# Mostrar el logo centrado sin fondo
try:
    logo = Image.open("assets/logo-1.jpg")
    st.markdown("<div style='text-align:center; margin-top: 10px;'>", unsafe_allow_html=True)
    st.image(logo, width=250)
    st.markdown("</div>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error("❌ No se encontró el archivo 'assets/logo-1.jpg'. Verifica el nombre y la ubicación.")

# ================== CONFIGURACIÓN DE SEDES ==================
SEDES = {
    "Matriz - Centro": {
        "direccion": "Av. Unidad Nacional entre Juan Montalvo y Carabobo",
        "horario": "Lunes a Sábado: 09:00 - 20:00 | Domingo: 10:00 - 16:00",
        "maps_url": "https://www.google.com/maps?q=-2.90055,-79.00453",
        "img": "assets/logo-2.jpg",
        "barberos": [
            {"nombre": "Israel", "img": "assets/barber-isra.jpg", "calendar_id": "barbero_israel@gmail.com"},
            {"nombre": "Josué", "img": "assets/Josue_SedeMatriz.jpg", "calendar_id": "barbero_dani@gmail.com"},
            {"nombre": "Carlos", "img": "assets/Carlos_SedeMatriz.jpg", "calendar_id": "barbero_jose@gmail.com"},
        ],
    },
    "Sucursal Veloz": {
        "direccion": "Av. Amazonas y Colón",
        "horario": "Lunes a Sábado: 09:00 - 20:00 | Domingo: 10:00 - 16:00",
        "maps_url": "https://www.google.com/maps?q=-0.1807,-78.4827",
        "img": "assets/logo-1.jpg",
        "barberos": [
            {"nombre": "Marcos", "img": "assets/Marcos_SedeVeloz.jpg", "calendar_id": "barbero_jose_norte@gmail.com"},
            {"nombre": "Kevin", "img": "assets/Kevin_Sedeveloz.jpg", "calendar_id": "barbero_dani_norte@gmail.com"},
        ],
    },
    "Barber Training": {
        "direccion": "Av. América y Mariana de Jesús",
        "horario": "Lunes a Viernes: 09:00 - 19:00 | Sábado: 09:00 - 14:00",
        "maps_url": "https://www.google.com/maps?q=-0.1901,-78.4952",
        "img": "assets/logo-2.jpg",
        "barberos": [
            {"nombre": "Jose", "img": "assets/barber-jose.jpg", "calendar_id": "barbero_jose_training@gmail.com"},
            {"nombre": "Don Luis", "img": "assets/barber-don-luis.jpg", "calendar_id": "barbero_isra_training@gmail.com"},
        ],
    },
    "Sucursal Urban": {
        "direccion": "Calle Loja y Ayacucho",
        "horario": "Lunes a Sábado: 09:00 - 20:00 | Domingo: 10:00 - 16:00",
        "maps_url": "https://www.google.com/maps?q=-2.9189,-79.0226",
        "img": "assets/logo-1.jpg",
        "barberos": [
            {"nombre": "Anothony", "img": "assets/Anthony_SedeUrban.jpg", "calendar_id": "barbero_jose_sur@gmail.com"},
            {"nombre": "Isra", "img": "assets/barber-isra.jpg", "calendar_id": "barbero_isra_sur@gmail.com"},
        ],
    },
}

# ================== ESTILOS ==================
st.markdown("""
<style>
div[data-testid="stSidebar"] {display: none;}
div.stButton > button {
    background-color: #7df4d3 !important;
    color: #0c0c0c !important;
    font-weight: bold;
    border: none;
    border-radius: 10px;
    padding: 0.6em 1.2em;
}
div.stButton > button:hover {
    background-color: #5ce0b8 !important;
}
</style>
""", unsafe_allow_html=True)

# ================== MENÚ ==================
selected = option_menu(
    menu_title=None,
    options=["Servicios", "Barberos", "Agendar Cita", "Ubicación"],
    icons=["scissors", "people", "calendar-check", "geo-alt"],
    orientation="horizontal",
    default_index=0,
)

# ================== SERVICIOS ==================
SERVICIOS = [
    {"nombre": "Corte clásico con máquina", "precio": "6 USD", "tiempo": "35 min", "img": "assets/logo-1.jpg"},
    {"nombre": "Corte clásico moderno", "precio": "7 USD", "tiempo": "45 min", "img": "assets/logo-2.jpg"},
    {"nombre": "Corte clásico con tijera", "precio": "7 USD", "tiempo": "45 min", "img": "assets/logo-1.jpg"},
    {"nombre": "Corte + diseño de barba", "precio": "10 USD", "tiempo": "1h", "img": "assets/logo-1.jpg"},
    {"nombre": "Diseño de barba moderno", "precio": "5 USD", "tiempo": "30 min", "img": "assets/logo-2.jpg"},
    {"nombre": "Permanente o semi permanente", "precio": "20 USD", "tiempo": "1h 30 min", "img": "assets/logo-1.jpg"},
]

# ---- SERVICIOS ----
if selected == "Servicios":
    st.markdown("<h2 style='text-align:center;'> Nuestros Servicios 💈</h2>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, servicio in enumerate(SERVICIOS):
        with cols[i % 3]:
            st.image(servicio["img"], width=250)
            st.markdown(f"**{servicio['nombre']}**", unsafe_allow_html=True)
            st.markdown(f"💲 {servicio['precio']} — ⏱ {servicio['tiempo']}", unsafe_allow_html=True)

# ---- BARBEROS ----
elif selected == "Barberos":
    st.markdown("<h2 style='text-align:center;'>👨‍🔧 Nuestro Equipo de Barberos</h2>", unsafe_allow_html=True)
    sede = st.selectbox("🏢 Selecciona una sede", list(SEDES.keys()))
    st.markdown(f"### 💈 Barberos de {sede}")

    barberos = SEDES[sede]["barberos"]
    cols = st.columns(len(barberos))
    for col, barbero in zip(cols, barberos):
        with col:
            st.image(barbero["img"], width=250)
            st.markdown(f"<p style='text-align:center; color:black; font-weight:bold;'>{barbero['nombre']}</p>", unsafe_allow_html=True)

# ---- AGENDAR ----
elif selected == "Agendar Cita":
    st.markdown("## 📅 Reserva tu cita")

    with st.form("form_reserva"):
        nombre = st.text_input("👤 Nombre completo")
        email = st.text_input("📧 Correo electrónico")
        telefono = st.text_input("📞 Número de celular")

        sede = st.selectbox("🏢 Selecciona una sede", list(SEDES.keys()))
        barbero = st.selectbox("💇 Selecciona tu barbero", [b["nombre"] for b in SEDES[sede]["barberos"]])
        servicio = st.selectbox("💈 Servicio", [s["nombre"] for s in SERVICIOS])

        fecha = st.date_input("📆 Fecha de la cita", datetime.today())
        hora = st.time_input("⏰ Hora de la cita", datetime.now().time())

        enviar = st.form_submit_button("💾 Confirmar Reserva")

        if enviar:
            if nombre and email and telefono:
                calendar_id = next((b["calendar_id"] for b in SEDES[sede]["barberos"] if b["nombre"] == barbero), None)

                if calendar_id:
                    gc = GoogleCalendar("credentials.json", {sede: calendar_id})
                    try:
                        if not gc.is_available(sede, fecha, hora):
                            st.error("🚫 El barbero ya tiene una cita o actividad en esa hora.")
                        else:
                            gc.create_event(sede, nombre, telefono, email, servicio, barbero, fecha, hora)
                            st.success(f"✅ Cita reservada para {nombre} en {sede} con {barbero} el {fecha} a las {hora}")
                    except Exception as e:
                        st.error(f"❌ Error al crear la cita: {e}")
                else:
                    st.error("❌ No se encontró el calendario del barbero seleccionado.")
            else:
                st.warning("⚠️ Por favor, completa todos los campos obligatorios.")

# ---- UBICACIÓN ----
elif selected == "Ubicación":
    st.markdown("## 📍 Nuestras Sedes")

    for sede, data in SEDES.items():
        st.markdown(f"### 💈 {sede}")
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(data["img"], use_container_width=True)
        with col2:
            st.markdown(f"**📍 Dirección:** {data['direccion']}")
            st.markdown(f"**🕐 Horario:** {data['horario']}")
            st.markdown(f"[🗺️ Ver en Google Maps]({data['maps_url']})", unsafe_allow_html=True)
        st.markdown("---")

    st.markdown("**📞 Contacto General:** 098 840 2541")
