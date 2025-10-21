import streamlit as st
from datetime import datetime, time
from streamlit_option_menu import option_menu
import os

# ======================================================
# SIMULACIÓN DE CALENDARIO (sin conexión a Google)
# ======================================================
class GoogleCalendar:
    def __init__(self, creds_file=None):
        self.eventos = {}

    def get_available_hours(self, calendar_id, fecha):
        ocupadas = [e["hora"].hour for e in self.eventos.get(calendar_id, []) if e["fecha"] == fecha]
        return [f"{h}:00" for h in range(9, 20) if h not in ocupadas]

    def create_event(self, calendar_id, nombre, telefono, email, servicio, barberos, fecha, hora, duracion_min=60):
        self.eventos.setdefault(calendar_id, []).append({"fecha": fecha, "hora": hora})
        print(f"✅ [SIMULADO] Cita creada para {nombre} en {calendar_id} a las {hora}")

# ==========================================
# CONFIGURACIÓN
# ==========================================
st.set_page_config(page_title="WabiSabi Barber", layout="wide")
calendar = GoogleCalendar()

# ==========================================
# DATOS
# ==========================================
SERVICIOS = [
    {"nombre": "Corte Clásico", "descripcion": "Estilo limpio y tradicional", "precio": "6 USD", "tiempo": "35 min"},
    {"nombre": "Fade Moderno", "descripcion": "Difuminado moderno", "precio": "7 USD", "tiempo": "45 min"},
    {"nombre": "Afeitado Premium", "descripcion": "Con toalla caliente y productos premium", "precio": "5 USD", "tiempo": "30 min"},
    {"nombre": "Corte + Barba", "descripcion": "Combina corte y barba", "precio": "10 USD", "tiempo": "1 hora"},
]

SEDE_PRINCIPAL = {
    "nombre": "Matriz - Centro",
    "direccion": "Av. Unidad Nacional y Carabobo, Riobamba",
    "horario": "Lun-Sáb: 09:00-20:00"
}

SEDES = {
    "Matriz - Centro": {
        "direccion": "Av. Unidad Nacional y Carabobo",
        "horario": "Lun-Sáb: 09:00-20:00",
        "barberos": [
            {"nombre": "Israel", "rating": 4.8, "foto": "assets/barber-isra.jpg"},
            {"nombre": "Josué", "rating": 4.6, "foto": "assets/Josue_SedeMatriz.jpg"},
        ],
    },
    "Urban": {
        "direccion": "Calle Loja y Ayacucho",
        "horario": "Lun-Sáb: 09:00-20:00",
        "barberos": [
            {"nombre": "Anthony", "rating": 4.3, "foto": "assets/Anthony_SedeUrban.jpg"},
            {"nombre": "Isra", "rating": 4.6, "foto": "assets/barber-isra.jpg"},
        ],
    },
    "Barber Training": {
        "direccion": "Av. América y Mariana de Jesús",
        "horario": "Lun-Vie: 09:00-19:00 | Sáb: 09:00-14:00",
        "barberos": [
            {"nombre": "Jose", "rating": 4.9, "foto": "assets/barber-jose.jpg"},
            {"nombre": "Don Luis", "rating": 4.7, "foto": "assets/barber-don-luis.jpg"},
        ],
    },
    "Veloz": {
        "direccion": "Av. Veloz y 9 de Octubre",
        "horario": "Lun-Sáb: 09:00-20:00",
        "barberos": [
            {"nombre": "Carlos", "rating": 4.5, "foto": "assets/Marcos_SedeVeloz.jpg"},
            {"nombre": "Pablo", "rating": 4.7, "foto": "assets/Fabian_SedeVeloz.jpg"},
        ],
    },
}

# ==========================================
# ESTILOS
# ==========================================
st.markdown("""
<style>
body {background-color:#f4f6f8;font-family:Inter,Arial,sans-serif;}
button[kind="secondary"] {
    background-color:#2563eb !important;
    color:white !important;
    border:none !important;
    border-radius:10px !important;
    padding:10px 20px !important;
    font-weight:600 !important;
}
button[kind="secondary"]:hover {
    background-color:#1d4ed8 !important;
}
.booking-card{
    background:#fff;border-radius:16px;padding:26px;margin:10px;
    box-shadow:0 8px 30px rgba(2,6,23,0.06);
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# ESTADO
# ==========================================
if "page" not in st.session_state:
    st.session_state.page = "sedes"

# ==========================================
# CABECERA CON IMAGEN FUNCIONAL (st.image)
# ==========================================
col_img, col_info = st.columns([1, 3])
with col_img:
    st.image("assets/logo-1.jpg", use_container_width=True)
with col_info:
    st.markdown("""
        <div style="text-align:center;">
            <h1 style="font-size:28px; font-weight:700; margin-bottom:5px;">💈 WabiSabi Barber</h1>
            <p style="font-size:16px; color:#555;">
                En Barbería Wabi Sabi La Veloz, la dedicación a la perfección en cada corte de cabello es evidente<br>
                Un equipo de expertos se asegura de que cada cliente reciba una atención personalizada y un estilo que resalte su individualidad. 
                La experiencia se complementa con un ambiente acogedor, ideal para relajarse mientras se transforma tu look.
                🕒 Lun-Sáb: 09:00–20:00
            </p>
        </div>
    """, unsafe_allow_html=True)


# ==========================================
# MENÚ SUPERIOR
# ==========================================
selected = option_menu(
    menu_title=None,
    options=["Servicios", "Barberos", "Agendar", "Sedes"],
    icons=["scissors", "people-fill", "calendar-check", "geo-alt-fill"],
    menu_icon="cast",
    default_index=["servicios", "barberos", "agendar", "sedes"].index(st.session_state.page),
    orientation="horizontal",
    styles={
        "container": {"padding": "5px!important", "background-color": "#ffffff"},
        "icon": {"color": "#2563eb", "font-size": "20px"},
        "nav-link": {"font-size": "16px", "font-weight": "600", "color": "#000"},
        "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
    },
)
st.session_state.page = selected.lower()

# ==========================================
# PÁGINAS
# ==========================================
if st.session_state.page == "servicios":
    st.title("💈 Servicios Disponibles")
    cols = st.columns(2)
    for i, s in enumerate(SERVICIOS):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="booking-card">
                <h3>{s["nombre"]}</h3>
                <p>{s["descripcion"]}</p>
                <p>⏱ {s["tiempo"]} — 💲 {s["precio"]}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Agendar {s['nombre']}", key=f"btn_{i}", type="secondary", use_container_width=True):
                st.session_state.servicio_preseleccionado = s["nombre"]
                st.session_state.page = "agendar"
                st.rerun()

elif st.session_state.page == "barberos":
    st.title("🏢 Barberos y Sedes")
    for sede, data in SEDES.items():
        st.subheader(sede)
        st.caption(f"📍 {data['direccion']} | 🕓 {data['horario']}")
        for b in data["barberos"]:
            col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
            with col1:
                st.image(b["foto"], width=80)
            with col2:
                st.markdown(f"**{b['nombre']}**")
            with col3:
                st.markdown(f"⭐ {b['rating']}")
            with col4:
                if st.button("💈 Agendar", key=f"agendar_{sede}_{b['nombre']}", type="secondary"):
                    st.session_state.selected_sede = sede
                    st.session_state.selected_barbero = b["nombre"]
                    st.session_state.page = "agendar"
                    st.rerun()
        st.divider()

elif st.session_state.page == "agendar":
    st.title("📅 Agendar Cita")
    sede_default = st.session_state.get("selected_sede", list(SEDES.keys())[0])
    sede = st.selectbox("🏢 Sede", list(SEDES.keys()), index=list(SEDES.keys()).index(sede_default))
    barberos_lista = [b["nombre"] for b in SEDES[sede]["barberos"]]
    barbero_index = barberos_lista.index(st.session_state.get("selected_barbero", barberos_lista[0]))
    barbero = st.selectbox("💇 Barbero", barberos_lista, index=barbero_index)
    servicio = st.selectbox("💈 Servicio", [s["nombre"] for s in SERVICIOS],
                            index=next((i for i, s in enumerate(SERVICIOS)
                                        if s["nombre"] == st.session_state.get("servicio_preseleccionado")), 0))

    with st.form("form_reserva"):
        nombre = st.text_input("👤 Nombre completo")
        email = st.text_input("📧 Correo electrónico")
        telefono = st.text_input("📞 Celular")
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("📆 Fecha", datetime.today())
        with col2:
            horas_libres = calendar.get_available_hours(barbero, fecha)
            if horas_libres:
                hora = st.selectbox("⏰ Hora disponible", horas_libres)
            else:
                st.warning("⚠️ No hay horarios disponibles para este día.")
                hora = None

        confirmar = st.form_submit_button("✅ Confirmar Reserva", use_container_width=True)
        if confirmar:
            if not nombre or not email or not telefono:
                st.warning("⚠️ Completa todos los campos.")
            elif not hora:
                st.error("⏰ No hay hora seleccionada.")
            else:
                calendar.create_event(barbero, nombre, telefono, email, servicio, [barbero], fecha, time(int(hora.split(':')[0]), 0))
                st.success(f"✅ Cita confirmada con {barbero} en {sede} para las {hora}.")
                for key in ["servicio_preseleccionado", "selected_barbero", "selected_sede"]:
                    st.session_state.pop(key, None)

    if st.button("⬅️ Volver a Servicios", type="secondary", use_container_width=True):
        st.session_state.page = "servicios"
        st.rerun()

elif st.session_state.page == "sedes":
    st.title("📍 Nuestras Sedes")
    for sede, data in SEDES.items():
        st.subheader(sede)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(data["barberos"][0]["foto"], width=180)
        with col2:
            st.markdown(f"📍 **Dirección:** {data['direccion']}")
            st.markdown(f"🕒 **Horario:** {data['horario']}")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("🗺️ Ver en Google Maps", key=f"map_{sede}", type="secondary"):
                    st.markdown(f"[Abrir en Google Maps](https://www.google.com/maps/search/{data['direccion'].replace(' ', '+')})")
            with col_btn2:
                if st.button("💈 Agendar aquí", key=f"agendar_sede_{sede}", type="secondary"):
                    st.session_state.selected_sede = sede
                    st.session_state.page = "agendar"
                    st.rerun()
        st.divider()
