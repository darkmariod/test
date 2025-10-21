import streamlit as st
from datetime import datetime, time
from googleapiclient.errors import HttpError
from streamlit_option_menu import option_menu
from gc_service import GoogleCalendar

# ========================
# CONFIGURACIÓN GENERAL
# ========================
st.set_page_config(page_title="WabiSabi Barber", layout="wide")

# Usa tu credentials.json ya configurado
calendar = GoogleCalendar("credentials.json")

# ========================
# DATOS
# ========================
SERVICIOS = [
    {"nombre": "Corte Clásico", "descripcion": "Estilo limpio y tradicional", "precio": "6 USD", "tiempo": "35 min"},
    {"nombre": "Fade Moderno", "descripcion": "Difuminado moderno", "precio": "7 USD", "tiempo": "45 min"},
    {"nombre": "Afeitado Premium", "descripcion": "Con toalla caliente y productos premium", "precio": "5 USD", "tiempo": "30 min"},
    {"nombre": "Corte + Barba", "descripcion": "Combina corte y barba", "precio": "10 USD", "tiempo": "1 hora"},
]

SEDES = {
    "Matriz - Centro": {
        "direccion": "Av. Unidad Nacional y Carabobo",
        "horario": "Lun-Sáb: 09:30-19:00",
        "barberos": [
            {"nombre": "Israel", "rating": 4.8, "foto": "assets/barber-isra.jpg"},
            {"nombre": "Josué", "rating": 4.6, "foto": "assets/Josue_SedeMatriz.jpg"},
        ],
    },
    "Urban": {
        "direccion": "Calle Loja y Ayacucho",
        "horario": "Lun-Sáb: 09:30-19:00",
        "barberos": [
            {"nombre": "Anthony", "rating": 4.3, "foto": "assets/Anthony_SedeUrban.jpg"},
        ],
    },
    "Barber Training": {
        "direccion": "Av. América y Mariana de Jesús",
        "horario": "Lun-Vie: 09:30-19:00 | Sáb: 09:30-14:00",
        "barberos": [
            {"nombre": "José", "rating": 4.9, "foto": "assets/barber-jose.jpg"},
        ],
    },
    "Veloz": {
        "direccion": "Av. Veloz y 9 de Octubre",
        "horario": "Lun-Sáb: 09:30-19:00",
        "barberos": [
            {"nombre": "Carlos", "rating": 4.5, "foto": "assets/Marcos_SedeVeloz.jpg"},
        ],
    },
    "Norte": {
        "direccion": "Av. Los Shyris y Eloy Alfaro",
        "horario": "Lun-Sáb: 09:30-19:00",
        "barberos": [
            {"nombre": "Pablo", "rating": 4.7, "foto": "assets/Fabian_SedeVeloz.jpg"},
        ],
    },
}

# ========================
# ESTILOS
# ========================
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
button[kind="secondary"]:hover {background-color:#1d4ed8 !important;}
.booking-card{
    background:#fff;border-radius:16px;padding:26px;margin:10px;
    box-shadow:0 8px 30px rgba(2,6,23,0.06);
}
</style>
""", unsafe_allow_html=True)

# ========================
# ESTADO INICIAL
# ========================
if "page" not in st.session_state:
    st.session_state.page = "sedes"

# ========================
# MENÚ SUPERIOR
# ========================
selected = option_menu(
    menu_title=None,
    options=["Sedes", "Servicios", "Barberos", "Agendar"],
    icons=["geo-alt-fill", "scissors", "people-fill", "calendar-check"],
    menu_icon="cast",
    default_index=["sedes", "servicios", "barberos", "agendar"].index(st.session_state.page),
    orientation="horizontal",
    styles={
        "container": {"padding": "5px!important", "background-color": "#ffffff"},
        "icon": {"color": "#2563eb", "font-size": "20px"},
        "nav-link": {"font-size": "16px", "font-weight": "600", "color": "#000"},
        "nav-link-selected": {"background-color": "#2563eb", "color": "white"},
    },
)
st.session_state.page = selected.lower()

# ========================
# SECCIONES
# ========================

if st.session_state.page == "sedes":
    st.title("📍 Nuestras Sedes")
    for sede, data in SEDES.items():
        st.subheader(sede)
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(data["barberos"][0]["foto"], width=160)
        with col2:
            st.markdown(f"📍 **Dirección:** {data['direccion']}")
            st.markdown(f"🕒 **Horario:** {data['horario']}")
            if st.button(f"💈 Agendar en {sede}", key=f"agendar_{sede}", type="secondary"):
                st.session_state.selected_sede = sede
                st.session_state.page = "agendar"
                st.rerun()
        st.divider()

elif st.session_state.page == "servicios":
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
    barbero = st.selectbox("💇 Barbero", barberos_lista)

    servicio = st.selectbox("💈 Servicio", [s["nombre"] for s in SERVICIOS])

    with st.form("form_reserva"):
        nombre = st.text_input("👤 Nombre completo")
        email = st.text_input("📧 Correo electrónico")
        telefono = st.text_input("📞 Celular")

        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("📆 Fecha", datetime.today())
        with col2:
            # ✅ ID del calendario real (no el correo del service account)
            correo_barbero = "mariodanielq.p@gmail.com"
            horas_libres = []
            if correo_barbero:
                try:
                    horas_libres = calendar.get_available_hours(correo_barbero, fecha)
                except Exception as e:
                    st.error(f"⚠️ Error al obtener horarios: {e}")

            if horas_libres:
                hora = st.selectbox("⏰ Hora disponible", horas_libres)
            else:
                st.warning("⚠️ No hay horarios disponibles para este día o barbero.")
                hora = None

        confirmar = st.form_submit_button("✅ Confirmar Reserva", use_container_width=True)
        if confirmar:
            if not nombre or not email or not telefono:
                st.warning("⚠️ Completa todos los campos.")
            elif not hora:
                st.error("⏰ No hay hora seleccionada.")
            else:
                try:
                    calendar.create_event(
                        calendar_id=correo_barbero,
                        nombre=nombre,
                        telefono=telefono,
                        email=email,
                        servicio=servicio,
                        fecha=fecha,
                        hora=datetime.strptime(hora, "%H:%M").time(),
                        duracion_min=60
                    )
                    st.success(f"✅ Cita confirmada con {barbero} en {sede} para las {hora}.")
                except HttpError as e:
                    st.error(f"Error al crear el evento: {e}")
                except Exception as e:
                    st.error(f"Ocurrió un error: {e}")

    if st.button("⬅️ Volver a Sedes", type="secondary", use_container_width=True):
        st.session_state.page = "sedes"
        st.rerun()
