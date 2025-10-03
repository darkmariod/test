import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, date, time, timedelta
from gc_service import GoogleCalendar

# ================= CONFIG STREAMLIT =================
st.set_page_config(page_title="Seven Club Barbería", page_icon="💈", layout="wide")

# ================= ESTILOS =================
st.markdown(
    """
    <style>
    .title-center {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #333333;
    }
    .subtitle-center {
        text-align: center;
        font-size: 18px;
        color: gray;
    }
    .card {
        background: #ffffff;
        border-radius: 20px;
        padding: 15px;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .card:hover {
        transform: scale(1.03);
        box-shadow: 0px 6px 16px rgba(0,0,0,0.2);
    }
    .service-title {
        font-size: 20px;
        font-weight: bold;
        margin-top: 10px;
    }
    .service-price {
        font-size: 16px;
        color: #666666;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================= LOGO + TÍTULO =================
st.image("assets/logo.png", width=120)
st.markdown("<div class='title-center'>Seven Club Barbería 💈</div>", unsafe_allow_html=True)
st.markdown("<p class='subtitle-center'>📍 Av. Unidad Nacional entre Juan Montalvo y Carabobo</p>", unsafe_allow_html=True)

# ================= CALENDARS POR SEDE =================
SEDES = {
    "Matriz": "calendar_id_matriz@group.calendar.google.com",
    "Sucursal Norte": "calendar_id_norte@group.calendar.google.com",
    "Sucursal Sur": "calendar_id_sur@group.calendar.google.com",
}

# ================= BARBEROS =================
BARBEROS = {
    "Matriz": [
        {"nombre": "Josué", "img": "assets/barber-1.png"},
        {"nombre": "Ariel", "img": "assets/barber-2.png"},
    ],
    "Sucursal Norte": [
        {"nombre": "Kevin", "img": "assets/barber-3.png"},
        {"nombre": "Luis", "img": "assets/barber-4.png"},
    ],
    "Sucursal Sur": [
        {"nombre": "Andrés", "img": "assets/barber-5.png"},
    ],
}

# ================= MENÚ =================
selected = option_menu(
    menu_title=None,
    options=["Servicios", "Barberos", "Portafolio", "Detalles"],
    icons=["scissors", "people", "images", "geo-alt"],
    orientation="horizontal",
)

# ================= SERVICIOS =================
if selected == "Servicios":
    st.subheader("💇 Nuestros Servicios")

    services = [
        {"nombre": "Corte Clásico", "precio": "10 USD", "img": "assets/corte.png"},
        {"nombre": "Barba & Diseño", "precio": "8 USD", "img": "assets/barba.png"},
        {"nombre": "Corte + Barba", "precio": "15 USD", "img": "assets/cortebarba.png"},
        {"nombre": "VIP: Corte + Barba + Cejas + bebida 🍹", "precio": "20 USD", "img": "assets/vip.png"},
    ]

    cols = st.columns(4)
    for col, service in zip(cols, services):
        with col:
            st.markdown(f"""
                <div class="card">
                    <img src="{service['img']}" style="width:100%; border-radius:15px;">
                    <div class="service-title">{service['nombre']}</div>
                    <div class="service-price">💲 {service['precio']}</div>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("📅 Reserva tu Cita")

    sede = st.selectbox("📍 Selecciona la sede", list(SEDES.keys()))

    with st.form("form_reserva"):
        nombre = st.text_input("👤 Nombre completo")
        email = st.text_input("✉️ Correo electrónico (obligatorio)")
        servicio = st.selectbox("💈 Selecciona un servicio", [s["nombre"] for s in services])
        barbero = st.selectbox("💈 Selecciona tu barbero", [b["nombre"] for b in BARBEROS[sede]])
        fecha = st.date_input("📆 Fecha", min_value=date.today())
        hora = st.time_input("⏰ Hora", value=time(10, 0))
        nota = st.text_area("📝 Nota (opcional)")

        submit = st.form_submit_button("✅ Confirmar Reserva")

        if submit:
            calendar = GoogleCalendar("credentials.json", SEDES[sede])
            if not email or not nombre:
                st.error("⚠️ Completa todos los campos obligatorios.")
            else:
                start_time = datetime.combine(fecha, hora)
                end_time = start_time + timedelta(minutes=30)

                if calendar.is_time_available(start_time, end_time):
                    calendar.add_event(
                        start_time,
                        end_time,
                        summary=f"Cita de {nombre} con {barbero}",
                        description=f"Servicio: {servicio}\nSede: {sede}\nBarbero: {barbero}\nNota: {nota}",
                        email=email,
                    )
                    st.success(f"✅ Reserva confirmada con {barbero} en {sede} el {fecha} a las {hora.strftime('%H:%M')}.")
                else:
                    st.error("❌ Ya existe una cita en ese horario. Por favor selecciona otra hora.")

# ================= BARBEROS =================
if selected == "Barberos":
    st.subheader("👨‍🔧 Conoce a nuestros Barberos")
    sede_actual = st.selectbox("📍 Ver barberos por sede", list(BARBEROS.keys()))
    cols = st.columns(3)
    for i, barbero in enumerate(BARBEROS[sede_actual]):
        with cols[i % 3]:
            # <-- reemplazado use_column_width por use_container_width
            st.image(barbero["img"], caption=barbero["nombre"], use_container_width=True)

# ================= PORTAFOLIO =================
if selected == "Portafolio":
    st.subheader("📸 Algunos de nuestros trabajos")
    st.image("assets/corte-1.jpg", caption="Degradado básico", use_container_width=True)
    st.image("assets/corte-2.jpg", caption="Corte + Barba", use_container_width=True)
    st.image("assets/corte-3.jpg", caption="Raya personalizada", use_container_width=True)

# ================= DETALLES =================
if selected == "Detalles":
    st.subheader("📍 Ubicación")
    st.image("assets/map.JPG", use_container_width=True)
    st.markdown("[Abrir en Google Maps](https://www.google.com/maps)")

    st.subheader("📞 Contacto")
    st.markdown("📱 **098 840 2541**")
    st.markdown("📷 [Instagram](https://www.instagram.com)")
