import streamlit as st
from streamlit_option_menu import option_menu
from datetime import datetime, timedelta
from gc_service import GoogleService
import os

# =====================================
# CONFIGURACIÓN GOOGLE CALENDAR
# =====================================
CREDENTIALS = "credentials.json"
CALENDAR_ID = "mariodanielq.p@gmail.com"
gc = GoogleService(CREDENTIALS)

# =====================================
# CARGAR ESTILOS
# =====================================
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("css/style.css")

# =====================================
# CONFIG STREAMLIT
# =====================================
st.set_page_config(page_title="Seven Barber Club", page_icon="✂️", layout="centered")

st.image("assets/banner.png")
st.title("Seven Barber Club")
st.text("📍 Av. Unidad Nacional entre Juan Montalvo y Carabobo")

# =====================================
# MENÚ
# =====================================
selected = option_menu(
    menu_title=None,
    options=["Reservar", "Portafolio", "Cortes de Aprendiz", "Detalles", "Reseñas"],
    icons=["calendar-check", "scissors", "person-workspace", "pin", "chat-dots"],
    orientation="horizontal",
)

# =====================================
# SECCIÓN: RESERVAR
# =====================================
if selected == "Reservar":
    st.subheader("📅 Reserva tu cita")

    servicios = [
        "",
        "Perfil de cejas con guillet y gel de afeitar - 1.00 USD",
        "Afeitado o Perfilación de barba - 3.00 USD",
        "Corte Clásico con máquina - 5.00 USD",
        "Corte Clásico a tijera - 5.00 USD",
        "Freestyle (diseño personalizado) - 7.00 USD",
        "Semi Ondulado (ondas) - desde 20.00 USD",
        "VIP: Corte + Barba + Cejas + bebida de cortesía - 8.00 USD"
    ]

    empleados = ["Josué", "Ariel", "Mario (Aprendiz)"]

    col1, col2 = st.columns(2)
    nombre = col1.text_input("Tu nombre *")
    whatsapp = col2.text_input("Tu WhatsApp * (Ej: 0987654321)")
    email = col1.text_input("Tu email (opcional)")
    fecha = col2.date_input("Fecha *")
    servicio = col1.selectbox("Servicio *", servicios)
    barbero = col2.selectbox("Barbero *", empleados)
    nota = col1.text_area("💬 Nota (opcional)")
    hora = col2.selectbox("Hora disponible *", [
        "09:00", "10:00", "11:00", "12:00",
        "14:00", "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00"
    ])

    if st.button("Reservar"):
        if not nombre or not whatsapp or not fecha or not servicio or not barbero or not hora:
            st.warning("⚠️ Por favor completa todos los campos obligatorios marcados con * antes de continuar.")
        else:
            try:
                start = datetime.combine(fecha, datetime.strptime(hora, "%H:%M").time())
                end = start + timedelta(hours=1)
                gc.crear_evento(
                    calendar_id=CALENDAR_ID,
                    resumen=f"Reserva: {servicio} con {barbero} - {nombre}",
                    descripcion=f"Cliente: {nombre}\nWhatsApp: {whatsapp}\nServicio: {servicio}\nBarbero: {barbero}\nNota: {nota}",
                    inicio=start,
                    fin=end,
                    timezone="America/Guayaquil"
                )
                st.success(f"✅ Reserva confirmada correctamente para {nombre} el {fecha} a las {hora} con {barbero}.")
                st.balloons()

                msg = f"Hola {barbero}, tienes una nueva reserva:\nCliente: {nombre}\nServicio: {servicio}\nHora: {hora}\nFecha: {fecha}\nWhatsApp: {whatsapp}"
                url = f"https://wa.me/593{whatsapp}?text={msg.replace(' ', '%20')}"
                st.markdown(f"[📲 Enviar mensaje por WhatsApp]({url})", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Ocurrió un error al crear la reserva: {e}")

# =====================================
# SECCIÓN: PORTAFOLIO
# =====================================
if selected == "Portafolio":
    # ===== Josué =====
    st.markdown("""
    <div class="perfil-barbero">
        <img src="assets/josue-perfil.jpg" alt="Josué">
        <h3>👑 Josué</h3>
        <p>Maestro barbero de Seven Barber Club.  
        Estilo, precisión y elegancia en cada corte.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("💇‍♂️ Cortes de Josué")
    cols = st.columns(3)
    cortes_josue = [
        "assets/corte-1.jpg", "assets/corte-2.jpg", "assets/corte-3.jpg",
        "assets/barber-1-test.png", "assets/barber-2-test.png", "assets/corte-1.jpg"
    ]
    for i, img in enumerate(cortes_josue):
        with cols[i % 3]:
            st.image(img, use_container_width=True)

    st.markdown("---")

    # ===== Ariel =====
    st.markdown("""
    <div class="perfil-barbero">
        <img src="assets/ariel-perfil.jpg" alt="Ariel">
        <h3>💈 Ariel</h3>
        <p>Barbero profesional, experto en cortes con carácter.  
        Técnica limpia y diseño moderno con personalidad.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("💈 Cortes de Ariel")
    cols = st.columns(3)
    cortes_ariel = [
        "assets/corte-1.jpg", "assets/corte-2.jpg", "assets/corte-3.jpg",
        "assets/barber-1-test.png", "assets/barber-2-test.png", "assets/corte-3.jpg"
    ]
    for i, img in enumerate(cortes_ariel):
        with cols[i % 3]:
            st.image(img, use_container_width=True)

# =====================================
# SECCIÓN: CORTES DE APRENDIZ
# =====================================
if selected == "Cortes de Aprendiz":
    st.subheader("💈 Cortes de Aprendiz — Mario (Seven Barber Club)")
    st.markdown("""
    ✂️ **Cortes de práctica profesional con dedicación y estilo.**  
    💸 *Precio especial: 2.00 USD — solo bajo reserva.*  
    ⏰ *Horario disponible: de 16:00 a 20:00*
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.image("assets/corte-aprendiz-1.png", caption="Mid Fade — Corte moderno de práctica", use_container_width=True)
    with col2:
        st.image("assets/corte-aprendiz-2.png", caption="Clásico — Corte tradicional", use_container_width=True)

# =====================================
# SECCIÓN: DETALLES
# =====================================
if selected == "Detalles":
    st.subheader("📍 Ubicación y Horarios")
    st.image("assets/map.jpg", caption="Mapa de Seven Barber Club", use_container_width=True)
    st.markdown("""
    📌 **Dirección:**  
    Av. Unidad Nacional entre Juan Montalvo y Carabobo — Riobamba, Ecuador.  
    """, unsafe_allow_html=True)
    st.markdown("### 🕒 Horarios de Atención")
    horarios = {
        "Lunes a Viernes": "09:00 - 21:00",
        "Sábado": "09:00 - 21:00",
        "Domingo": "09:00 - 21:00"
    }
    for dia, hora in horarios.items():
        st.markdown(f"**{dia}:** {hora}")
    st.markdown("""
    ### 📞 Contacto
    📲 WhatsApp: **098 840 2541**  
    📷 Instagram: [@sevenbarberclub](https://www.instagram.com)  
    💈 *Donde el estilo se crea con precisión.*
    """, unsafe_allow_html=True)
    # =====================================

# =====================================
# SECCIÓN: RESEÑAS (imágenes reales)
# =====================================
if selected == "Reseñas":
    st.subheader("💬 Opiniones de nuestros clientes")
    st.markdown("""
    ✂️ **Mira algunas experiencias reales de nuestros clientes en Seven Barber Club.**
    """, unsafe_allow_html=True)

    # Validar imágenes antes de mostrarlas
    rutas = ["assets/review-1.png", "assets/review-2.png", "assets/qr.png"]
    for ruta in rutas:
        if not os.path.exists(ruta):
            st.warning(f"⚠️ No se encontró el archivo: {ruta}")

    # --- Fila 1 ---
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.image("assets/review-1.png", caption="⭐ Opinión real — Arturo Llerena", use_container_width=True)
    with col2:
        st.image("assets/review-2.png", caption="⭐ Opinión real — Jonas Pinduisaca", use_container_width=True)

    # --- Fila 2 ---
    col3, col4 = st.columns(2, gap="large")
    with col3:
        st.image("assets/review-1.png", caption="⭐ Opinión real — Cliente Seven Barber Club", use_container_width=True)
    with col4:
        st.image("assets/qr.png", caption="📱 Escanea y deja tu reseña en Google", use_container_width=True)

