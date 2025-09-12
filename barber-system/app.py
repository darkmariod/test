import streamlit as st
from streamlit_option_menu import option_menu

# Variables
servicios = [
    "Perfil de cejas con guillet y gel de afeitar - 1.00 USD",
    "Afeitado o Perfilación de barba - 3.00 USD",
    "Corte Clásico con máquina - 5.00 USD",
    "Corte Clásico a tijera - 5.00 USD",
    "Freestyle (diseño personalizado) - 7.00 USD",
    "Semi Ondulado (ondas) - desde 20.00 USD",
    "VIP: Corte + Barba + Cejas + bebida de cortesía - 8.00 USD",
]

empleados = ["Josué", "Ariel"]

# Horarios en diccionario
horarios = {
    "Lunes": "09:00 - 21:00",
    "Martes": "09:00 - 21:00",
    "Miércoles": "09:00 - 21:00",
    "Jueves": "09:00 - 21:00",
    "Viernes": "09:00 - 21:00",
    "Sábado": "09:00 - 21:00",
    "Domingo": "09:00 - 21:00"
}

# Page config
st.set_page_config(page_title="App de citas", page_icon="✂️", layout="centered")
st.image("assets/banner.png")
st.title("Seven Barber Club")
st.text("Av. Unidad Nacional ente Juan Montalvo y Carabobo")

# Menú de navegación
selected = option_menu(
    menu_title=None,
    options=["Servicios", "Reseñas", "Portafolio", "Detalles"],
    icons=["scissors", "chat-dots", "file-text", "pin"],  # https://icons.getbootstrap.com/
    orientation="horizontal",
)

# ================== PORTAFOLIO ==================
if selected == "Portafolio":
    st.image("assets/corte-1.jpg", caption="Degradado básico")
    st.image("assets/corte-2.jpg", caption="Corte más barba")
    st.image("assets/corte-3.jpg", caption="Raya personalizada")

# ================== DETALLES ==================
if selected == "Detalles":
    st.image("assets/map.JPG")
    st.markdown("[📍 Pulsa aquí](www.google.com) para ver la dirección en Google Maps.")

    st.subheader("💈 Barberos")
    column1, column2 = st.columns(2)
    column1.image("assets/barber-1.png", caption="Josué")
    column2.image("assets/barber-2.png", caption="Ariel")

    # Mostrar horarios en tabla visual
    st.markdown("### 🕒 Horarios de Atención")
    c1, c2 = st.columns(2)
    for dia, hora in horarios.items():
        c1.markdown(f"**📅 {dia}**")
        c2.markdown(f"⏰ {hora}")

# ================== RESEÑAS ==================
if selected == "Reseñas":
    st.image("assets/opinion1.JPG")
    st.image("assets/opinion2.JPG")

# ================== SERVICIOS ==================
if selected == "Servicios":
    st.subheader("Reservar cita")
    a1, a2 = st.columns(2)

    nombre = a1.text_input("Tu nombre")
    email = a2.text_input("Tu email")
    fecha = a1.date_input("Fecha")
    hora = a2.selectbox("Horas disponibles", ["09:00", "10:00", "11:00", "12:00", "14:00","15:00","16:00", "17:00", "18:00", "19:00","20:00",])

    servicio = a1.selectbox("Servicio", servicios)
    empleado = a2.selectbox("Barberos", empleados)
    nota = a1.text_area("💬 Nota (opcional)")

    enviar = st.button("Reservar")

    if enviar:
        st.success(f"✅ Reserva confirmada para {nombre} el {fecha} a las {hora} con {empleado} ({servicio}).")
