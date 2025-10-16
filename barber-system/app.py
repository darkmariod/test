import streamlit as st
from datetime import datetime
from googleapiclient.errors import HttpError
from gc_service import GoogleCalendar  # tu archivo existente (no tocar)

# ================== CONFIG ==================
st.set_page_config(page_title="WabiSabi Barber", layout="wide")

# ================== SESSION STATE ==================
if "page" not in st.session_state:
    st.session_state.page = "servicios"
if "servicio_preseleccionado" not in st.session_state:
    st.session_state.servicio_preseleccionado = None
if "selected_sede" not in st.session_state:
    st.session_state.selected_sede = None
if "selected_barbero" not in st.session_state:
    st.session_state.selected_barbero = None

# ================== DATOS ==================
SERVICIOS = [
    {"nombre": "Corte Clásico", "descripcion": "Un estilo limpio y tradicional.", "precio": "6 USD", "tiempo": "35 min"},
    {"nombre": "Fade Moderno", "descripcion": "Difuminado moderno con estilo urbano.", "precio": "7 USD", "tiempo": "45 min"},
    {"nombre": "Afeitado Premium", "descripcion": "Afeitado con toalla caliente y productos premium.", "precio": "5 USD", "tiempo": "30 min"},
    {"nombre": "Corte + Barba", "descripcion": "Combina corte moderno y diseño de barba.", "precio": "10 USD", "tiempo": "1 hora"},
]

# Sedes y barberos (modifica los calendar_id por los reales)
SEDES = {
    "Matriz - Centro": {
        "direccion": "Av. Unidad Nacional entre Juan Montalvo y Carabobo",
        "horario": "Lun-Sáb: 09:00 - 20:00 | Dom: 10:00 - 16:00",
        "barberos": [
            {"nombre": "Israel", "calendar_id": "mariodanielq.p@gmail.com", "rating": 4.8},
            {"nombre": "Josué", "calendar_id": "guamanjosue380@gmail.com", "rating": 4.6},
            {"nombre": "Carlos", "calendar_id": "barbero_jose@gmail.com", "rating": 4.7},
        ],
    },
    "Sucursal Veloz": {
        "direccion": "Av. Amazonas y Colón",
        "horario": "Lun-Sáb: 09:00 - 20:00 | Dom: 10:00 - 16:00",
        "barberos": [
            {"nombre": "Marcos", "calendar_id": "barbero_jose_norte@gmail.com", "rating": 4.5},
            {"nombre": "Kevin", "calendar_id": "barbero_dani_norte@gmail.com", "rating": 4.4},
        ],
    },
    "Urban": {
        "direccion": "Calle Loja y Ayacucho",
        "horario": "Lun-Sáb: 09:00 - 20:00 | Dom: 10:00 - 16:00",
        "barberos": [
            {"nombre": "Anothony", "calendar_id": "barbero_jose_sur@gmail.com", "rating": 4.3},
            {"nombre": "Isra", "calendar_id": "barbero_isra_sur@gmail.com", "rating": 4.6},
        ],
    },
    "Barber Training": {
        "direccion": "Av. América y Mariana de Jesús",
        "horario": "Lun-Vie: 09:00 - 19:00 | Sáb: 09:00 - 14:00",
        "barberos": [
            {"nombre": "Jose", "calendar_id": "barbero_jose_training@gmail.com", "rating": 4.9},
            {"nombre": "Don Luis", "calendar_id": "barbero_isra_training@gmail.com", "rating": 4.7},
        ],
    },
}

# ================== CSS ==================
st.markdown(
    """
    <style>
    body { background-color: #f4f6f8; font-family: Inter, Arial, sans-serif; }
    .page-center { max-width: 1100px; margin: 20px auto; }
    .header { text-align:center; margin-bottom: 18px; }
    .servicio-card { background: #fff; border-radius: 12px; padding:18px; border:1px solid #e6e9ee; box-shadow: 0 6px 18px rgba(16,24,40,0.04); margin-bottom:12px; }
    .servicio-title { font-size:18px; font-weight:700; color:#0f172a; margin-bottom:6px; }
    .servicio-desc { color:#475569; margin-bottom:10px; }
    .servicio-meta { color:#0f172a; font-weight:600; }
    .agendar-blue { background:#2563eb; color:white; padding:8px 14px; border-radius:10px; border:none; font-weight:600; cursor:pointer;}
    .agendar-blue:hover { background:#1e40af; transform: translateY(-1px); }
    .center-cta { display:flex; justify-content:center; margin-top:20px; }
    .ver-sedes { background:#111827; color:white; padding:12px 26px; border-radius:10px; border:none; font-size:16px; font-weight:700; cursor:pointer; }
    .ver-sedes:hover { background:#2563eb; }
    .sede-card { background:#fff; padding:18px; border-radius:12px; border:1px solid #e6e9ee; margin-bottom:14px; }
    .barbero-row { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-top:1px dashed #eef2f7; }
    .barbero-name { font-weight:600; }
    .rating-pill { background:#f1f5f9; padding:6px 10px; border-radius:999px; color:#0f172a; font-weight:600; }
    .back-btn { background:#e5e7eb; color:#0f172a; padding:10px 18px; border-radius:10px; border:none; cursor:pointer; }
    .booking-card { background:#fff; border-radius:16px; padding:26px; max-width:720px; margin:0 auto; box-shadow: 0 8px 30px rgba(2,6,23,0.06); }
    .time-blocks { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
    .time-slot { background:#f8fafc; padding:8px 12px; border-radius:8px; border:1px solid #e6eef8; cursor:pointer; }
    .time-slot.selected { background:#2563eb; color:white; border-color:#1e40af; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ================== PAGES ==================

# ---------- SERVICIOS ----------
if st.session_state.page == "servicios":
    st.markdown('<div class="page-center">', unsafe_allow_html=True)
    st.markdown('<div class="header"><h1>💈 WabiSabi / Monkey Barber</h1><p style="color:#475569;">Selecciona un servicio para agendar</p></div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for i, s in enumerate(SERVICIOS):
        with cols[i % 2]:
            st.markdown(f'<div class="servicio-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="servicio-title">{s["nombre"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="servicio-desc">{s["descripcion"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="servicio-meta">⏱ {s["tiempo"]} — 💲 {s["precio"]}</div>', unsafe_allow_html=True)
            # Botón de agendar (azul)
            if st.button(f"Agendar {s['nombre']}", key=f"agendar_{i}"):
                st.session_state.servicio_preseleccionado = s["nombre"]
                # limpiar selecciones previas
                st.session_state.selected_sede = None
                st.session_state.selected_barbero = None
                st.session_state.page = "agendar"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # CTA centrada para ver sedes/barberos
    st.markdown('<div class="center-cta">', unsafe_allow_html=True)
    if st.button("🏢 Ver Barberos y Sedes", key="ver_sedes_btn"):
        st.session_state.page = "barberos"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- BARBEROS Y SEDES ----------
elif st.session_state.page == "barberos":
    st.markdown('<div class="page-center">', unsafe_allow_html=True)
    st.markdown('<div class="header"><h1>🏢 Barberos y Sedes</h1><p style="color:#475569;">Elige una sede y selecciona un barbero</p></div>', unsafe_allow_html=True)

    # Mostrar cada sede con sus barberos y rating
    for sede, data in SEDES.items():
        st.markdown(f'<div class="sede-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex; justify-content:space-between; align-items:center;"><div><strong>{sede}</strong><div style="color:#6b7280; font-size:13px;">{data.get("direccion","")}</div></div><div style="color:#6b7280;">{data.get("horario","")}</div></div>', unsafe_allow_html=True)
        # list barberos
        for b in data["barberos"]:
            # fila del barbero con botón elegir
            cols = st.columns([6, 2, 2])
            with cols[0]:
                st.markdown(f'<div style="padding-top:6px;"><span class="barbero-name">{b["nombre"]}</span><div style="color:#64748b; font-size:13px;">Especialista</div></div>', unsafe_allow_html=True)
            with cols[1]:
                st.markdown(f'<div style="padding-top:6px;"><span class="rating-pill">★ {b.get("rating",4.5)}</span></div>', unsafe_allow_html=True)
            with cols[2]:
                if st.button(f"Elegir {b['nombre']} - {sede}", key=f"elegir_{sede}_{b['nombre']}"):
                    # preseleccionar y abrir formulario
                    st.session_state.selected_sede = sede
                    st.session_state.selected_barbero = b["nombre"]
                    st.session_state.servicio_preseleccionado = None
                    st.session_state.page = "agendar"
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Volver a servicios
    if st.button("⬅️ Volver a Servicios", key="back_from_barberos"):
        st.session_state.page = "servicios"
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- AGENDAR ----------
elif st.session_state.page == "agendar":
    st.markdown('<div class="page-center">', unsafe_allow_html=True)
    st.markdown('<div class="header"><h1>📅 Reservar cita</h1><p style="color:#475569;">Selecciona fecha, hora y confirma</p></div>', unsafe_allow_html=True)

    # Tarjeta tipo Weibook
    st.markdown('<div class="booking-card">', unsafe_allow_html=True)

    with st.form("form_reserva"):
        # Prellenar si venimos de "barberos"
        if st.session_state.selected_sede:
            sede_default = st.session_state.selected_sede
        else:
            sede_default = list(SEDES.keys())[0]

        if st.session_state.selected_barbero:
            barbero_default = st.session_state.selected_barbero
        else:
            # primer barbero de la sede por defecto
            barbero_default = SEDES[sede_default]["barberos"][0]["nombre"]

        nombre = st.text_input("👤 Nombre completo")
        email = st.text_input("📧 Correo electrónico")
        telefono = st.text_input("📞 Número de celular")

        sede = st.selectbox("🏢 Selecciona una sede", list(SEDES.keys()), index=list(SEDES.keys()).index(sede_default))
        # cuando cambia la sede, actualizamos la lista de barberos con JS no disponible; hacemos simple select next
        barbero = st.selectbox("💇 Selecciona un barbero", [b["nombre"] for b in SEDES[sede]["barberos"]], index=0)

        servicio_default = st.session_state.servicio_preseleccionado or SERVICIOS[0]["nombre"]
        servicio = st.selectbox("💈 Servicio", [s["nombre"] for s in SERVICIOS], index=[s["nombre"] for s in SERVICIOS].index(servicio_default))

        # Fecha
        col1, col2 = st.columns([1, 1])
        with col1:
            fecha = st.date_input("📆 Fecha", datetime.today())
        with col2:
            hora = st.time_input("⏰ Hora", datetime.now().time())

        # botón enviar
        enviar = st.form_submit_button("✅ Confirmar Reserva")

        if enviar:
            if not nombre or not email or not telefono:
                st.warning("⚠️ Completa todos los campos.")
            else:
                # obtener calendar_id del barbero elegido
                calendar_id = None
                for b in SEDES[sede]["barberos"]:
                    if b["nombre"] == barbero:
                        calendar_id = b["calendar_id"]
                        break

                if not calendar_id:
                    st.error("❌ No se encontró el calendario del barbero seleccionado.")
                else:
                    gc = GoogleCalendar("credentials.json")
                    try:
                        # is_available ya valida rango 10:00 - 19:00 en tu gc_service si lo dejaste así
                        disponible = gc.is_available(calendar_id, fecha, hora)
                        if not disponible:
                            st.error("🚫 El barbero no está disponible en ese horario.")
                        else:
                            gc.create_event(
                                calendar_id,
                                nombre,
                                telefono,
                                email,
                                servicio,
                                [b["calendar_id"] for b in SEDES[sede]["barberos"]],
                                fecha,
                                hora
                            )
                            st.success(f"✅ Cita confirmada con {barbero} en {sede} para {fecha} a las {hora}.")
                            # limpiar selección previa y volver a servicios
                            st.session_state.servicio_preseleccionado = None
                            st.session_state.selected_sede = None
                            st.session_state.selected_barbero = None
                            st.session_state.page = "servicios"
                            st.rerun()
                    except HttpError:
                        st.error("❌ Error con Google Calendar. Verifica credenciales y permisos.")
                    except ValueError as ve:
                        st.error(f"⚠️ {ve}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    st.markdown('</div>', unsafe_allow_html=True)

    # Botón Volver a Servicios funcional
    if st.button("⬅️ Volver a Servicios", key="back_from_agendar"):
        st.session_state.page = "servicios"
        st.session_state.servicio_preseleccionado = None
        st.session_state.selected_sede = None
        st.session_state.selected_barbero = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
