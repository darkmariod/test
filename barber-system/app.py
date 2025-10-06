import streamlit as st
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
from gc_service import GoogleCalendar

# ================== CONFIGURACIÓN DE PÁGINA ==================
st.set_page_config(page_title="WabiSabi 💈", page_icon="💈", layout="wide")

# ================== CONFIGURACIÓN DE SEDES ==================
SEDES = {
    "Matriz - Centro": {
        "barberos": [
            {"nombre": "Alex", "img": "assets/barber-isra.jpg"},
            {"nombre": "Luis", "img": "assets/barber-dani.jpg"},
            {"nombre": "Carlos", "img": "assets/barber-jose.jpg"},
        ],
        "calendar_id": "calendario_matriz_id@group.calendar.google.com"
    },
    "Sucursal Norte": {
        "barberos": [
            {"nombre": "Mario", "img": "assets/barber-mario.jpg"},
            {"nombre": "David", "img": "assets/barber-david.jpg"},
        ],
        "calendar_id": "calendario_norte_id@group.calendar.google.com"
    },
    "Sucursal Sur": {
        "barberos": [
            {"nombre": "Andrés", "img": "assets/barber-andres.jpg"},
            {"nombre": "Pedro", "img": "assets/barber-pedro.jpg"},
        ],
        "calendar_id": "calendario_sur_id@group.calendar.google.com"
    },
    "Sucursal Este": {
        "barberos": [
            {"nombre": "Kevin", "img": "assets/barber-kevin.jpg"},
            {"nombre": "Roberto", "img": "assets/barber-roberto.jpg"},
        ],
        "calendar_id": "calendario_este_id@group.calendar.google.com"
    }
}

# ================== ESTILOS ==================
st.markdown("""
<style>
div[data-testid="stSidebar"] {display: none;}

/* ===== MENÚ SUPERIOR ===== */
nav[data-testid="stHorizontalBlock"] {
    background-color: #0c0c0c !important;
    border-radius: 10px;
    padding: 8px 0;
}

/* ===== BOTONES ===== */
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
    color: black !important;
}

/* ===== TEXTOS ===== */
span.precio {
    color: black !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================== MENÚ SUPERIOR ==================
selected = option_menu(
    menu_title=None,
    options=["Servicios", "Barberos", "Agendar Cita", "Ubicación"],
    icons=["scissors", "people", "calendar-check", "geo-alt"],
    orientation="horizontal",
    default_index=0,
    styles={
        "container": {"background-color": "#0c0c0c", "padding": "8px", "border-radius": "10px"},
        "icon": {"color": "#7df4d3", "font-size": "20px"},
        "nav-link": {
            "color": "#7df4d3",
            "font-weight": "bold",
            "text-transform": "uppercase",
            "margin": "0px 20px",
        },
        "nav-link-selected": {"background-color": "#7df4d3", "color": "#0c0c0c", "border-radius": "8px"},
    },
)

# ================== SERVICIOS ==================
SERVICIOS = [
    {"nombre": "Corte Clásico", "precio": "10 USD", "img": "assets/logo-1.jpg"},
    {"nombre": "Barba & Diseño", "precio": "8 USD", "img": "assets/logo-2.jpg"},
    {"nombre": "Corte + Barba", "precio": "15 USD", "img": "assets/colors.jpg"},
    {"nombre": "VIP: Corte + Barba + Cejas", "precio": "18 USD", "img": "assets/banner.jpg"},
]

# ================== PÁGINAS ==================

# ---- SERVICIOS ----
if selected == "Servicios":
    st.markdown("<h2 style='text-align:center;'>💈 Nuestros Servicios 💈</h2>", unsafe_allow_html=True)
    cols = st.columns(4)
    for col, servicio in zip(cols, SERVICIOS):
        with col:
            st.image(servicio["img"], use_container_width=True)
            st.markdown(f"<strong>{servicio['nombre']}</strong>", unsafe_allow_html=True)
            st.markdown(f"<span class='precio'>💲 {servicio['precio']}</span>", unsafe_allow_html=True)

# ---- BARBEROS ----
elif selected == "Barberos":
    st.markdown("<h2 style='text-align:center;'>👨‍🔧 Nuestro Equipo de Barberos</h2>", unsafe_allow_html=True)
    sede = st.selectbox("🏢 Selecciona una sede", list(SEDES.keys()))
    st.markdown(f"### 💈 Barberos de {sede}")

    barberos = SEDES[sede]["barberos"]
    cols = st.columns(len(barberos))
    for col, barbero in zip(cols, barberos):
        with col:
            st.image(barbero["img"], use_container_width=True)
            st.markdown(f"<p style='text-align:center; color:##7df4d3; font-weight:bold;'>{barbero['nombre']}</p>", unsafe_allow_html=True)

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
                calendar_ids = {k: v["calendar_id"] for k, v in SEDES.items()}
                gc = GoogleCalendar("credentials.json", calendar_ids)
                gc.create_event(sede, nombre, telefono, email, servicio, barbero, fecha, hora)
                st.success(f"✅ Cita reservada para {nombre} en la sede {sede} el {fecha} a las {hora}")
            else:
                st.warning("⚠️ Por favor, completa todos los campos obligatorios.")

# ---- UBICACIÓN ----
elif selected == "Ubicación":
    st.markdown("## 📍 Nuestras Sedes")
    st.markdown("""
    **📍 Matriz - Centro:** Av. Unidad Nacional entre Juan Montalvo y Carabobo  
    **📍 Sucursal Norte:** Av. Amazonas y Colón  
    **📍 Sucursal Sur:** Calle Loja y Ayacucho  
    **📍 Sucursal Este:** Av. 6 de Diciembre y Portugal  

    **📞 Teléfono:** 098 840 2541  
    **🕐 Horario:** Lunes a Sábado: 09:00 - 20:00 | Domingo: 10:00 - 16:00
    """)
