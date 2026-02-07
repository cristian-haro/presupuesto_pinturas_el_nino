import streamlit as st
import os
import json
import sys
from utils import get_app_path
from quote_generator import generate_pdf

# Set page config
st.set_page_config(
    page_title="Presupuestos - Pinturas El Niño",
    page_icon="🎨",
    layout="centered"
)

# Paths (Use /app/data for persistence in Docker, or local dir for dev)
DATA_DIR = os.getenv("DATA_DIR", get_app_path())
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
LOGO_FILE = os.path.join(DATA_DIR, "logo.png")

# Defaults
DEFAULT_CONFIG = {
    "theme": "flatly",
    "logo_path": "",
    "default_validity": "3 meses",
    "default_iva": "IVA incluido",
    "favorites": [
        "Pintura plástica blanca en paredes y techos",
        "Alisado de paredes (quitar gotelet)",
        "Lacado de puertas en blanco",
        "Tratamiento antimicótico para humedades"
    ]
}

def check_password():
    """Returns `True` if the user had the correct password."""
    
    # If no password is set in secrets, allow access (dev mode or risky mode)
    if "passwords" not in st.secrets:
        return True

    def password_entered():
        if st.session_state["password"] == st.secrets["passwords"]["main_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input
        st.text_input(
            "🔒 Introduce la contraseña:", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password incorrect, show input + error
        st.text_input(
            "🔒 Introduce la contraseña:", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        # Password correct
        return True

if not check_password():
    st.stop()  # Stop execution if not authenticated

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG

def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando configuración: {e}")

# Load Config
config = load_config()

# --- HEADER ---
st.title("Pinturas El Niño")
st.markdown("### Generador de Presupuestos")

# --- SIDEBAR (Settings) ---
with st.sidebar:
    st.header("Configuración")
    
    # Logo Uploader
    st.subheader("Logo")
    uploaded_logo = st.file_uploader("Subir Logo (Sobrescribe el actual)", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_logo is not None:
        with open(LOGO_FILE, "wb") as f:
            f.write(uploaded_logo.getbuffer())
        st.success("Logo actualizado!")
        config["logo_path"] = LOGO_FILE
        save_config(config)

    # Show current logo if exists
    current_logo = config.get("logo_path", "")
    if current_logo and os.path.exists(current_logo):
        st.image(current_logo, caption="Logo Actual", width=150)
    elif os.path.exists(LOGO_FILE):
         st.image(LOGO_FILE, caption="Logo Actual", width=150)

# --- MAIN FORM ---

# Client Data
st.subheader("Datos del Cliente")
col1, col2 = st.columns(2)
with col1:
    client_name = st.text_input("Nombre del Cliente", help="Se usará para el nombre del archivo")

# Services
st.subheader("Servicios")

# Add from favorites
favorites = config.get("favorites", [])
selected_fav = st.selectbox("Añadir de Favoritos", [""] + favorites)

if "services_list" not in st.session_state:
    st.session_state.services_list = []

# Logic to add favorite
if selected_fav and selected_fav not in st.session_state.services_list:
    st.session_state.services_list.append(selected_fav)

# Custom Service Input
col_serv, col_btn = st.columns([3, 1])
with col_serv:
    new_service = st.text_input("Nuevo Servicio Manual")
with col_btn:
    if st.button("Añadir"):
        if new_service:
            st.session_state.services_list.append(new_service)

# Display List
if st.session_state.services_list:
    st.markdown("**Lista de Servicios:**")
    for i, s in enumerate(st.session_state.services_list):
        cols = st.columns([0.9, 0.1])
        cols[0].text(f"• {s}")
        if cols[1].button("❌", key=f"del_{i}"):
            st.session_state.services_list.pop(i)
            st.rerun()
else:
    st.info("Añade servicios para comenzar.")

# Description
st.subheader("Descripción del Trabajo")
default_desc = (
            "Se sanearán las grietas y desconchones. Se aplicará una mano de fijador de cal y agua "
            "a las partes donde se haya quitado la pintura en mal estado o esté la pared virgen. "
            "Se terminará con dos manos de pintura de primera calidad."
)
description = st.text_area(
    "Detalles (Usa **negrita** y __cursiva__)", 
    value=default_desc,
    height=150
)

# Price
st.subheader("💰 Precio y Condiciones")
col_price, col_iva, col_validity = st.columns(3)

with col_price:
    amount = st.text_input("Importe Total (€)")

with col_iva:
    iva_opts = ["IVA incluido", "+ IVA", "Sin IVA", "(Personalizado)"]
    def_iva = config.get("default_iva", "IVA incluido")
    try:
        idx = iva_opts.index(def_iva)
    except:
        idx = 0
    iva_option = st.selectbox("IVA", iva_opts, index=idx)

with col_validity:
    validity = st.text_input("Validez", value=config.get("default_validity", "3 meses"))

# --- GENERATION ---
st.divider()

if st.button("GENERAR PRESUPUESTO", type="primary", use_container_width=True):
    # Validation
    if not st.session_state.services_list:
        st.error("❌ Faltan servicios.")
    elif not amount:
        st.error("❌ Falta el precio.")
    else:
        # Save config
        config["default_validity"] = validity
        config["default_iva"] = iva_option
        save_config(config)

        # Prepare Data
        # Construct Price String
        if iva_option == "(Personalizado)":
             full_price_str = f"{amount}€"
        else:
             full_price_str = f"{amount}€ {iva_option}"

        price_paragraph = (
            f"Yo me comprometo a la aportación de todo el material y/o herramienta necesaria para la "
            f"realización de dicho trabajo, teniendo este un coste total de {full_price_str}."
        )
        
        # Logo Logic
        final_logo_path = config.get("logo_path")
        if not final_logo_path or not os.path.exists(final_logo_path):
             # Try local file
             if os.path.exists(LOGO_FILE):
                 final_logo_path = LOGO_FILE
             else:
                 final_logo_path = None

        try:
            # Generate
            output_path = generate_pdf(
                st.session_state.services_list, 
                description, 
                full_price_str, 
                detailed_price_text=price_paragraph, 
                logo_path=final_logo_path,
                client_name=client_name,
                validity=validity
            )
            
            st.success("✅ Presupuesto creado con éxito!")
            
            # Download Button
            with open(output_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Descargar PDF",
                    data=pdf_file,
                    file_name=os.path.basename(output_path),
                    mime="application/pdf"
                )
                
        except Exception as e:
            st.error(f"Error generando PDF: {e}")
