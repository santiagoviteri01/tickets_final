import time
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import requests
#from streamlit_gsheets import GSheetsConnection
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import os
import json
from pathlib import Path
import numpy as np
import base64
import boto3
import uuid
import streamlit.components.v1 as components
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
import folium
from geopy.geocoders import Nominatim
import io
from dashboard import mostrar_dashboard_analisis
import segmentation_models_pytorch as smp
import torch
import albumentations as A
from albumentations.pytorch import ToTensorV2
from PIL import ImageDraw
import cv2
import smtplib
from email.message import EmailMessage
import base64
from string import Template
import matplotlib.pyplot as plt
from pandas.io.formats.style import Styler  # ✅ importa Styler explícitamente
from typing import Literal, Optional
from streamlit.components.v1 import html
from folium import Element


st.set_page_config(
    page_title="Insurapp",
    page_icon="",
    layout="wide"
)
st.markdown(
    """
    <style>
      /* Fuente global */
      html, body, .stApp {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        font-size: 16px;
        color: #7F7F7F;
        background-color: #FFFFFF;
      }

      /* Sidebar */
      section[data-testid="stSidebar"] {
        background-color: #7F7F7F !important;
        color: white !important;
      }

      section[data-testid="stSidebar"] .css-1v0mbdj,
      section[data-testid="stSidebar"] .css-1cpxqw2,
      section[data-testid="stSidebar"] label,
      section[data-testid="stSidebar"] p {
        color: white !important;
        font-family: 'Calibri', sans-serif !important;
      }
      
      /* Selectbox dentro del sidebar: texto gris oscuro y fondo blanco */
      section[data-testid="stSidebar"] select {
        background-color: #FFFFFF !important;
        color: #7F7F7F !important;
        border-radius: 8px !important;
        border: 2px solid #C5C5C5 !important;
        font-family: 'Calibri', sans-serif !important;
        font-weight: bold;
        padding: 6px 10px !important;
      }
      section[data-testid="stSidebar"] .stButton > button {
        background-color: #FFFFFF !important;
        color: #D62828 !important;
        border: 2px solid #D62828 !important;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        font-size: 15px !important;
        font-weight: bold;
        border-radius: 8px !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.3s ease;
        box-shadow: none !important;

      }
    
      /* Hover dentro del sidebar */
      section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #D62828 !important;
        color: #FFFFFF !important;
      }
      /* Títulos */
      h1, h2, h3 {
        color: #D62828;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
      }
      .stButton > button,
      section[data-testid="stSidebar"] .stButton > button,
      button[kind="formSubmit"],
      div[data-testid="stDownloadButton"] > button {
        background-color: #FFFFFF !important;
        color: #D62828 !important;
        border: 2px solid #D62828 !important;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        font-size: 15px !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s ease;
      }

      /* Hover: rojo invertido */
      .stButton > button:hover,
      section[data-testid="stSidebar"] .stButton > button:hover,
      button[kind="formSubmit"]:hover,
      div[data-testid="stDownloadButton"] > button:hover {
        background-color: #D62828 !important;
        color: #FFFFFF !important;
      }    

      /* Inputs y selects activos */
      input, textarea, select {
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        font-size: 15px !important;
        padding: 6px 10px !important;
        background-color: #FFFFFF !important;
        color: #7F7F7F !important;
        border-radius: 6px !important;
      }

      /* Inputs deshabilitados o solo lectura */
      input:disabled, textarea:disabled, select:disabled,
      input[readonly], textarea[readonly], select[readonly] {
        background-color: #7F7F7F !important;
        color: white !important;
        opacity: 1 !important;
      }
      /* Form submit buttons */
      button[kind="formSubmit"] {
        background-color: #FFFFFF !important;
        color: #D62828 !important;
        border: 2px solid #D62828 !important;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        font-size: 15px !important;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s ease;
      }

      button[kind="formSubmit"]:hover {
        background-color: #D62828 !important;
        color: #FFFFFF !important;
      }

      /* Métricas */
      .element-container .stMetric {
        font-size: 14px !important;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        color: #7F7F7F !important;
      }
      .stMetric > div {
        color: #7F7F7F !important;
      }

      /* Expander headers */
      .streamlit-expanderHeader {
        font-size: 16px !important;
        font-weight: bold;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
        color: white !important;
        background-color: #C5C5C5 !important;
        padding: 0.5rem !important;
        border-radius: 6px !important;
      }

      /* Contenido del expander desplegado */
      div.streamlit-expanderContent {
        background-color: #7F7F7F !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 1rem !important;
      }

      /* Markdown + texto adicional */
      .stMarkdown, .stText, .stDataFrame, .stTable, .css-1v0mbdj, .css-1cpxqw2 {
        color: white !important;
        font-family: 'Calibri', 'Segoe UI', sans-serif !important;
      }
      /* NUEVO: forzar texto plano gris oscuro */      
      .stMarkdown p,
      .stMarkdown span:not([style*="color"]),
      .stMarkdown li,
      .streamlit-expanderContent p,
      .streamlit-expanderContent span:not([style*="color"]),
      .streamlit-expanderContent li {
          color: #7F7F7F !important;
      }
      
      /* NUEVO: links en rojo institucional */
      a {
        color: #D62828 !important;
        font-weight: bold;
      }
      section[data-testid="stSidebar"] .stButton > button span {
        color: #D62828 !important;
      }
      section[data-testid="stSidebar"] .stButton > button:hover span {
        color: #FFFFFF !important;
      }
      section[data-testid="stSidebar"] .stButton > button div {
        color: #D62828 !important;
      }

      /* Hover: blanco al pasar el mouse */
      section[data-testid="stSidebar"] .stButton > button:hover div {
        color: #FFFFFF !important;
      }
      
      section[data-testid="stSidebar"] .stButton > button * {
        color: #D62828 !important;
      }  

      /* Hover: texto blanco */
      section[data-testid="stSidebar"] .stButton > button:hover * {
        color: #FFFFFF !important;
      }
      
      /* Caja falsa para mantener orden visual (opcional) */
      .zona-portal-fake {
        width: 100%;
        margin-bottom: 1.5rem;
      }
    
      /* Contenedor con borde visual real */
      .zona-portal-visual {
        border: 2px solid #7F7F7F;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
      }

    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <link rel="manifest" href="/manifest.json">
    <script>
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(reg => console.log('Service Worker registrado', reg))
                .catch(err => console.log('Error al registrar Service Worker', err));
        }
    </script>
    """,
    unsafe_allow_html=True
)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# Definir el alcance
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]

# Cargar las credenciales de Google desde los secretos de Streamlit
# O Método 2: Archivo secreto
creds_path = Path('/etc/secrets/google-creds.json')
creds_dict = json.loads(creds_path.read_text())

# Verificación
if not all([creds_dict["private_key"], creds_dict["client_email"]]):
    st.error("❌ Faltan credenciales. Configúralas en Render.")
    st.stop()
def upload_to_s3(file):
    # Inicializar cliente de S3
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION')
    )

    bucket_name = os.getenv('AWS_BUCKET_NAME')
    extension = file.name.split('.')[-1]
    file_key = f"fotos_siniestros/{uuid.uuid4()}.{extension}"  # ruta única

    # Subir a S3
    s3.upload_fileobj(file, bucket_name, file_key, ExtraArgs={"ACL": "public-read", "ContentType": file.type})

    # URL pública
    url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"
    return url

# Verificar que todas las credenciales estén presentes
required_keys = ["private_key_id", "private_key", "client_email", "client_id"]
missing_keys = [key for key in required_keys if not creds_dict.get(key)]

if missing_keys:
    st.error(f"❌ Faltan credenciales: {', '.join(missing_keys)}")
    st.stop()
    
@st.cache_resource
def get_gspread_client():
    # Convertir las credenciales a formato usable
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)

client = get_gspread_client()


@st.cache_resource
def get_spreadsheet():
    return client.open_by_key("13hY8la9Xke5-wu3vmdB-tNKtY5D6ud4FZrJG2_HtKd8")

spreadsheet = get_spreadsheet()

@st.cache_data(ttl=60) 
def cargar_worksheet(nombre_hoja):
    return spreadsheet.worksheet(nombre_hoja)

@st.cache_resource
def get_worksheet(nombre_hoja):
    return get_spreadsheet().worksheet(nombre_hoja)
    
@st.cache_data(ttl=60)
def cargar_df(nombre_hoja):
    hoja = get_worksheet(nombre_hoja)  # ✅ esta SÍ usa la función cacheada
    return pd.DataFrame(hoja.get_all_records())

@st.cache_data(ttl=60)
def cargar_df_seguro(nombre_hoja):
    st.cache_data.clear()
    hoja = spreadsheet.worksheet(nombre_hoja)
    return pd.DataFrame(hoja.get_all_records())

#Funciones sin cache:
def get_spreadsheet_sin_cache():
    return client.open_by_key("13hY8la9Xke5-wu3vmdB-tNKtY5D6ud4FZrJG2_HtKd8")
spreadsheet_sin_cache = get_spreadsheet_sin_cache()
def cargar_worksheet_sin_cache(nombre_hoja):
    return spreadsheet_sin_cache.worksheet(nombre_hoja)
def get_worksheet_sin_cache(nombre_hoja):
    return get_spreadsheet_sin_cache().worksheet(nombre_hoja)
def cargar_df_sin_cache(nombre_hoja):
    hoja = get_worksheet_sin_cache(nombre_hoja)  # ✅ esta SÍ usa la función cacheada
    return pd.DataFrame(hoja.get_all_records())


# Configuración de usuarios y contraseñas
USUARIOS = {
    "cliente1": {"password": "pass1", "rol": "cliente"},
    "cliente2": {"password": "pass2", "rol": "cliente"},
    "carlosserrano": {"password": "crediprime2", "rol": "admin"},
    "mauriciodavila": {"password": "insuratlan1", "rol": "admin"},
    "santiagoviteri": {"password": "insuratlan2", "rol": "admin"},
}
# Mantienes el acceso al worksheet
#defino asegurados df
asegurados_df=cargar_df("aseguradosfiltrados")
for _, row in asegurados_df.iterrows():
    client_id = str(row["NOMBRE COMPLETO"])
    USUARIOS[client_id] = {
        "password": client_id,  # Contraseña = ID en texto plano
        "rol": "cliente"
    }
    
def estilo_tabla(df: pd.DataFrame) -> Styler:
    def estilo_filas(fila):
        if fila.name == 'Total':
            return ['background-color: #D62828; color: white; font-weight: bold;' for _ in fila]
        else:
            return ['background-color: #C5C5C5; color: #7F7F7F;' for _ in fila]

    estilo = df.style\
        .apply(estilo_filas, axis=1)\
        .set_table_styles([
            {
                'selector': 'th',
                'props': [
                    ('background-color', '#C5C5C5'),
                    ('color', 'white'),
                    ('font-weight', 'bold'),
                    ('text-align', 'center')
                ]
            }
        ])\
        .set_properties(**{
            'text-align': 'center',
            'font-family': 'Calibri, sans-serif'
        })
    return estilo
    
def render_tabla_html(df,height):
    table_html = """
    <style>
        .tabla-container {
            overflow-x: auto;
            padding: 0.5rem;
        }

        table.custom-table {
            border-collapse: separate;
            border-spacing: 0;
            width: 100%;
            font-family: 'Calibri', sans-serif;
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            overflow: hidden;
        }

        table.custom-table th {
            background-color: #7F7F7F;
            color: white;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            border-bottom: 1px solid #999999;
        }

        table.custom-table td {
            background-color: #F2F2F2;
            color: #7F7F7F;
            text-align: center;
            padding: 8px;
            border-bottom: 1px solid white;
        }

        table.custom-table tr.total-row td {
            background-color: #D62828;
            color: white;
            font-weight: bold;
            border-top: 1px solid white;
        }

    </style>
    <div class="tabla-container">
        <table class="custom-table">
            <thead>
                <tr>
    """

    for col in df.columns:
        table_html += f"<th>{col}</th>"
    table_html += "</tr></thead><tbody>"

    for index, row in df.iterrows():
        clase_fila = "total-row" if str(index).lower() == "total" else ""
        table_html += f'<tr class="{clase_fila}">'
        for val in row:
            table_html += f"<td>{val}</td>"
        table_html += "</tr>"

    table_html += "</tbody></table></div>"

    components.html(table_html, height=height, scrolling=True)

    
def imagen_base64(ruta_img, ancho="100%"):
    img_path = Path(ruta_img)
    if not img_path.exists():
        st.warning(f"⚠️ Imagen no encontrada en {ruta_img}")
        return ""
    with open(img_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode()
    return f"<img src='data:image/png;base64,{img_b64}' style='width:{ancho}; border-radius:10px;'/>"

def mostrar_encabezado(texto_derecha=""):
    logo_path = Path("images/atlantida_logo.jpg")

    if not logo_path.exists():
        st.warning("⚠️ Logo no encontrado en 'images/atlantida_logo.jpg'")
        return

    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()

    html_template = Template("""
    <style>
        .encabezado-fijo {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 9999;
            background-color: #FFFFFF;
            padding: 10px 20px;
            border-bottom: 1px solid #ccc;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            font-family: 'Calibri', sans-serif;
        }

        .encabezado-fijo img {
            height: 40px;
        }

        .encabezado-texto {
            color: #7F7F7F;
            font-weight: bold;
            font-size: 18px;
        }

        @media (max-width: 768px) {
            .encabezado-fijo {
                flex-direction: column;
                align-items: flex-start;
                padding: 10px;
            }

            .encabezado-texto {
                font-size: 16px;
                margin-top: 5px;
            }
        }
    </style>

    <div class="encabezado-fijo">
        <img src="data:image/jpeg;base64,$logo_b64" alt="Atlántida Logo">
        <div class="encabezado-texto">$texto_derecha</div>
    </div>

    <!-- Espacio para que no se tape el contenido -->
    <div style="height:80px;"></div>
    """)

    html = html_template.substitute(logo_b64=logo_b64, texto_derecha=texto_derecha)
    components.html(html, height=140)

OPAQUE_CONTAINER_CSS = """
:root {{
    --background-color: #ffffff; /* Default background color */
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) div[data-testid="stVerticalBlock"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) > div[data-testid="stVerticalBlockBorderWrapper"] {{
    background-color: var(--background-color);
    width: 100%;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) div[data-testid="stVerticalBlock"]:has(div.opaque-container-{id}):not(:has(div.not-opaque-container)) > div[data-testid="element-container"] {{
    display: none;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.not-opaque-container):not(:has(div[class^='opaque-container-'])) {{
    display: none;
}}
""".strip()

OPAQUE_CONTAINER_JS = """
const root = parent.document.querySelector('.stApp');
let lastBackgroundColor = null;
function updateContainerBackground(currentBackground) {
    parent.document.documentElement.style.setProperty('--background-color', currentBackground);
    ;
}
function checkForBackgroundColorChange() {
    const style = window.getComputedStyle(root);
    const currentBackgroundColor = style.backgroundColor;
    if (currentBackgroundColor !== lastBackgroundColor) {
        lastBackgroundColor = currentBackgroundColor; // Update the last known value
        updateContainerBackground(lastBackgroundColor);
    }
}
const observerCallback = (mutationsList, observer) => {
    for(let mutation of mutationsList) {
        if (mutation.type === 'attributes' && (mutation.attributeName === 'class' || mutation.attributeName === 'style')) {
            checkForBackgroundColorChange();
        }
    }
};
const main = () => {
    checkForBackgroundColorChange();
    const observer = new MutationObserver(observerCallback);
    observer.observe(root, { attributes: true, childList: false, subtree: false });
}
// main();
document.addEventListener("DOMContentLoaded", main);
""".strip()


# ————— OPAQUE CONTAINER HELPERS —————
def st_opaque_container(
    *,
    height: Optional[int] = None,
    border: Optional[bool] = None,
    key: Optional[str] = None,
):
    opaque = st.container()
    non_opaque = st.container()
    css = OPAQUE_CONTAINER_CSS.format(id=key)
    with opaque:
        html(f"<script>{OPAQUE_CONTAINER_JS}</script>", scrolling=False, height=0)
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.markdown(f"<div class='opaque-container-{key}'></div>", unsafe_allow_html=True)
    with non_opaque:
        st.markdown("<div class='not-opaque-container'></div>", unsafe_allow_html=True)
    return opaque.container(height=height, border=border)


FIXED_CONTAINER_CSS = """
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)){{
    background-color: transparent;
    position: {mode};
    width: inherit;
    background-color: inherit;
    {position}: {margin};
    z-index: 999;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) div[data-testid="stVerticalBlock"]:has(div.fixed-container-{id}):not(:has(div.not-fixed-container)) > div[data-testid="element-container"] {{
    display: none;
}}
div[data-testid="stVerticalBlockBorderWrapper"]:has(div.not-fixed-container):not(:has(div[class^='fixed-container-'])) {{
    display: none;
}}
""".strip()

MARGINS = {
    "top": "-50px",
    "bottom": "0",
}


# ————— FIXED CONTAINER HELPERS —————
def st_fixed_container(
    *,
    height: Optional[int] = None,
    border: Optional[bool] = None,
    mode: Literal["fixed", "sticky"] = "fixed",
    position: Literal["top", "bottom"] = "top",
    margin: Optional[str] = None,
    transparent: bool = False,
    key: Optional[str] = None,
):
    if margin is None:
        margin = MARGINS[position]
    fixed = st.container()
    non_fixed = st.container()
    css = FIXED_CONTAINER_CSS.format(id=key, mode=mode, position=position, margin=margin)
    with fixed:
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
        st.markdown(f"<div class='fixed-container-{key}'></div>", unsafe_allow_html=True)
    with non_fixed:
        st.markdown("<div class='not-fixed-container'></div>", unsafe_allow_html=True)
    with fixed:
        if transparent:
            return st.container(height=height, border=border)
        return st_opaque_container(height=height, border=border, key=f"opaque_{key}")


# ————— TU HEADER USANDO st_fixed_container_header —————
def mostrar_encabezado(texto_derecha=""):
    logo_path = Path("images/atlantida_logo.jpg")
    if not logo_path.exists():
        st.warning("⚠️ Logo no encontrado en 'images/atlantida_logo.jpg'")
        return
    b64 = base64.b64encode(logo_path.read_bytes()).decode()

    # 1) Inyecta el header fijo + spacer
    with st_fixed_container_header(key="hdr"):
        cols = st.columns([1, 6, 1])
        with cols[0]:
            st.image(f"data:image/jpeg;base64,{b64}", width=40)
        with cols[1]:
            st.markdown(
                f"<h3 style='margin:0; color:#7F7F7F; "
                "font-family:Calibri,sans-serif;'>"
                f"{texto_derecha}</h3>",
                unsafe_allow_html=True
            )
        with cols[2]:
            if st.button("Cerrar Sesión", use_container_width=True):
                st.session_state.autenticado = False
                st.session_state.mostrar_login = False
    
def encabezado_sin_icono(texto, nivel="h2"):
    estilo = {
        "h1": "font-size:28px; font-weight:bold;",
        "h2": "font-size:22px; font-weight:bold;",
        "h3": "font-size:18px;",
    }.get(nivel, "font-size:22px; font-weight:bold;")

    html = f"""
    <div style='margin-bottom:10px;'>
        <span style='{estilo} color:#D8272E; font-family:Calibri, sans-serif;'>{texto}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

    
def encabezado_con_icono(ruta_icono, texto, nivel="h2"):
    tamaños = {"h1": 28, "h2": 22, "h3": 18}
    estilo = {
        "h1": "font-size:28px; font-weight:bold;",
        "h2": "font-size:22px; font-weight:bold;",
        "h3": "font-size:18px;",
    }
    tamaño = tamaños.get(nivel, 22)
    estilo_texto = estilo.get(nivel, "font-size:22px;")

    icon_path = Path(ruta_icono)
    if not icon_path.exists():
        st.warning(f"⚠️ No se encontró el ícono en {ruta_icono}")
        return

    with open(icon_path, "rb") as f:
        icon_b64 = base64.b64encode(f.read()).decode()

    html = f"""
    <div style='display:flex; align-items:center; gap:10px; margin-bottom:10px;'>
        <img src="data:image/png;base64,{icon_b64}" style='height:{tamaño}px;' />
        <span style='color:#D8272E; {estilo_texto} font-family:Calibri, sans-serif;'>{texto}</span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
def cargar_datos():
    try:
        df = cargar_df("hoja")
        # 🔥 Aseguramos que siempre existan estas columnas, aunque vengan vacías
        for col in ['Grua', 'Asistencia_Legal', 'Ubicacion', 'Foto_URL']:
            if col not in df.columns:
                df[col] = None
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame(columns=['Número','Título','Área','Estado','Descripción',
                                     'Fecha_Creación','Usuario_Creación','Fecha_Modificacion',
                                     'Usuario_Modificacion','Tiempo_Cambio','Cliente',
                                     'Grua','Asistencia_Legal','Ubicacion','Foto_URL'])


@st.cache_data(ttl=60)
def cargar_datos_dashboard_desde_sheets():
    df_pagados = cargar_df("pagados")
    df_pendientes = cargar_df("pendientes")
    df_asegurados = cargar_df("aseguradosfiltrados")
    return df_pagados, df_pendientes, df_asegurados

def descargar_archivos_ticket(numero_ticket, nombre_cliente):
    df_adjuntos = cargar_df("archivos_adjuntos")
    archivos_ticket = df_adjuntos[df_adjuntos["Número Ticket"] == numero_ticket]

    if archivos_ticket.empty:
        st.warning("No hay archivos subidos para este ticket.")
        return

    import zipfile

    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        for _, row in archivos_ticket.iterrows():
            url = row["URL"]
            nombre_archivo = row["Nombre Archivo"]
            try:
                # Descargar archivo desde URL
                import requests
                response = requests.get(url)
                if response.status_code == 200:
                    zip_file.writestr(nombre_archivo, response.content)
            except Exception as e:
                st.error(f"Error descargando {nombre_archivo}: {e}")

    buffer.seek(0)
    nombre_zip = f"{nombre_cliente.replace(' ', '_')}_ticket_{numero_ticket}.zip"
    st.download_button(
        label="Descargar todos los archivos",
        data=buffer,
        file_name=nombre_zip,
        mime="application/zip"
    )
   
def subir_y_mostrar_archivo(archivo, bucket_name, numero_ticket, hoja_adjuntos, usuario):
    file_type = archivo.type
    extension = archivo.name.split('.')[-1]
    unique_filename = f"adjuntos/{str(uuid.uuid4())}.{extension}"
    archivo_url = f"https://{bucket_name}.s3.us-east-1.amazonaws.com/{unique_filename}"

    # ✅ Leer contenido en memoria para evitar que se cierre
    archivo_bytes = archivo.read()
    archivo_buffer = io.BytesIO(archivo_bytes)

    # ✅ Subir a S3
    archivo_buffer.seek(0)
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name='us-east-1'
    )
    s3.upload_fileobj(
        archivo_buffer,
        bucket_name,
        unique_filename,
        ExtraArgs={'ContentType': file_type, 'ACL': 'public-read'}
    )

    # ✅ Guardar en Google Sheets
    hoja_adjuntos.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        usuario,
        numero_ticket,
        archivo.name,
        file_type,
        archivo_url
    ])
    st.cache_data.clear()  # ← LIMPIA CACHE

    # ✅ Mostrar feedback visual
    st.success(f"✅ `{archivo.name}` subido correctamente al ticket #{numero_ticket}")

    if file_type == "application/pdf":
        base64_pdf = base64.b64encode(archivo_bytes).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.image(io.BytesIO(archivo_bytes), caption=archivo.name, use_container_width=True)

    st.markdown(f"[Ver archivo en S3]({archivo_url})")
    st.markdown("---")
    
def formulario_cotizacion():
    encabezado_sin_icono("Formulario de Cotización","h1")
    tipo_seguro = st.selectbox("¿Qué seguro deseas cotizar?", ["Vida", "Auto", "Accidentes Personales"])
    nombre = st.text_input("Nombres")
    apellidos = st.text_input("Apellidos")
    correo = st.text_input("Correo electrónico")
    telefono = st.text_input("Número de teléfono")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Enviar solicitud de cotización"):
            if not all([tipo_seguro, nombre, apellidos, correo, telefono]):
                st.warning("Por favor completa todos los campos.")
            else:
                hoja_cotizaciones = cargar_worksheet_sin_cache("cotizaciones")
                nueva_fila = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo_seguro, nombre, apellidos, correo, telefono, "NO COTIZADA"]
                hoja_cotizaciones.append_row(nueva_fila)
                st.success("🎉 Tu solicitud ha sido enviada exitosamente. Pronto nos contactaremos contigo.")
                time.sleep(1.5)
                st.session_state.mostrar_formulario_cotizacion = False
                st.rerun()

    with col2:
        if st.button("Volver"):
            st.session_state.mostrar_formulario_cotizacion = False
            st.rerun()

if 'recargar_tickets' not in st.session_state:
    st.session_state.recargar_tickets = False
    
def landing_page():
    import base64
    from pathlib import Path

    # Convertir logo a base64
    logo_path = "images/atlantida_logo.jpg"
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()

    # Convertir imagen principal a base64
    image_path = "images/landing_image.jpg"
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>
          .logo-bar {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem 0;
            background-color: #FFFFFF;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
            margin-bottom: 2rem;
          }}
          .logo-bar img {{
            height: 100px;
            object-fit: contain;
          }}
          .main-container {{
            padding: 2rem;
            text-align: center;
            font-family: 'Calibri', sans-serif;
            background-color: #FFFFFF;
            color: #333333;
          }}
          .hero-title {{
            font-size: 4rem;
            color: #D8272E;
            font-weight: bold;
            margin-bottom: 1rem;
          }}
          .hero-subtitle {{
            font-size: 1.4rem;
            color: #7F7F7F;
            max-width: 700px;
            margin: 0 auto 2rem auto;
            text-align: center;
          }}

          .hero-image {{
            width: 100%;
            max-width: 500px;
            height: auto;
            margin: 0 auto 2rem auto;
            border-radius: 12px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.08);
          }}
          .hero-buttons .stButton>button {{
            margin: 0 1rem;
            padding: 0.8rem 2rem;
            font-size: 1rem;
            border: 2px solid #D8272E;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            background-color: #FFFFFF;
            color: #D8272E;
            transition: all 0.3s ease;
          }}
          .hero-buttons .stButton>button:hover {{
            background-color: #D8272E !important;
            color: #FFFFFF !important;
            transform: scale(1.03);
          }}
          @media (max-width: 768px) {{
            .hero-title {{
              font-size: 2.4rem;
            }}
            .hero-subtitle {{
              font-size: 1.1rem;
              padding: 0 1rem;
            }}
            .hero-buttons .stButton>button {{
              width: 100%;
              margin: 0.5rem 0;
            }}
          }}
        </style>

        <div class="logo-bar">
          <img src="data:image/jpeg;base64,{logo_b64}" alt="Atlántida Insurance logo" />
        </div>

        <div class="main-container">
          <div class='hero-title'>
            Bienvenido a InsurApp
          </div>

          <div class='hero-subtitle'>
            Tu sistema inteligente de gestión de seguros y reclamos. Rápido, seguro y accesible desde cualquier lugar.
          </div>

          <!-- Imagen institucional -->
          <img class="hero-image" src="data:image/jpeg;base64,{image_b64}" alt="Imagen institucional"/>

          <!-- Botones -->
          <div class='hero-buttons'>
        """,
        unsafe_allow_html=True
    )

    # Botones funcionales
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mi Cuenta", use_container_width=True):
            st.session_state.mostrar_login = True
            st.session_state.mostrar_formulario_cotizacion = False
            st.rerun()
    with col2:
        if st.button("Cotiza con Nosotros", use_container_width=True):
            st.session_state.mostrar_login = False
            st.session_state.mostrar_formulario_cotizacion = True
            st.rerun()

    # Cierre del div
    st.markdown("</div></div>", unsafe_allow_html=True)
       
def detectar_dispositivo():
    width = streamlit_js_eval(js_expressions="window.innerWidth", key="GET_WIDTH")
    if width is None:
        st.stop()
    st.session_state["mobile"] = width < 600

def autenticacion():
    detectar_dispositivo()

    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    if "mobile" not in st.session_state:
        st.warning("Cargando...")
        st.stop()  # ⚠️ Esto detiene el render hasta que mobile esté en session_state

    is_mobile = st.session_state.get("mobile", False)

    if not st.session_state.autenticado:
        imagen_html = imagen_base64("images/atlantida_logo.jpg", ancho="50%")  # o el icono nuevo

        if is_mobile:
            st.markdown(
                f"""
                <div style='display: flex; justify-content: center; margin-bottom: 1rem;'>
                    {imagen_html}
                </div>
                """,
                unsafe_allow_html=True
            )
            usuario = st.text_input("Usuario")
            contraseña = st.text_input("Contraseña", type="password")
            col1, col2 = st.columns([2, 1])
            with col1:
                if st.button("Ingresar"):
                    user_data = USUARIOS.get(usuario)
                    if user_data and user_data['password'] == contraseña:
                        st.session_state.autenticado = True
                        st.session_state.usuario_actual = usuario
                        st.session_state.rol = user_data['rol']
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
            with col2:
                if st.button("Volver"):
                    st.session_state.mostrar_login = False
                    st.rerun()
        else:
            col_form, col_img = st.columns([1, 1])
            with col_form:
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: center; margin-bottom: 1rem;'>
                        {imagen_html}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                usuario = st.text_input("Usuario")
                contraseña = st.text_input("Contraseña", type="password")
                col1, col2 = st.columns([2, 1])
                with col1:
                    if st.button("Ingresar"):
                        user_data = USUARIOS.get(usuario)
                        if user_data and user_data['password'] == contraseña:
                            st.session_state.autenticado = True
                            st.session_state.usuario_actual = usuario
                            st.session_state.rol = user_data['rol']
                            st.rerun()
                        else:
                            st.error("❌ Credenciales incorrectas")
                with col2:
                    if st.button("Volver"):
                        st.session_state.mostrar_login = False
                        st.rerun()
            with col_img:
                st.markdown(
                    f"""
                    <div style='display: flex; align-items: flex-start; justify-content: center; margin-top: -8rem;'>
                        {imagen_base64("images/imagen_logo.jpg", ancho="70%")}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        return False

    return True


from folium.plugins import LocateControl
geolocator = Nominatim(user_agent="mi_app_insurapp")
from streamlit.runtime.scriptrunner import RerunException
# Si no necesitas reverse geocoding, puedes eliminar Geolocator
def obtener_ubicacion():
    # 0) Detecto si es móvil
    mobile = st.session_state.get("mobile", False)
    map_width  = "100%" if mobile else 600
    map_height = 300    if mobile else 450
    zoom_start = 14     if mobile else 16

    # 1) Pedir permiso la primera vez
    if "ubicacion_coords" not in st.session_state:
        encabezado_con_icono("iconos/pingps.png", "Solicitando permiso de ubicación…", "h3")

        js = """
        new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                pos => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude}),
                err => reject(err.message),
                {enableHighAccuracy: true, timeout:10000, maximumAge:0}
            );
        })
        """
        coords = streamlit_js_eval(js_expressions=js, key="get_geo")
        if not coords or "lat" not in coords:
            st.warning("Para continuar, **permite** el acceso a tu ubicación.")
            return ""
        st.session_state.ubicacion_coords = {"lat": coords["lat"], "lon": coords["lon"]}
        st.success("Permiso concedido y ubicación obtenida.")

    # 2) Leer coords actuales
    lat = st.session_state.ubicacion_coords["lat"]
    lon = st.session_state.ubicacion_coords["lon"]

    # 3) Construir mapa y marcador fijo
    m = folium.Map(location=[lat, lon], zoom_start=zoom_start, width=map_width, height=map_height)
    LocateControl(auto_start=False, flyTo=True).add_to(m)
    folium.Marker(
        [lat, lon],
        icon=folium.Icon(color="red", icon="map-pin", prefix="fa"),
        popup="📍 Ubicación seleccionada"
    ).add_to(m)
    
    css = """
    <style>
      .leaflet-container, 
      .leaflet-container > img, 
      .leaflet-container > div {
        margin: 0 !important;
        padding: 0 !important;
        box-sizing: border-box;
      }
    </style>
    """
    m.get_root().html.add_child(Element(css))
    # 4) Mostrar y capturar clic (la “manito”)
    salida = st_folium(
        m,
        height=map_height,
        width=map_width,
        returned_objects=["last_clicked"]
    )
    # — Aquí el mensaje de ayuda —
    st.info(
        "Para ajustar tu ubicación, haz zoom al mapa "
        "y dale doble click (o tap) a la pantalla."
    )

    # 5) Si hubo clic, actualizamos coords y refrescamos
    if salida and salida.get("last_clicked"):
        click = salida["last_clicked"]
        nueva = {"lat": click["lat"], "lon": click["lng"]}
        st.session_state.ubicacion_coords = nueva
        st.success(f"🔄 Coordenadas ajustadas: {nueva['lat']:.6f}, {nueva['lon']:.6f}")

    # 6) Generar URIs siempre con las coords en session_state
    lat_cur = st.session_state.ubicacion_coords["lat"]
    lon_cur = st.session_state.ubicacion_coords["lon"]
    web_uri = f"https://www.google.com/maps/search/?api=1&query={lat_cur},{lon_cur}"

    # 7) Mostrar enlace para móvil y escritorio
    st.markdown(
        f"**Enlace Web:** {web_uri}",
        unsafe_allow_html=True
    )

    # 8) Confirmar ubicación
    if st.form_submit_button("Confirmar ubicación"):
        pass

    web_uri = f"https://maps.google.com/maps?q={lat},{lon}"
    return web_uri
  
from PIL import Image
from ultralytics import YOLO
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# 1. Carga del modelo (se cachea para no recargar en cada interacción)
@st.cache_resource
def cargar_modelo_yolo():
    return YOLO("modelos/best.pt")

# 1. Carga del modelo (se cachea para no recargar en cada interacción)
@st.cache_resource
def load_detector():
    # Puedes cambiar 'yolov8n.pt' por el checkpoint que prefieras
    return YOLO('yolov8n.pt')

model = load_detector()

# 2. Función auxiliar para verificar si hay un auto
def contiene_auto(pil_img: Image.Image, conf_threshold=0.10) -> bool:
    # Convertir a numpy array compatible
    img_np = np.array(pil_img)
    # Inferencia
    results = model.predict(source=img_np, conf=conf_threshold, verbose=False)
    # Revisar cada detección
    for det in results:
        # det.boxes.cls es un tensor con índices de clase
        clases = det.boxes.cls.cpu().numpy().astype(int)
        for c in clases:
            if model.names[c] == 'car':
                return True
    return False

TEMPLATES = {
    "AIG":     "archivos_coberturas/certificado_aig_temp.docx",
    "MAPFRE":  "archivos_coberturas/certificado_mapfre_temp.docx",
    "ZURICH SEGUROS":  "archivos_coberturas/certificado_zurich_temp.docx",
}

import subprocess
import tempfile
from docxtpl import DocxTemplate

def generar_certificado_pdf_from_template(
    df_asegurados: pd.DataFrame,
    cliente_id: str,
    template_path: str
) -> io.BytesIO:
    """
    1) Rellena la plantilla .docx en memoria.
    2) Guarda un .docx temporal.
    3) Llama a LibreOffice headless para convertirlo a PDF.
    4) Devuelve un BytesIO con el PDF listo.
    """
    # Filtrar y preparar datos (idéntico a tu lógica)
    df = df_asegurados[df_asegurados["NOMBRE COMPLETO"] == cliente_id].copy()
    if df.empty:
        raise ValueError(f"No encontrado '{cliente_id}'")
    df["NÚMERO RENOVACIÓN"] = df["NÚMERO RENOVACIÓN"].astype(int)

    # Columnas numéricas a limpiar
    numeric_cols = [
        "VALOR ASEGURADO",
        "PRIMA TOTAL VEHÍCULOS",
        "IMPUESTO VEHÍCULOS EMISIÓN",
        "IMPUESTO VEHÍCULOS SUPER DE BANCOS",
        "IMPUESTO VEHÍCULOS SEGURO CAMPESINO",
        "IMPUESTO VEHÍCULOS IVA",
        "PRIMA VEHÍCULOS"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # 2) Escoger la fila de mayor renovación
    fila = df.loc[df["NÚMERO RENOVACIÓN"].idxmax()]

    # 3) Montar el contexto para la plantilla
    context = {
        "tipo_id":     fila["TIPO IDENTIFICACIÓN"],
        "numero_id":   fila["NÚMERO IDENTIFICACIÓN"],
        "nombre1":     fila["NOMBRE1"],
        "nombre2":     fila["NOMBRE2"],
        "apellido1":   fila["APELLIDO1"],
        "apellido2":   fila["APELLIDO2"],
        "nombre":      fila["NOMBRE COMPLETO"],
        "genero":      fila["GENERO"],
        "estado_civil":fila["ESTADO CIVIL"],
        "ciudad":            fila["CIUDAD CLIENTE"],
        "direccion_oficina": fila["DIRECCIÓN OFICINA"],
        "telefono_oficina":  fila["TELÉFONO OFICINA"],
        "direccion_dom":     fila["DIRECCIÓN DOMICILIO"],
        "telefono_dom":      fila["TELÉFONO DOMICILIO"],
        "email":             fila["CORREO ELECTRÓNICO"],
        "fecha_nac":         pd.to_datetime(fila["FECHA NACIMIENTO"]).strftime("%d/%m/%Y"),
        "poliza_maestra":    fila["POLIZA MAESTRA"],
        "poliza":            fila["NÚMERO PÓLIZA VEHÍCULOS"],
        "liderseg":          fila["ID"],
        "marca":             fila["MARCA"],
        "modelo":            fila["MODELO"],
        "motor":             fila["MOTOR"],
        "chasis":            fila["CHASIS"],
        "color":             fila["COLOR"],
        "ano":               fila["AÑO"],
        "concesionario":     fila["CONCESIONARIO"],
        "ano_carro":         fila["AÑOCARRO"],
        "tipo":              fila["CLASE (TIPO)"],
        "fecha_ini":         pd.to_datetime(fila["FECHA VIGENCIA"]).strftime("%d/%m/%Y"),
        "fecha_ven":         pd.to_datetime(fila["FECHA EXPIRACIÓN"]).strftime("%d/%m/%Y"),
        "fecha_emi":         pd.to_datetime(fila["FECHA"]).strftime("%d/%m/%Y"),
        "tipo_placa":        fila["TIPO PLACA"],
        "placa":             fila["PLACA"],
        "accesorios":        fila["ACCESORIOS"],
        "benef_acr":         fila["BENEFICIARIO ACREEDOR"],
        "emision":           f"${fila['IMPUESTO VEHÍCULOS EMISIÓN']:,.2f}",
        "imp_super":         f"${fila['IMPUESTO VEHÍCULOS SUPER DE BANCOS']:,.2f}",
        "imp_camp":          f"${fila['IMPUESTO VEHÍCULOS SEGURO CAMPESINO']:,.2f}",
        "iva":               f"${fila['IMPUESTO VEHÍCULOS IVA']:,.2f}",
        "valor_asegurado":   f"${fila['VALOR ASEGURADO']:,.2f}",
        "prima":             f"${fila['PRIMA VEHÍCULOS']:,.2f}",
        "prima_total":       f"${fila['PRIMA TOTAL VEHÍCULOS']:,.2f}",
    }

    # 1) Rellenar y volcar a buffer .docx
    doc = DocxTemplate(template_path)
    doc.render(context)
    buf_docx = io.BytesIO()
    doc.save(buf_docx)
    buf_docx.seek(0)

    # 2) Guardar DOCX temporal en disco
    tmp_docx = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    tmp_docx.write(buf_docx.read())
    tmp_docx.close()

    # 3) Convertir a PDF con LibreOffice headless
    tmp_pdf = tmp_docx.name.replace(".docx", ".pdf")
    subprocess.run([
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", os.path.dirname(tmp_docx.name),
        tmp_docx.name
    ], check=True)

    # 4) Leer el PDF en buffer y limpiar
    buf_pdf = io.BytesIO(open(tmp_pdf, "rb").read())
    buf_pdf.seek(0)
    os.remove(tmp_docx.name)
    os.remove(tmp_pdf)
    return buf_pdf
    
def enviar_correo_reclamo(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg["Subject"] = asunto
    msg["From"] = os.environ.get("EMAIL_RECLAMOS")
    msg["To"] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:  # ← CAMBIADO
            smtp.starttls()
            smtp.login(os.environ["EMAIL_RECLAMOS"], os.environ["EMAIL_RECLAMOS_PASS"])
            smtp.send_message(msg)
        return True
    except Exception as e:
        st.error(f"❌ Error al enviar el correo: {e}")
        return False

def persistir_en_sheet(df: pd.DataFrame):
    # Formateo de fechas a string
    for c in df.select_dtypes(include=["datetime64", "datetime64[ns]"]):
        df[c] = df[c].dt.strftime("%Y-%m-%d")

    # Reemplaza NaN/NaT con cadenas vacías
    df = df.fillna("").astype(str)

    # Prepara la matriz de valores (incluyendo cabecera)
    values = [df.columns.tolist()] + df.values.tolist()
    hoja = spreadsheet_sin_cache.worksheet("aseguradosfiltrados")
    # Limpia la hoja y sube todo
    hoja.clear()
    hoja.update(values)
    
def gestionar_asegurados():
    encabezado_con_icono("iconos/buscar.png", "Buscar y Editar Asegurados", "h1")
    with st.expander("Filtros de Búsqueda", expanded=True):
        col1, col2 = st.columns(2)
        buscar_id     = col1.text_input("ID")
        buscar_poliza = col2.text_input("Número de Póliza")
        buscar_cedula = col1.text_input("Número de Cédula")
        buscar_nombre = col2.text_input("Nombre Completo (o parte)")

    EDITABLE_COLS = [
        "TELÉFONO DOMICILIO",
        "CORREO ELECTRÓNICO",
        "OBSERVACIÓN",
        "BENEFICIARIO ACREEDOR",
        "ESTADO PÓLIZA",
        "NÚMERO FACTURA VEHÍCULOS"
    ]

    df_asegurados = cargar_df_sin_cache("aseguradosfiltrados")
    st.session_state["df_original"] = df_asegurados
    df_original = st.session_state["df_original"]

    mask = pd.Series(True, index=df_original.index)
    if buscar_id:
        mask &= df_original["ID"].astype(str) == buscar_id.strip()
    if buscar_poliza:
        mask &= df_original["NÚMERO PÓLIZA VEHÍCULOS"].astype(str) == buscar_poliza.strip()
    if buscar_cedula:
        mask &= df_original["NÚMERO IDENTIFICACIÓN"].astype(str) == buscar_cedula.strip()
    if buscar_nombre:
        mask &= df_original["NOMBRE COMPLETO"].str.contains(buscar_nombre.strip(), case=False, na=False)

    df_filtrado = df_original[mask]

    if df_filtrado.empty:
        st.warning("No se encontró ningún asegurado con esos criterios.")
        return

    registro = df_filtrado.sort_values("NÚMERO RENOVACIÓN", ascending=False).iloc[0]
    mask_upd = (df_original["ID"] == registro["ID"]) & \
               (df_original["NÚMERO RENOVACIÓN"] == registro["NÚMERO RENOVACIÓN"])    
    registro_act = df_original[mask_upd].iloc[0]  # ✅ Esta línea es clave

    encabezado_sin_icono("Detalles del Asegurado","h2")
    left, right = st.columns([1, 2])

    with left:
        st.info(f"**Nombre:** {registro['NOMBRE COMPLETO']}")
        st.info(f"**ID:** {registro['ID']}")
        st.info(f"**Cédula:** {registro['NÚMERO IDENTIFICACIÓN']}")
        st.info(f"**Póliza:** {registro['NÚMERO PÓLIZA VEHÍCULOS']}")

    with right:
        encabezado_con_icono("iconos/editar.png", "Editar Campos", "h2")
        with st.form("editar_aseg_form"):
            telefono        = st.text_input("Teléfono", registro["TELÉFONO DOMICILIO"])
            correo          = st.text_input("Correo Electrónico", registro["CORREO ELECTRÓNICO"])
            observacion     = st.text_area("Observación", registro["OBSERVACIÓN"])
            beneficiario    = st.text_area("Beneficiario Acreedor", registro["BENEFICIARIO ACREEDOR"])
            estado_poliza   = st.selectbox(
                "Estado de Póliza",
                options=[
                    "DOCUMENTOS AUDITADOS",
                    "PÓLIZA CREADA",
                    "PÓLIZA VENCIDA RENOVADA",
                    "CANCELADA"
                ],
                index=[
                    "DOCUMENTOS AUDITADOS",
                    "PÓLIZA CREADA",
                    "PÓLIZA VENCIDA RENOVADA",
                    "CANCELADA"
                ].index(registro["ESTADO PÓLIZA"])
            )
            num_factura = st.text_input("Número Factura Vehículos", registro["NÚMERO FACTURA VEHÍCULOS"])
            submitted = st.form_submit_button("Guardar Cambios")

        if submitted:
            df_original.loc[mask_upd, "TELÉFONO DOMICILIO"] = telefono
            df_original.loc[mask_upd, "CORREO ELECTRÓNICO"] = correo
            df_original.loc[mask_upd, "OBSERVACIÓN"] = observacion
            df_original.loc[mask_upd, "BENEFICIARIO ACREEDOR"] = beneficiario
            df_original.loc[mask_upd, "ESTADO PÓLIZA"] = estado_poliza
            df_original.loc[mask_upd, "NÚMERO FACTURA VEHÍCULOS"] = num_factura

            st.session_state["df_original"] = df_original
            persistir_en_sheet(df_original)
            st.success("✅ Cambios guardados")
            df_registro = registro_act.to_frame().T
            render_tabla_html(df_registro,height=150)


    # 📄 EMITIR CERTIFICADO
    if st.button("Emitir Certificado de Cobertura"):
        try:
            TEMPLATES = {
                "AIG": "archivos_coberturas/certificado_aig_temp.docx",
                "MAPFRE": "archivos_coberturas/certificado_mapfre_temp.docx",
                "ZURICH SEGUROS": "archivos_coberturas/certificado_zurich_temp.docx",
            }
            aseguradora = registro_act["ASEGURADORA"].strip().upper()
            tpl_path = TEMPLATES[aseguradora]

            buffer_pdf = generar_certificado_pdf_from_template(
                df_asegurados=df_original,
                cliente_id=registro["NOMBRE COMPLETO"],
                template_path=tpl_path
            )

            st.download_button(
                label="Descargar Certificado PDF",
                data=buffer_pdf,
                file_name=f"Certificado_{registro['NOMBRE COMPLETO'].replace(' ', '_')}.pdf",
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"❌ No se pudo generar el certificado: {e}")

            
# Portal del Cliente
def portal_cliente():
    st.sidebar.title("Menú Cliente")
    tab_seleccionado = ["Mis Datos Personales", "Mis Tickets", "Nuevo Reclamo", "Subir Archivos Adicionales a un Reclamo"]
    tab_seleccionado = st.sidebar.radio("Opciones", tab_seleccionado)
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.mostrar_login = False
        st.success("Sesión cerrada exitosamente")
        time.sleep(1)
        st.rerun()
    
    st.markdown(
        """
        <style>
          @media (max-width: 600px) {
            .header-text { display: none !important; }
          }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ——— Header fijo arriba ———
    with st_fixed_container(mode="fixed", position="top", transparent=False, key="header_top"):
        col1, col2, col3 = st.columns([1, 6, 1], gap="small")
        with col1:
            b64 = base64.b64encode(Path("images/atlantida_logo.jpg").read_bytes()).decode()
            st.markdown(
                f"<img src='data:image/jpeg;base64,{b64}' style='height:60px;' />",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f"""
                <div class="header-text" style="margin-left:-20px;">
                  <h5 style="margin:0; color:#7F7F7F; font-family:Calibri,sans-serif;">
                    Cliente: {st.session_state.usuario_actual}
                  </h5>
                </div>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.write("")
                
    st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)


                
    # Cuadro visual con borde
    with st.container():
        # Fondo y borde simulados mediante un markdown antes y después
        st.markdown("<hr style='border:1px solid #7F7F7F; margin-top:0rem;'>", unsafe_allow_html=True)
        # fondo blanco con borde visual simulado como encabezado
        st.markdown(
            """
            <div style="border:1px solid #FFFFFF; border-radius:10px; padding:20px; background-color:#FFFFFF;">
            """,
            unsafe_allow_html=True
        )
    
        # Contenido: título
        st.markdown(
            f"<h2 style='color:#D62828; font-family:Calibri, sans-serif;'>Portal del Cliente - {st.session_state.usuario_actual}</h2>",
            unsafe_allow_html=True
        )
        # Cierre visual del bloque
        st.markdown("</div>", unsafe_allow_html=True)
    
        st.markdown("<hr style='border:1px solid #7F7F7F; margin-top:1rem;'>", unsafe_allow_html=True)

    if tab_seleccionado == "Mis Datos Personales":
        encabezado_con_icono("iconos/verdatos.png", "Mis Datos Personales y del Vehículo", "h1")
        cliente_id = st.session_state.usuario_actual
        cliente_data = asegurados_df[asegurados_df["NOMBRE COMPLETO"].astype(str) == cliente_id]

        # Quedarse solo con el registro de mayor NÚMERO RENOVACIÓN por vehículo
        cliente_data = cliente_data.sort_values("NÚMERO RENOVACIÓN", ascending=False)
        cliente_data = cliente_data.drop_duplicates(subset=["PLACA"], keep="first")
        
        if not cliente_data.empty:
            encabezado_sin_icono(
                "Datos Personales",
                nivel="h2"
            )
            datos_personales = cliente_data.iloc[0]  # Asumimos que estos campos se repiten en todas las filas
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nombre Completo:** {datos_personales['NOMBRE COMPLETO']}")
                st.write(f"**Género:** {datos_personales['GENERO']}")
                st.write(f"**Estado Civil:** {datos_personales['ESTADO CIVIL']}")
                st.write(f"**Ciudad:** {datos_personales['CIUDAD CLIENTE']}")
                st.write(f"**Fecha de Nacimiento:** {datos_personales['FECHA NACIMIENTO']}")
                st.write(f"**Correo:** {datos_personales['CORREO ELECTRÓNICO']}")
            with col2:
                st.write(f"**Dirección Oficina:** {datos_personales['DIRECCIÓN OFICINA']}")
                st.write(f"**Teléfono Oficina:** {datos_personales['TELÉFONO OFICINA']}")
                st.write(f"**Dirección Domicilio:** {datos_personales['DIRECCIÓN DOMICILIO']}")
                st.write(f"**Teléfono Domicilio:** {datos_personales['TELÉFONO DOMICILIO']}")
                
            encabezado_con_icono("iconos/carro.png", "Vehículos Asegurados", "h2")

            for idx, datos in cliente_data.iterrows():
                with st.expander(f"Vehículo {idx + 1} — {datos['MARCA']} {datos['MODELO']} ({datos['PLACA']})"):
                    col3, col4 = st.columns(2)
                    with col3:
                        st.write(f"**Marca:** {datos['MARCA']}")
                        st.write(f"**Modelo:** {datos['MODELO']}")
                        st.write(f"**Año:** {datos['AÑOCARRO']}")
                        st.write(f"**Clase (Tipo):** {datos['CLASE (TIPO)']}")
                    with col4:
                        st.write(f"**Motor:** {datos['MOTOR']}")
                        st.write(f"**Chasis:** {datos['CHASIS']}")
                        st.write(f"**Color:** {datos['COLOR']}")
                        st.write(f"**Tipo Placa:** {datos['TIPO PLACA']}")
                        st.write(f"**Placa:** {datos['PLACA']}")
            
                    st.write(f"**Accesorios:** {datos['ACCESORIOS']}")
                    st.write(f"**Valor Asegurado:** {datos['VALOR ASEGURADO']}")
                    st.write(f"**Póliza Maestra:** {datos['POLIZA MAESTRA']}")
                    st.write(f"**Número Certificado:** {datos['NÚMERO CERTIFICADO']}")
                    st.write(f"**Fecha Vigencia:** {datos['FECHA VIGENCIA']}")
                    st.write(f"**Fecha Expiración:** {datos['FECHA EXPIRACIÓN']}")
                    st.write(f"**Aseguradora:** {datos['ASEGURADORA']}")
                    st.write(f"**Plan:** {datos['PLAN']}")
            
                    aseguradora = datos["ASEGURADORA"].strip().upper()
                    tpl_path = TEMPLATES[aseguradora]  # tu mapeo a .docx
                    if st.button("Generar Certificado PDF", key=f"pdf_{datos['PLACA']}"):
                        try:
                            pdf_buf = generar_certificado_pdf_from_template(
                                asegurados_df,
                                st.session_state.usuario_actual,
                                tpl_path
                            )
                            st.download_button(
                                "Descargar Certificado (PDF)",
                                data=pdf_buf,
                                file_name=f"Certificado_{datos['PLACA']}.pdf",
                                mime="application/pdf",
                                key=f"dl_pdf_{datos['PLACA']}"
                            )
                        except Exception as e:
                            st.error(f"No se pudo generar el PDF: {e}")
    
        else:
            st.error("No se encontró información para tu cuenta.")
        
    elif tab_seleccionado == "Mis Tickets":
        encabezado_con_icono("iconos/verdatos.png", "Mis Tickets", "h1")
        df = cargar_datos()
    
        if not df.empty:
            # 🔥 Dejar solo la última versión de cada ticket
            df = df.sort_values('Fecha_Modificacion').groupby('Número').last().reset_index()
    
            # Filtrar tickets del cliente
            mis_tickets = df[df['Cliente'] == st.session_state.usuario_actual]
    
            # Filtro por estado
            estado_filtro = st.selectbox("Filtrar por estado:", ["Todos", "Abiertos", "Cerrados"])
    
            if estado_filtro == "Abiertos":
                mis_tickets = mis_tickets[mis_tickets['Estado'] != 'cerrado']
            elif estado_filtro == "Cerrados":
                mis_tickets = mis_tickets[mis_tickets['Estado'] == 'cerrado']
    
            if not mis_tickets.empty:
                # Mostrar resumen de estados
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tickets Abiertos", len(mis_tickets[mis_tickets['Estado'] != 'cerrado']['Número'].unique()))
                with col2:
                    st.metric("Tickets Cerrados", len(mis_tickets[mis_tickets['Estado'] == 'cerrado']['Número'].unique()))
                with col3:
                    ultimo_ticket = mis_tickets.iloc[-1]
                    st.metric("Último Estado", ultimo_ticket['Estado'])
    
                # Mostrar tickets con detalles
                for _, ticket in mis_tickets.iterrows():
                    with st.expander(f"Ticket #{ticket['Número']} - {ticket['Título']}"):
                        col_left, col_right = st.columns([1, 3])
    
                        with col_left:
                            estado = ticket['Estado'].lower()
                            color_map = {
                                'NUEVO': '⚫',
                                'EN PROCESO': '⚫',
                                'RESUELTO': '⚫',
                                'CERRADO': '⚫',
                                'DOCUMENTACION PENDIENTE': '⚫'
                            }
                            icono = color_map.get(estado, '⚫')
                            st.markdown(f"**Estado:** {icono} {ticket['Estado'].capitalize()}")
    
                            st.write(f"**Fecha creación:** {ticket['Fecha_Creación']}")
                            if pd.notna(ticket['Fecha_Modificacion']):
                                st.write(f"**Última actualización:** {ticket['Fecha_Modificacion']}")
    
                        with col_right:
                            st.write("**Descripción:**")
                            st.write(ticket['Descripción'])
    
                            # Mostrar imagen si existe
                            if 'Foto_URL' in ticket and ticket['Foto_URL'] and ticket['Foto_URL'] != "None":
                                try:
                                    
                                    encabezado_con_icono("iconos/ver.png", "Foto del Siniestro", "h3")

                                    st.image(ticket['Foto_URL'], caption="Imagen del siniestro", use_container_width=True)
                                except Exception as e:
                                    st.warning(f"⚠️ Error mostrando la imagen: {e}")
                            else:
                                st.info("No se adjuntó foto del siniestro.")
                            ubic = ticket.get('Ubicacion', '')
                            if isinstance(ubic, str) and ubic.startswith("http"):
                                st.markdown(
                                    f"[Ver ubicación en Google Maps]({ubic})",
                                    unsafe_allow_html=True
                                )
            else:
                st.info("No se encontraron tickets con los filtros seleccionados.")

        else:
            st.warning("No hay tickets registrados.")

    UPLOAD_DIR = "uploads"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    elif tab_seleccionado == "Nuevo Reclamo":
        encabezado_con_icono("iconos/reclamos.png", "Nuevo Reclamo", "h1")

        enviar_reclamo = False  
        cliente_id = st.session_state.usuario_actual
        cliente_data = asegurados_df[asegurados_df["NOMBRE COMPLETO"].astype(str) == cliente_id]
        
        if cliente_data.empty:
            st.error("No se encontró información del asegurado.")
            st.stop()
        
        datos = cliente_data.iloc[0]
        
        with st.form("nuevo_reclamo"):
            # Campos que el cliente debe llenar
            titulo = st.text_input("Título del Reclamo*")
            descripcion = st.text_area("Descripción detallada*")
            area = st.selectbox("Área*", ["CREDIPRIME", "GENERALES"])
            fecha_ocurrencia = st.date_input(
                "Fecha de ocurrencia*", 
                max_value=datetime.today(), 
                format="YYYY-MM-DD"
            )
    
            ciudad_ocurrencia = st.text_input("Ciudad de ocurrencia*")
            encabezado_sin_icono("Asistencia Adicional",nivel="h2")
            necesita_grua = st.selectbox("¿Necesitas grúa?", ["No", "Sí"])
            asistencia_legal = st.selectbox("¿Necesitas asistencia legal en el punto?", ["No", "Sí"])
            enviar_asistencias = st.form_submit_button("Enviar Asistencias")
            
            # Sección de ubicación automática con GPS solo si es necesario
            ubicacion_actual = ""

            if necesita_grua == "Sí" or asistencia_legal == "Sí":
                ubicacion_actual = obtener_ubicacion()
                permiso_ubicacion = st.form_submit_button("permitir ubicación")
            encabezado_sin_icono("Información sobre el Siniestro",nivel="h2")
            siniestro_vehicular = st.selectbox("¿Fue un siniestro vehicular?", ["No", "Sí"])
            enviar_vehiculos = st.form_submit_button("Enviar Foto")

            auto_detectado = False
            foto_siniestro = None
            
            if siniestro_vehicular == "Sí":
                foto_siniestro = st.camera_input("Toma una foto del siniestro (opcional)")
                if foto_siniestro is None:
                    foto_siniestro = st.file_uploader("O bien, sube una imagen", type=["jpg","jpeg","png"])
            
                # ——— Detección de auto ———
                if foto_siniestro is not None:
                    img = Image.open(foto_siniestro).convert("RGB")
                    if not contiene_auto(img):
                        st.error("No detecté un automóvil en la imagen. Por favor, sube otra foto.")
                        foto_siniestro = None
                    else:
                        st.success("Automóvil detectado correctamente 👍")
                        auto_detectado = True
            
                # ——— Segmentación y visualización sólo si el auto fue detectado ———
                if auto_detectado:
                    from ultralytics import YOLO
                    seg_model = cargar_modelo_yolo()
                    img_path = "temp_img.jpg"
                    img.save(img_path)
                
                    results = seg_model(img_path)[0]
                
                    img_np = np.array(img)
                    overlay_img = img_np.copy()
                    mask_canvas = np.zeros_like(img_np)
                
                    names = seg_model.names  # Diccionario de clases
                    overlay_final = img                    
                    if results.masks is not None and results.masks.data is not None:
                        mask_canvas = np.zeros((img.height, img.width, 3), dtype=np.uint8)
                        overlay_img = np.array(img).copy()
                    
                        for i, mask in enumerate(results.masks.data):
                            # Procesar la máscara
                            mask_resized = cv2.resize(mask.cpu().numpy(), (img.width, img.height))
                            mask_binary = (mask_resized > 0.5).astype(np.uint8) * 255
                    
                            # Añadir la máscara al canvas
                            contours, _ = cv2.findContours(mask_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            cv2.drawContours(mask_canvas, contours, -1, (255, 0, 0), -1)
                    
                            # Dibujar bounding box + clase
                            if results.boxes is not None and i < len(results.boxes):
                                box = results.boxes.xyxy[i].cpu().numpy().astype(int)
                                cls = int(results.boxes.cls[i].item())
                                label = names[cls] if cls in names else f"Clase {cls}"
                    
                                x1, y1, x2, y2 = box
                                cv2.rectangle(overlay_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(overlay_img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                            0.6, (0, 255, 0), 2, cv2.LINE_AA)
                    
                        # Convertir a PIL
                        pil_original = img.convert("RGBA")
                        pil_mask = Image.fromarray(mask_canvas).convert("RGBA")
                    
                        # Canal alfa a partir de la máscara
                        alpha = Image.fromarray((mask_canvas[:, :, 0] > 0).astype(np.uint8) * 100)
                        pil_mask.putalpha(alpha)
                    
                        # Combinar imagen original + máscara
                        overlay_masked_img = Image.alpha_composite(pil_original, pil_mask)
                    
                        # Añadir bounding boxes y etiquetas
                        overlay_final = overlay_masked_img.convert("RGB").copy()
                        draw = ImageDraw.Draw(overlay_final)
                        for i, box in enumerate(results.boxes.xyxy):
                            x1, y1, x2, y2 = box.int().tolist()
                            cls = int(results.boxes.cls[i].item())
                            label = names[cls] if cls in names else f"Clase {cls}"
                            draw.rectangle([x1, y1, x2, y2], outline="green", width=2)
                            draw.text((x1, y1 - 10), label, fill="green")
                    
                        # Mostrar
                        col1, = st.columns(1)
                        col1.image(img, caption="Imagen Capturada", use_container_width=True)
                        #col2.image(mask_canvas, caption="🟥 Máscara", use_container_width=True)
                        #col3.image(overlay_final, caption="🎯 Imagen Final", use_container_width=True)
                    else:
                        st.warning("No se detectaron daños en la imagen.")

            
            if siniestro_vehicular == "No" or auto_detectado:
                enviar_reclamo = st.form_submit_button("Enviar Reclamo")
            else:
                # Podrías opcionalmente dejar el botón gris o simplemente mostrar un aviso
                st.info("Para enviar el reclamo debes subir primero una foto con un automóvil.")
    
            if enviar_reclamo:
                if not all([titulo, descripcion, ciudad_ocurrencia, fecha_ocurrencia]):
                    st.error("❌ Por favor completa todos los campos obligatorios.")
                else:
                    # Subir imagen a S3 si existe
                    foto_url = None
                    if foto_siniestro:
                        s3 = boto3.client(
                            's3',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                            region_name='us-east-1'
                        )
                        extension = foto_siniestro.name.split('.')[-1]
                        unique_filename = f"reclamos/{str(uuid.uuid4())}.{extension}"
                        bucket_name = 'insurapp-fotos'
                        buffer = io.BytesIO()
                        # Ajusta el formato según tu extensión (jpg, png…)
                        overlay_final.save(buffer, format="JPEG")
                        buffer.seek(0)
                    
                        # Sube el buffer, en lugar de overlay_final directamente
                        s3.upload_fileobj(
                            buffer,
                            bucket_name,
                            unique_filename,
                            ExtraArgs={'ContentType': 'image/jpeg', 'ACL': 'public-read'}
                        )
                        foto_url = f"https://{bucket_name}.s3.us-east-1.amazonaws.com/{unique_filename}"
    
                    # Calcular número de ticket nuevo
                    df = cargar_datos()
                    ultimo_ticket = df['Número'].max() if not df.empty else 0
                    nuevo_numero = int(ultimo_ticket) + 1
    
                    # Crear diccionario del reclamo
                    nuevo_reclamos = {
                        'Número': nuevo_numero,
                        'Título': titulo,
                        'Área': area,
                        'Estado': 'creado por usuario',
                        'Descripción': descripcion,
                        'Fecha_Creación': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Usuario_Creación': st.session_state.usuario_actual,
                        'Fecha_Modificacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'Usuario_Modificacion': 'cliente',
                        'Tiempo_Cambio': '0d',
                        'Cliente': st.session_state.usuario_actual,
                        'Cedula': datos.get('CÉDULA'),
                        'CONCESIONARIO': datos.get('CONCESIONARIO'),
                        'ID': datos.get('ID'),
                        'ASEGURADORA': datos.get('ASEGURADORA'),
                        'CIUDAD OCURRENCIA': ciudad_ocurrencia,
                        'TALLER': "SIN TALLER DEFINIDO",
                        'MARCA': datos.get('MARCA'),
                        'MODELO': datos.get('MODELO'),
                        'AÑOCARRO': datos.get('AÑOCARRO'),
                        'PLACA': datos.get('PLACA'),
                        'fecha_ocurrencia': fecha_ocurrencia.strftime("%Y-%m-%d"),
                        'SUMA ASEGURADA': datos.get('VALOR ASEGURADO'),
                        'VALOR SINIESTRO': "",
                        'DEDUCIBLE': "",
                        'RASA': "",
                        'LIQUIDACION': "",
                        'CAUSA': "ASISTENCIA",
                        'Grua': necesita_grua,
                        'Asistencia_Legal': asistencia_legal,
                        'Ubicacion': ubicacion_actual,
                        'Foto_URL': foto_url if foto_url else None
                    }
    
                    # Serializar y guardar
                    nuevo_reclamos_serializable = {k: str(v) for k, v in nuevo_reclamos.items()}
                    sheet = cargar_worksheet_sin_cache("hoja")
                    sheet.append_row(list(nuevo_reclamos_serializable.values()))
                    st.success(f"✅ Reclamo #{nuevo_numero} creado exitosamente")
                    # --- Enviar correo de notificación ---
                    correo_destinatario = "reclamosinsuratlan@outlook.com"
                    asunto = f"Nuevo Reclamo #{nuevo_numero} de {st.session_state.usuario_actual}"
                    cuerpo = f"""
                    Se ha creado un nuevo reclamo por parte del cliente {st.session_state.usuario_actual}.
                    
                    Título: {titulo}
                    Descripción: {descripcion}
                    Ciudad de Ocurrencia: {ciudad_ocurrencia}
                    Fecha de Ocurrencia: {fecha_ocurrencia.strftime("%Y-%m-%d")}
                    Área: {area}
                    Aseguradora: {datos.get('ASEGURADORA')}
                    Placa: {datos.get('PLACA')}
                    
                    Puedes revisar el reclamo en la plataforma.
                    """
                    
                    enviar_correo_reclamo(correo_destinatario, asunto, cuerpo)
                
    elif tab_seleccionado == "Subir Archivos Adicionales a un Reclamo":
        
        encabezado_con_icono("iconos/cargardocumento.png", "Subir Archivos Adicionales a un Reclamo", "h1")

        df_tickets_cliente = cargar_datos()
        df_tickets_cliente = df_tickets_cliente[df_tickets_cliente["Cliente"] == st.session_state.usuario_actual]
        df_tickets_cliente = df_tickets_cliente.sort_values("Número")
    
        if df_tickets_cliente.empty:
            st.info("No tienes reclamos registrados para asociar archivos.")
        else:
            numero_reclamo = st.selectbox("Selecciona el número de reclamo:", df_tickets_cliente["Número"].unique())
    
            archivos = st.file_uploader(
                "Selecciona uno o más archivos (PDF o imagen)",
                type=["jpg", "jpeg", "png", "pdf"],
                accept_multiple_files=True
            )
    
            if archivos:
                bucket_name = 'insurapp-fotos'
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                    region_name='us-east-1'
                )
    
                hoja_adjuntos = cargar_worksheet_sin_cache("archivos_adjuntos")
                bucket_name = 'insurapp-fotos'
                for archivo in archivos:
                    subir_y_mostrar_archivo(archivo=archivo, bucket_name=bucket_name, numero_ticket=numero_reclamo, hoja_adjuntos=hoja_adjuntos, usuario=st.session_state.usuario_actual)
            
def modulo_cotizaciones_mauricio():
    encabezado_con_icono("iconos/dinero.png", "Gestión de Cotizaciones", "h1")

    cotizaciones_df = cargar_df_sin_cache("cotizaciones")
    # 🔥 Aquí agregas la recarga automática
    if st.session_state.get("recargar_cotizaciones"):
        cotizaciones_df = cargar_df_sin_cache("cotizaciones")
        st.session_state.recargar_cotizaciones = False

    if cotizaciones_df.empty:
        st.info("No hay cotizaciones registradas.")
        return

    # Asegurarse que la columna de estado existe
    if 'Estado' not in cotizaciones_df.columns:
        cotizaciones_df['Estado'] = 'NO COTIZADA'

    estados = ["NO COTIZADA", "EN PROCESO", "COTIZADA", "ACEPTADA", "RECHAZADA"]
    

    def actualizar_estado(index, nuevo_estado):
        hoja_cotizaciones = cargar_worksheet_sin_cache("cotizaciones")
        hoja_cotizaciones.update_cell(index + 2, cotizaciones_df.columns.get_loc('Estado') + 1, nuevo_estado)
        st.success(f"Cotización actualizada a '{nuevo_estado}'.")
        time.sleep(1)
        st.session_state.recargar_cotizaciones = True
        st.rerun()


    # Sección 1: Nuevas Cotizaciones
    encabezado_sin_icono("Pendientes", "h2")
    nuevas = cotizaciones_df[cotizaciones_df['Estado'] == 'NO COTIZADA']
    for idx, row in nuevas.iterrows():
        with st.expander(f"{row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']}"):
            st.write(f"**Correo:** {row['Correo']}")
            st.write(f"**Teléfono:** {row['Teléfono']}")
            if st.button(f"Tomar Cotización #{idx}", key=f"tomar_{idx}"):
                actualizar_estado(idx, "EN PROCESO")

    # Sección 2: Cotizaciones en Proceso
    encabezado_sin_icono("En Proceso", "h2")
    en_proceso = cotizaciones_df[cotizaciones_df['Estado'] == 'EN PROCESO']
    for idx, row in en_proceso.iterrows():
        with st.expander(f"{row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']}"):
            st.write(f"**Correo:** {row['Correo']}")
            st.write(f"**Teléfono:** {row['Teléfono']}")
            opcion = st.selectbox(f"Actualizar estado Cotización #{idx}", ["COTIZADA", "RECHAZADA"], key=f"proceso_{idx}")
            if st.button(f"Actualizar Estado #{idx}", key=f"btn_proceso_{idx}"):
                actualizar_estado(idx, opcion)

    # Sección 3: Cotizaciones Cotizadas
    encabezado_sin_icono("Realizadas", "h2")
    cotizadas = cotizaciones_df[cotizaciones_df['Estado'] == 'COTIZADA']
    for idx, row in cotizadas.iterrows():
        with st.expander(f"{row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']}"):
            st.write(f"**Correo:** {row['Correo']}")
            st.write(f"**Teléfono:** {row['Teléfono']}")
            opcion = st.selectbox(f"Actualizar estado Cotización #{idx}", ["ACEPTADA", "RECHAZADA"], key=f"cotizada_{idx}")
            if st.button(f"Actualizar Estado #{idx}", key=f"btn_cotizada_{idx}"):
                actualizar_estado(idx, opcion)

    # Sección 4: Cotizaciones Finalizadas
    encabezado_sin_icono("Finalizadas", "h2")
    finalizadas = cotizaciones_df[cotizaciones_df['Estado'].isin(['ACEPTADA', 'RECHAZADA'])]
    for idx, row in finalizadas.iterrows():
        with st.expander(f"{row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']} - {row['Estado'].capitalize()}"):
            st.write(f"**Correo:** {row['Correo']}")
            st.write(f"**Teléfono:** {row['Teléfono']}")
            st.info(f"Estado final: {row['Estado'].capitalize()}")

def visualizar_ticket_modificar(ticket=None):
    """
    Muestra un expander con todos los datos del ticket.
    Si no recibe parámetro, usa st.session_state.ticket_actual.
    """
    if ticket is None:
        ticket = st.session_state.get("ticket_actual")
    if not ticket:
        st.warning("No hay ticket seleccionado.")
        return

    header = f"Ticket #{ticket['Número']} – {ticket['Título']}"
    with st.expander(header, expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            icons = {
                'NUEVO': '⚫', 'EN PROCESO': '⚫', 'RESUELTO': '⚫',
                'cerrado': '⚫', 'DOCUMENTACION PENDIENTE': '⚫'
            }
            est = ticket['Estado'].lower()
            st.markdown(f"**Estado:** {icons.get(est,'⚫')} {ticket['Estado'].capitalize()}")
            st.write(f"**Cliente:** {ticket.get('Cliente','Desconocido')}")
            st.write(f"**Área:** {ticket.get('Área','')}")
            st.write(f"**Fecha creación:** {ticket.get('Fecha_Creación','')}")
            st.write(f"**Última actualización:** {ticket.get('Fecha_Modificacion','')}")
            if ticket.get('Tiempo_Cambio'):
                st.write(f"**Tiempo Cambio:** {ticket['Tiempo_Cambio']}")
        with col2:
            st.write("**Descripción:**")
            st.write(ticket.get('Descripción',''))
            # Ubicación
            st.write("**Ubicación:**")
            ubic = ticket.get('Ubicacion', '')
            if isinstance(ubic, str) and ubic.startswith("http"):
                st.markdown(f"[Ver en Google Maps]({ubic})", unsafe_allow_html=True)

            # Foto del siniestro
            url = ticket.get('Foto_URL', '')
            if isinstance(url, str) and url.startswith("http"):
                encabezado_con_icono("iconos/ver.png","Foto", "h2")
                st.image(url, caption="Imagen del siniestro", use_container_width=True)
                st.markdown(f"[Ver imagen en nueva pestaña]({url})", unsafe_allow_html=True)
            else:
                st.info("No se adjuntó foto del siniestro.")

def mostrar_conversaciones_bot():
    df_conversaciones = cargar_df("tickets_bot")
    df_conversaciones["fecha"] = pd.to_datetime(df_conversaciones["fecha"], errors="coerce")

    # Clasificación del sentimiento
    def clasificar_sentimiento(score):
        if score <= -0.5:
            return "Muy negativo"
        elif -0.5 < score <= -0.2:
            return "Negativo"
        elif -0.2 < score < 0:
            return "Ligeramente negativo"
        elif score == 0:
            return "Neutral"
        else:
            return "Positivo"

    colores = {
        "Muy negativo": "#C62828",
        "Negativo": "#EF5350",
        "Ligeramente negativo": "#FFCDD2",
        "Neutral": "#9E9E9E",
        "Positivo": "#BDBDBD"
    }

    df_conversaciones["categoria"] = df_conversaciones["sentimiento"].apply(clasificar_sentimiento)

    # Filtro por fecha
    fecha_inicio = st.date_input("Desde", df_conversaciones['fecha'].min().date())
    fecha_fin = st.date_input("Hasta", df_conversaciones['fecha'].max().date())
    df_filtrado = df_conversaciones[
        (df_conversaciones['fecha'] >= pd.to_datetime(fecha_inicio)) &
        (df_conversaciones['fecha'] <= pd.to_datetime(fecha_fin))
    ]

    if df_filtrado.empty:
        st.warning("⚠️ No hay conversaciones en el rango de fechas seleccionado.")
        return

    # Gráfico de pastel
    encabezado_sin_icono("Distribución de Sentimientos", "h2")

    conteo = df_filtrado["categoria"].value_counts().reindex(colores.keys(), fill_value=0)
    conteo = conteo[conteo > 0]  # <- Aquí se filtran las categorías vacías

    if conteo.empty:
        st.warning("⚠️ No hay datos de sentimiento disponibles para graficar.")
    else:
        fig, ax = plt.subplots(figsize=(4, 4))  # más espacio visual
        ax.pie(
            conteo,
            labels=conteo.index,
            autopct='%1.1f%%',
            startangle=90,
            colors=[colores[c] for c in conteo.index]
        )
        ax.axis("equal")
        st.pyplot(fig)

    # Tabla detallada
    encabezado_sin_icono("Detalle de Conversaciones", "h2")
    df_mostrar = df_filtrado[['fecha', 'numero', 'conversacion', 'categoria']]\
    .sort_values(by="fecha", ascending=False)
    render_tabla_html(df_mostrar,height=250)

    # Descarga CSV
    csv = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button("Descargar CSV", data=csv, file_name="conversaciones_bot.csv", mime="text/csv")



# Portal de Administración (Usuarios)
def portal_administracion():
    with st_fixed_container(mode="fixed", position="top", transparent=False, key="header_admin"):
        col1, col2, col3 = st.columns([1, 6, 1], gap="small")
        with col1:
            b64 = base64.b64encode(Path("images/atlantida_logo.jpg").read_bytes()).decode()
            st.markdown(
                f"<img src='data:image/jpeg;base64,{b64}' "
                "style='height:60px; margin:10px;'/>",
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                """
                <h5 style='margin:0; color:#7F7F7F; 
                    font-family:Calibri,sans-serif;'>
                  Portal Administrativo
                </h5>
                """,
                unsafe_allow_html=True
            )
        with col3:
            st.write("")

    # 3) Espaciador de exactamente la altura del header (80px)
    st.markdown("<div style='height:120px;'></div>", unsafe_allow_html=True)

    st.sidebar.title("Menú Admin")
    opciones = [
        "Inicio", 
        "Dashboard",
        "Polizas y Asegurados",
        "Gestión de Reclamos y Tickets", 
        "Ver Reclamos", 
        "Analisis de Chatbot",
        "Descargar Datos"
    ]   
    
    if st.session_state.usuario_actual == "mauriciodavila":
        opciones.insert(2, "Gestión de Cotizaciones")
    
    opcion = st.sidebar.radio("Opciones", opciones)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.mostrar_login = False
        st.success("Sesión cerrada exitosamente")
        time.sleep(1)
        st.rerun()

    if opcion == "Inicio":
        encabezado_con_icono("iconos/home.png", "Panel de Administración", "h1")
        st.markdown("""
        **Bienvenido al panel de administración**
        Selecciona una opción del menú lateral para comenzar.
        """)
        
    elif opcion == "Dashboard":
        df_pagados, df_pendientes, df_asegurados = cargar_datos_dashboard_desde_sheets()
        mostrar_dashboard_analisis(df_pagados, df_pendientes, df_asegurados)
        if st.button("Recargar datos (limpiar caché)"):
            st.cache_data.clear()
   
    elif opcion == "Polizas y Asegurados":
        gestionar_asegurados()

    elif opcion == "Gestión de Reclamos y Tickets":
        manejar_tickets()
        

    elif opcion == "Ver Reclamos":

        encabezado_con_icono("iconos/reclamos.png", "Reclamos", "h1")
        visualizar_tickets()
    
    elif opcion == "Analisis de Chatbot":
        encabezado_con_icono("iconos/chat.png", "Analisis e Historial del ChatBot", "h1")
        mostrar_conversaciones_bot()

    elif opcion == "Descargar Datos":
        encabezado_con_icono("iconos/carpeta.png", "Descargar Datos", "h1")
        descargar_tickets()
        
    elif opcion == "Gestión de Cotizaciones" and st.session_state.usuario_actual == "mauriciodavila":
        modulo_cotizaciones_mauricio()
        


def procesar_tiempos_estado(tiempos_cambio):
    """
    Procesa una lista de registros de tiempo de cambio de estado y devuelve un DataFrame
    con el tiempo acumulado por estado de origen.
    
    Args:
        tiempos_cambio (list): Lista de strings con formato "Xd (estado1 -> estado2)" 
        
    Returns:
        pd.DataFrame: DataFrame con columnas ['Estado', 'Tiempo_Cambio']
    """
    tiempos_estado = {}
    
    for entry in tiempos_cambio:
        if '(' in entry and '->' in entry:
            # Separar componentes
            time_part, transition_part = entry.split(' (', 1)
            time_str = time_part.replace('d', '').strip()
            time = int(time_str) if time_str.isdigit() else 0
            
            # Extraer estado de origen
            source_state = transition_part.split('->')[0].split(')')[0].strip()
            
            # Acumular tiempo
            tiempos_estado[source_state] = tiempos_estado.get(source_state, 0) + time
            
    return pd.DataFrame(list(tiempos_estado.items()), columns=['Estado', 'Tiempo_Cambio'])

# Función para visualizar tickets
def visualizar_tickets():
    df = cargar_datos()
    if not df.empty:
        # 🔥 Muy importante: Solo dejar la última versión de cada ticket
        df = df.sort_values('Fecha_Modificacion').groupby('Número').last().reset_index()

        # Mostrar métricas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Tickets", df['Número'].nunique())
        with col2:
            st.metric("Tickets Abiertos", df[df['Estado'] != 'cerrado']['Número'].nunique())
        with col3:
            tickets_cerrados = df[df['Estado'] == 'cerrado']
            if 'Tiempo_Cambio' in tickets_cerrados.columns:
                try:
                    dias = (tickets_cerrados['Tiempo_Cambio']
                            .astype(str)
                            .str.extract(r'(\d+)d', expand=False)
                            .dropna()
                            .astype(float))
                    tiempo_promedio = dias.mean() if not dias.empty else None
                except Exception as e:
                    tiempo_promedio = None
                    st.error(f"Error al calcular el tiempo de resolución: {e}")
            else:
                tiempo_promedio = None
            st.metric("Tiempo Resolución Promedio", f"{tiempo_promedio:.1f} días" if tiempo_promedio is not None else "N/A")
                        
        encabezado_sin_icono("Filtros",nivel="h2")
        # Evitar errores si columnas están vacías
        areas = df['Área'].dropna().unique().tolist()
        estados = df['Estado'].dropna().unique().tolist()
        clientes = df['Cliente'].dropna().unique().tolist()
        numeros = df['Número'].dropna().unique().tolist()
        
        cola, colb = st.columns(2)
        with cola:
            area = st.selectbox("Área", ["Todas"] + sorted(areas))
            estado = st.selectbox("Estado", ["Todos"] + sorted(estados))
        with colb:
            nombre = st.selectbox("Cliente", ["Todos"] + sorted(clientes), key="filtro_cliente")
            numero = st.selectbox("Número de Reclamo", ["Todos"] + sorted(map(str, numeros)), key="filtro_numero")
        
        # Aplicar filtros
        if area != "Todas":
            df = df[df['Área'] == area]
        if estado != "Todos":
            df = df[df['Estado'] == estado]
        if nombre != "Todos":
            df = df[df['Cliente'] == nombre]
        if numero != "Todos":
            df = df[df['Número'] == int(numero)]

        # Mostrar cada ticket
        for _, ticket in df.iterrows():
            numero  = ticket['Número']
            titulo  = ticket['Título']
            cliente = ticket.get('Cliente', 'Desconocido')
            header  = f"Ticket #{numero} – {titulo}"
            with st.expander(header):
                col_left, col_right = st.columns([1, 3])

                with col_left:
                    # Estado
                    estado_ticket = ticket['Estado'].lower()
                    color_map = {
                        'NUEVO': '⚫',
                        'EN PROCESO': '⚫',
                        'RESUELTO': '⚫',
                        'cerrado': '⚫',
                        'DOCUMENTACION PENDIENTE': '⚫'
                    }
                    icono = color_map.get(estado_ticket, '⚫')
                    st.markdown(f"**Estado:** {icono} {ticket['Estado'].capitalize()}")
                    
                    # Cliente justo debajo del estado
                    st.write(f"**Cliente:** {cliente}")

                    # Fechas
                    st.write(f"**Fecha creación:** {ticket['Fecha_Creación']}")
                    if pd.notna(ticket['Fecha_Modificacion']):
                        st.write(f"**Última actualización:** {ticket['Fecha_Modificacion']}")

                with col_right:
                    st.write("**Descripción:**")
                    st.write(ticket['Descripción'])

                    # Ubicación
                    st.write("**Ubicación:**")
                    ubic = ticket.get('Ubicacion', '')
                    if isinstance(ubic, str) and ubic.startswith("http"):
                        st.markdown(f"[Ver en Google Maps]({ubic})", unsafe_allow_html=True)

                    # Foto del siniestro
                    url = ticket.get('Foto_URL', '')
                    if isinstance(url, str) and url.startswith("http"):
                        st.subheader("Foto del Siniestro")
                        st.image(url, caption="Imagen del siniestro", use_container_width=True)
                        st.markdown(f"[Ver imagen en nueva pestaña]({url})", unsafe_allow_html=True)
                    else:
                        st.info("No se adjuntó foto del siniestro.")
# Versión cacheada para uso general
@st.cache_data(ttl=60)
def _cargar_tickets():
    data = cargar_df("hoja")
    return data

# Función pública para permitir limpieza de caché
def cargar_tickets(clear_cache=False):
    if clear_cache:
        st.cache_data.clear()
    return _cargar_tickets()
    
def convertir_a_float(valor):
    try:
        numero = pd.to_numeric(valor, errors='coerce')
        if pd.isna(numero):
            return 0.0
        return round(float(numero), 2)
    except:
        return 0.0   
        
def actualizar_bases_reclamos(todos_df, spreadsheet_sin_cache):
    
    todos_df["fecha_ocurrencia"] = pd.to_datetime(todos_df["fecha_ocurrencia"], errors="coerce")
    todos_df["Fecha_Modificacion"] = pd.to_datetime(todos_df["Fecha_Modificacion"], errors="coerce")
    todos_df["MES"] = todos_df["fecha_ocurrencia"].dt.month.fillna(0).astype(int)

    # Tomar el último registro por número de ticket
    todos_df_ultimos = todos_df.sort_values("Fecha_Modificacion").drop_duplicates(subset=["Número"], keep="last")

    # Leer y conservar histórico de pagados y pendientes
    pagados_ws = cargar_worksheet_sin_cache("pagados")
    pagados_hist = cargar_df_sin_cache("pagados")

    pendientes_ws = cargar_worksheet_sin_cache("pendientes")
    pendientes_hist = cargar_df_sin_cache("pendientes")

    # Convertir campos de fecha si existen
    #Fecha Siniestro
    if not pagados_hist.empty and "FECHA SINIESTRO" in pagados_hist.columns:
        pagados_hist["FECHA SINIESTRO"] = pd.to_datetime(pagados_hist["FECHA SINIESTRO"], errors="coerce")
    if not pendientes_hist.empty and "FECHA DE SINIESTRO" in pendientes_hist.columns:
        pendientes_hist["FECHA DE SINIESTRO"] = pd.to_datetime(pendientes_hist["FECHA DE SINIESTRO"], errors="coerce")
    #Fecha Modificacion
    if not pagados_hist.empty and "FECHA MODIFICACION" in pagados_hist.columns:
        pagados_hist["FECHA MODIFICACION"] = pd.to_datetime(pagados_hist["FECHA MODIFICACION"], errors="coerce")
    
    if not pendientes_hist.empty and "FECHA MODIFICACION" in pendientes_hist.columns:
        pendientes_hist["FECHA MODIFICACION"] = pd.to_datetime(pendientes_hist["FECHA MODIFICACION"], errors="coerce")

    cerrados_df = todos_df_ultimos[todos_df_ultimos["Estado"].str.lower() == "cerrado"]
    pendientes_df = todos_df_ultimos[todos_df_ultimos["Estado"].str.lower() != "cerrado"]

    # === PAGADOS ===
    nuevos_pagados = []
    for _, row in cerrados_df.iterrows():
        fila = {
            "COMPAÑÍA": row.get("ASEGURADORA", ""),
            "CANAL": row.get("Área", ""),
            "CLIENTE": row.get("Cliente", ""),
            "MARCA": row.get("MARCA", ""),
            "MODELO": row.get("MODELO", ""),
            "AÑO": row.get("AÑO", ""),
            "FECHA SINIESTRO": row.get("fecha_ocurrencia", ""),
            "FECHA MODIFICACION" : row.get("Fecha_Modificacion", ""),
            "MES SINIESTRO": row.get("fecha_ocurrencia", pd.NaT).strftime("%B") if pd.notnull(row.get("fecha_ocurrencia", pd.NaT)) else "",
            "EVENTO": row.get("CAUSA", ""),
            "VALOR RECLAMO": convertir_a_float(row.get("VALOR SINIESTRO", 0)),
            "DEDUCIBLE": convertir_a_float(row.get("DEDUCIBLE", 0)),
            "LIQUIDADO": convertir_a_float(row.get("LIQUIDACION", 0)),
            "TALLER DE REPARACION": row.get("TALLER", ""),
            "CIUDAD OCURRENCIA": row.get("CIUDAD OCURRENCIA", ""),
            "CONCESIONARIO SISTEMA": row.get("CONCESIONARIO", ""),
            "BASE": int(row.get("fecha_ocurrencia").year) if pd.notnull(row.get("fecha_ocurrencia")) else None,
            "ESTADO": row.get("Estado", ""),
            "MES": row.get("MES", "")
        }
        nuevos_pagados.append(fila)

    df_pagados_final = pd.concat([pagados_hist, pd.DataFrame(nuevos_pagados)]).sort_values("FECHA MODIFICACION").drop_duplicates(subset=["CLIENTE", "FECHA SINIESTRO"], keep="last")
    pagados_ws.clear()
    pagados_ws.update(
        [df_pagados_final.columns.tolist()] + df_pagados_final.astype(str).values.tolist()
    )

    # === PENDIENTES ===
    nuevos_pendientes = []
    for _, row in pendientes_df.iterrows():
        fila = {
            "CIA. DE SEGUROS": row.get("ASEGURADORA", ""),
            "CLIENTE": row.get("Cliente", ""),
            "CIUDAD OCURRENCIA": row.get("CIUDAD OCURRENCIA", ""),
            "MARCA": row.get("MARCA", ""),
            "MODELO": row.get("MODELO", ""),
            "AÑO": row.get("AÑO", ""),
            "PLACA": row.get("PLACA", ""),
            "FECHA DE SINIESTRO": row.get("fecha_ocurrencia", ""),
            "FECHA MODIFICACION": row.get("Fecha_Modificacion", ""),
            "SUMA ASEGURADA": convertir_a_float(row.get("SUMA ASEGURADA", 0)),
            "VALOR SINIESTRO": convertir_a_float(row.get("VALOR SINIESTRO", 0)),
            "DEDUCIBLE": convertir_a_float(row.get("DEDUCIBLE", 0)),
            "RASA": convertir_a_float(row.get("RASA", 0)),
            "LIQUIDACION": convertir_a_float(row.get("LIQUIDACION", 0)),
            "TALLER DE REPARACION": row.get("TALLER", ""),
            "CAUSA": row.get("CAUSA", ""),
            "MES": row.get("MES", ""),
            "ESTADO ACTUAL": row.get("Estado", ""),
            "BASE": row.get("BASE", ""),
            "ESTADO": row.get("Estado", "")
        }
        nuevos_pendientes.append(fila)

    df_pendientes_final = pd.concat([pendientes_hist, pd.DataFrame(nuevos_pendientes)]).sort_values("FECHA MODIFICACION").drop_duplicates(subset=["CLIENTE", "FECHA DE SINIESTRO"], keep="last")
    pendientes_ws.clear()
    pendientes_ws.update(
        [df_pendientes_final.columns.tolist()] + df_pendientes_final.astype(str).values.tolist()
    )
        
def manejar_tickets():
    # ✅ Nuevo bloque más limpio y eficiente
    df = cargar_tickets(clear_cache=st.session_state.get("recargar_tickets", False))
    st.session_state.recargar_tickets = False
    with st.container():
        st.markdown("<hr style='border:1px solid #7F7F7F; margin-top:0rem;'>", unsafe_allow_html=True)
        # fondo blanco con borde visual simulado como encabezado
        st.markdown(
            """
            <div style="border:1px solid #FFFFFF; border-radius:10px; padding:20px; background-color:#FFFFFF;">
            """,
            unsafe_allow_html=True
        )
        encabezado_con_icono("iconos/informe.png", "Gestión de Reclamos y Tickets", "h1")
    
        # 3) Radio controlada por session_state
        opcion_ticket = st.radio(
            "Seleccione una acción:",
            ["Ver reclamos en cola", "Registrar nuevo reclamo", "Modificar reclamo existente", "Subir documentación a reclamo"]
        )
        # Cierre visual del bloque
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<hr style='border:1px solid #7F7F7F; margin-top:1rem;'>", unsafe_allow_html=True)
    
    if opcion_ticket == "Ver reclamos en cola":
        encabezado_sin_icono("Ver reclamos en cola", "h2")
        if df.empty:
            st.warning("No se encontraron reclamos")
            return

        ultimos = (df.sort_values('Fecha_Modificacion')
                     .groupby('Número')
                     .last()
                     .reset_index())
        cola = ultimos[(ultimos['Usuario_Modificacion'] == 'cliente') &
                      (ultimos['Estado'] != 'cerrado')]

        if cola.empty:
            st.info("No hay reclamos pendientes de clientes")
            return

        st.metric("Reclamos Pendientes", len(cola))
        df_tabla = cola[['Número','Título','Cliente','Estado','Fecha_Modificacion']]\
            .sort_values('Fecha_Modificacion', ascending=False)
        render_tabla_html(df_tabla,height=250)

        # 1) Selección
        selected = st.number_input(
            "Seleccionar Número de Ticket para ver detalles:",
            min_value=int(cola['Número'].min()),
            max_value=int(cola['Número'].max()),
            step=1
        )

        if selected in cola['Número'].values:
            # 2) Previsualizar antes de tomar
            ticket = cola[cola['Número']==selected].iloc[0].to_dict()
            visualizar_ticket_modificar(ticket)

            # 3) Botón de tomar
            if st.button(f"Tomar Ticket #{selected}"):
                st.session_state.ticket_actual = ticket
                st.session_state.opcion_ticket = "Modificar reclamo existente"
                st.success(f"✅ Reclamo #{selected} asignado para gestión") 
        else:
            st.info("Selecciona un número válido de la tabla anterior")
    elif opcion_ticket == "Registrar nuevo reclamo":
        with st.form("nuevo_reclamos"):
            encabezado_con_icono("iconos/reclamos.png","Crear nuevo reclamo con datos del asegurado", "h2")
            # Paso 1: Buscar cliente por cédula o póliza
            asegurados_data = asegurados_df.copy()
            tipo_busqueda = st.radio("Buscar por:", ["Cédula", "Número de Póliza"])
            if tipo_busqueda == "Cédula":
                cedula = st.text_input("Ingrese el número:")
                coincidencias = asegurados_data[asegurados_data["NÚMERO IDENTIFICACIÓN"].astype(str) == cedula]
            else:
                poliza = st.text_input("Ingrese número de póliza:")
                coincidencias = asegurados_data[asegurados_data["NÚMERO PÓLIZA VEHÍCULOS"].astype(str) == poliza]
                # Validación de la columna
            buscar = st.form_submit_button("Buscar")
        if buscar:
            if not coincidencias.empty:
                st.session_state.coincidencias = coincidencias
                st.session_state.busqueda_exitosa = True
            else:
                st.session_state.busqueda_exitosa = False
                st.warning("⚠️ No se encontraron coincidencias.")
        
        # Paso 2: Mostrar formulario solo si hubo coincidencia
        if st.session_state.get("busqueda_exitosa"):
            coincidencias = st.session_state.coincidencias
        
            with st.form("form_registro_reclamo"):
                vehiculo = st.selectbox(
                    "Selecciona el vehículo asegurado:",
                    coincidencias.apply(lambda row: f"{row['MARCA']} {row['MODELO']} ({row['PLACA']})", axis=1)
                )
                vehiculo_info = coincidencias.iloc[
                    list(coincidencias.apply(lambda row: f"{row['MARCA']} {row['MODELO']} ({row['PLACA']})", axis=1)).index(vehiculo)
                ]
        
                # Relleno automático
                cliente = vehiculo_info["NOMBRE COMPLETO"]
                cedula = vehiculo_info["NÚMERO IDENTIFICACIÓN"]
                concesionario = vehiculo_info.get("CONCESIONARIO", "")
                id_liderseg = vehiculo_info.get("ID", "")
                aseguradora = vehiculo_info["ASEGURADORA"]
                ciudad = vehiculo_info["CIUDAD CLIENTE"]
                marca = vehiculo_info["MARCA"]
                modelo = vehiculo_info["MODELO"]
                anio = vehiculo_info["AÑOCARRO"]
                placa = vehiculo_info["PLACA"]
                suma_asegurada = vehiculo_info["VALOR ASEGURADO"]
        
                # Formulario restante
                titulo = st.text_input("Título del Reclamo*")
                area = st.selectbox("Área*", ["CREDIPRIME", "GENERALES"])
                estado = st.selectbox("Estado*", ["INICIAL","INSPECCION","DOCUMENTACION PENDIENTE" ,"DOCUMENTACION ENVIADA","EN LIQUIDACION","POR INGRESO VEHICULO A TALLER","POR PROFORMA","EN IMPORTACION","EN REPARACION"])
                descripcion = st.text_area("Descripción detallada*")
                ciudad_ocurrencia = st.text_input("Ciudad donde ocurrió el siniestro*")
                fecha_ocurrencia = st.date_input("Fecha de ocurrencia")
                causa = st.selectbox("Causa*", ["ROBO TOTAL", "CHOQUE PARCIAL + RC", "PERDIDA TOTAL", "DAÑOS MALICIOSOS", "CHOQUE PARCIAL", "ROBO PARCIAL", "ROTURA DE PARABRISAS", "SOLO RC", "DESGRAVAMEN","ASISTENCIA"])
                talleres_df = cargar_df_sin_cache("talleres")  # o como corresponda según tu sistema
                talleres_unicos = sorted(talleres_df["Taller"].dropna().unique().tolist())
                taller_opcion = st.selectbox("Selecciona el taller de reparación*", talleres_unicos + ["Otro..."])
        
                if taller_opcion == "Otro...":
                    nuevo_taller = st.text_input("Nombre del nuevo taller")
                    taller_seleccionado = nuevo_taller
                else:
                    taller_seleccionado = taller_opcion
        
                necesita_grua = st.selectbox("¿Necesita grúa?", ["No", "Sí"])
                asistencia_legal = st.selectbox("¿Requiere asistencia legal?", ["No", "Sí"])
        
                guardar = st.form_submit_button("Guardar Reclamo")
                if guardar:
                    fecha_modificacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ultimo_ticket = df["Número"].max() if not df.empty else 0
                    nuevo_numero = int(ultimo_ticket) + 1
        
                    nuevo_reclamos = {
                        'Número': nuevo_numero,
                        'Título': titulo,
                        'Área': area,
                        'Estado': estado,
                        'Descripción': descripcion,
                        'Fecha_Creación': fecha_modificacion,
                        'Usuario_Creación': st.session_state.usuario_actual,
                        'Fecha_Modificacion': fecha_modificacion,
                        'Usuario_Modificacion': st.session_state.usuario_actual,
                        'Tiempo_Cambio': '0d',
                        'Cliente': cliente,
                        'Cedula': cedula,
                        'CONCESIONARIO': concesionario,
                        'ID_LIDERSEG': id_liderseg,
                        'ASEGURADORA': aseguradora,
                        'CIUDAD OCURRENCIA': ciudad_ocurrencia,
                        'TALLER': taller_seleccionado,
                        'MARCA': marca,
                        'MODELO': modelo,
                        'AÑOCARRO': anio,
                        'PLACA': placa,
                        'fecha_ocurrencia': fecha_ocurrencia.strftime("%Y-%m-%d"),
                        'SUMA ASEGURADA': suma_asegurada,
                        'VALOR SINIESTRO': None,
                        'DEDUCIBLE': None,
                        'RASA': None,
                        'LIQUIDACION': None,
                        'CAUSA': causa,
                        'Necesita Grua': necesita_grua,
                        'Asistencia Legal': asistencia_legal,
                        'Ubicacion': None,
                        'Foto_URL': None
                    }
                    sheet = cargar_worksheet_sin_cache("hoja")
                    sheet.append_row([str(v) for v in nuevo_reclamos.values()])
                    st.success(f"✅ Reclamo #{nuevo_numero} guardado exitosamente.")
                    pendientes_ws =cargar_worksheet("pendientes")
                    pagados_ws = cargar_worksheet("pagados")
                    todos_df =cargar_df_sin_cache("hoja")
                    actualizar_bases_reclamos(todos_df, spreadsheet_sin_cache)
                    del st.session_state.coincidencias
                    del st.session_state.busqueda_exitosa
                    st.rerun()


    elif opcion_ticket == "Modificar reclamo existente":
        tickets_df = cargar_tickets()
        if tickets_df.empty:
            st.warning("No hay reclamos disponibles.")
            st.stop()
        
        busqueda_tipo = st.radio("Buscar por:", ["Número de Reclamo", "Nombre del Cliente"])
        
        ticket_id = None
        ticket_seleccionado = None
        
        if busqueda_tipo == "Número de Reclamo":
            ticket_ids = tickets_df["Número"].unique().tolist()
            ticket_id = st.selectbox("Selecciona el número de reclamo:", sorted(ticket_ids), key="modificar_por_numero")
            ticket_seleccionado = tickets_df[tickets_df["Número"] == ticket_id].iloc[-1]
        
        else:
            nombres = tickets_df["Cliente"].dropna().unique().tolist()
            nombre_cliente = st.selectbox("Selecciona el cliente:", sorted(nombres), key="modificar_por_cliente")
            tickets_cliente = tickets_df[(tickets_df["Cliente"] == nombre_cliente) & (tickets_df["Estado"] != "cerrado")]
        
            if tickets_cliente.empty:
                st.info("Este cliente no tiene reclamos abiertos.")
                st.stop()
        
            ticket_ids = tickets_cliente["Número"].unique().tolist()
            ticket_id = st.selectbox("Selecciona el número de reclamo del cliente:", sorted(ticket_ids), key="modificar_ticket_cliente")
            ticket_seleccionado = tickets_cliente[tickets_cliente["Número"] == ticket_id].iloc[-1]
        
        # Validación final
        if ticket_seleccionado is not None:
            if ticket_seleccionado['Estado'] == "cerrado":
                st.error("❌ No se puede modificar un reclamo cerrado.")
            else:
                st.success(f"✅ Reclamo #{ticket_id} seleccionado para modificación")
                st.session_state.ticket_actual = ticket_seleccionado.to_dict()
        
        if 'ticket_actual' in st.session_state:
            
            encabezado_con_icono(
                "iconos/editar.png",
                f"Modificando Reclamo #{st.session_state.ticket_actual['Número']}",
                nivel="h2"
            )
        
            # Paso 1: Selección de estado y descripción (dentro del formulario)
            with st.form("seleccion_estado_form"):
                nuevo_estado = st.selectbox(
                    "Nuevo estado:",
                    ["INICIAL", "INSPECCION","DOCUMENTACION PENDIENTE" ,"DOCUMENTACION ENVIADA","EN LIQUIDACION","POR INGRESO VEHICULO A TALLER","POR PROFORMA","EN IMPORTACION","EN REPARACION","cerrado"],
                    index=["creado por usuario","INICIAL", "INSPECCION","DOCUMENTACION PENDIENTE" ,"DOCUMENTACION ENVIADA","EN LIQUIDACION","POR INGRESO VEHICULO A TALLER","POR PROFORMA","EN IMPORTACION","EN REPARACION", "cerrado"].index(
                        st.session_state.ticket_actual['Estado']
                    )
                )
        
                nueva_descripcion = st.text_area(
                    "Descripción actualizada:",
                    value=st.session_state.ticket_actual['Descripción']
                )
        
                confirmar_estado = st.form_submit_button("Seleccionar estado")
        
            if confirmar_estado:
                st.session_state.estado_seleccionado = nuevo_estado
                st.session_state.descripcion_modificada = nueva_descripcion
        
            # Paso 2: Mostrar campos adicionales si ya se seleccionó el estado
            if st.session_state.get("estado_seleccionado"):
                ticket_actual = st.session_state.ticket_actual  # ✅ CORRECCIÓN AQUI

                estado_final = st.session_state.estado_seleccionado
                descripcion_final = st.session_state.descripcion_modificada
                lista_causas = ["ROBO TOTAL", "CHOQUE PARCIAL + RC","PERDIDA TOTAL","DAÑOS MALICIOSOS","CHOQUE PARCIAL","ROBO PARCIAL","ROTURA DE PARABRISAS","SOLO RC","DESGRAVAMEN","CHOQUE PARCIAL","PERDIDA TOTAL","ASISTENCIA"]
                causa_actual = ticket_actual.get("CAUSA", lista_causas[0])  # ✅ PREVIENE ERROR SI NO EXISTE
                causa = st.selectbox("Causa del siniestro:", lista_causas, index=lista_causas.index(causa_actual))
                talleres_df=cargar_df("talleres")

                
                if "Taller" in talleres_df.columns:
                    talleres_unicos = sorted(talleres_df["Taller"].dropna().unique().tolist())
                else:
                    st.error("❌ No se encontró la columna 'Taller' en la hoja 'talleres'")
                    st.stop()
                
                # === Selección del taller de reparación ===
                taller_opcion = st.selectbox("Taller de reparación:", talleres_unicos + ["Otro..."], 
                                             index=talleres_unicos.index(ticket_actual.get("TALLER")) if ticket_actual.get("TALLER") in talleres_unicos else len(talleres_unicos))
                
                if taller_opcion == "Otro...":
                    nuevo_taller = st.text_input("Escribe el nombre del nuevo taller")
                    if nuevo_taller and nuevo_taller not in talleres_unicos:
                        if st.button("Guardar nuevo taller"):
                            talleres_ws = cargar_worksheet_sin_cache("talleres")
                            talleres_ws.append_row([nuevo_taller])
                            st.success(f"Taller '{nuevo_taller}' guardado exitosamente.")
                            taller_seleccionado = nuevo_taller
                        else:
                            taller_seleccionado = None
                    else:
                        taller_seleccionado = nuevo_taller
                else:
                    taller_seleccionado = taller_opcion
        
                if estado_final == "cerrado":
                    st.markdown("### Información final del siniestro (opcional)")
                    valor_siniestro = st.number_input("Valor estimado del siniestro", min_value=0.0, format="%.2f", key="valor_siniestro")
                    deducible = st.text_input("Deducible (si aplica)", key="deducible")
                    rasa = st.text_input("RASA", key="rasa")
                    liquidacion = st.text_input("Liquidación", key="liquidacion")
                else:
                    valor_siniestro = ""
                    deducible = ""
                    rasa = ""
                    liquidacion = ""
        
                # Botón final para guardar cambios
                if st.button("Guardar Cambios"):
                    fecha_modificacion = datetime.now()
                    ultima_fecha = datetime.strptime(st.session_state.ticket_actual['Fecha_Creación'], "%Y-%m-%d %H:%M:%S")
                    dias_transcurridos = (fecha_modificacion - ultima_fecha).days
        
                    if estado_final != st.session_state.ticket_actual['Estado']:
                        registro_dias = f"{dias_transcurridos}d ({st.session_state.ticket_actual['Estado']} -> {estado_final})"
                    else:
                        registro_dias = "Sin cambio de estado"
        
                    ticket_actualizado = {
                        'Número': ticket_actual['Número'],
                        'Título': ticket_actual['Título'],
                        'Área': ticket_actual['Área'],
                        'Estado': estado_final,
                        'Descripción': descripcion_final,
                        'Fecha_Creación': ticket_actual['Fecha_Creación'],
                        'Usuario_Creación': ticket_actual['Usuario_Creación'],
                        'Fecha_Modificacion': fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                        'Usuario_Modificacion': st.session_state.usuario_actual,
                        'Tiempo_Cambio': registro_dias,
                        'Cliente': ticket_actual.get('Cliente'),
                        'Cedula': ticket_actual.get('Cedula'),
                        'CONCESIONARIO': ticket_actual.get('CONCESIONARIO'),
                        'ID': ticket_actual.get('ID'),
                        'ASEGURADORA': ticket_actual.get('ASEGURADORA'),
                        'CIUDAD OCURRENCIA': ticket_actual.get('CIUDAD OCURRENCIA'),
                        'TALLER': taller_seleccionado,
                        'MARCA': ticket_actual.get('MARCA'),
                        'MODELO': ticket_actual.get('MODELO'),
                        'AÑOCARRO': ticket_actual.get('AÑOCARRO'),
                        'PLACA': ticket_actual.get('PLACA'),
                        'fecha_ocurrencia': ticket_actual.get('fecha_ocurrencia'),
                        'SUMA ASEGURADA': ticket_actual.get('SUMA ASEGURADA'),
                        'VALOR SINIESTRO': valor_siniestro,
                        'DEDUCIBLE': deducible,
                        'RASA': rasa,
                        'LIQUIDACION': liquidacion,
                        'CAUSA': causa,
                        'Necesita Grua': ticket_actual.get('Necesita Grua'),
                        'Asistencia Legal': ticket_actual.get('Asistencia Legal'),
                        'Ubicacion': ticket_actual.get('Ubicacion'),
                        'Foto_URL': ticket_actual.get('Foto_URL')
                    }
                    
                    # Asegurar compatibilidad de tipos
                    ticket_actualizado_serializable = {
                        k: (int(v) if isinstance(v, float) and v.is_integer() else v)
                        for k, v in ticket_actualizado.items()
                    }
        
                    with st.spinner("Actualizando ticket..."):
                        sheet = cargar_worksheet_sin_cache("hoja")
                        sheet.append_row(list(ticket_actualizado_serializable.values()))
                        # Cargar datos actuales
                        pendientes_ws = cargar_worksheet_sin_cache("pendientes")
                        pagados_ws =cargar_worksheet_sin_cache("pagados")
                        todos_df = cargar_df_sin_cache("hoja")
                        actualizar_bases_reclamos(todos_df, spreadsheet_sin_cache)
                        st.success("Base actualizado correctamente ✅")
                        st.session_state.recargar_tickets = True
                        del st.session_state.ticket_actual
                        del st.session_state.estado_seleccionado
                        del st.session_state.descripcion_modificada
                        st.rerun()
                    
    elif opcion_ticket == "Subir documentación a reclamo":
        encabezado_sin_icono("Subir documentación a un reclamo existente", "h2")
        tickets_df = cargar_tickets()
        
        if tickets_df.empty:
            st.warning("No hay reclamos disponibles.")
            return
    
        # Opciones de búsqueda
        busqueda_tipo = st.radio("Buscar por:", ["Número de Reclamo", "Nombre del Cliente"])
    
        if busqueda_tipo == "Número de Reclamo":
            ticket_ids = tickets_df["Número"].unique().tolist()
            numero_ticket = st.selectbox("Selecciona el número de reclamo:", sorted(ticket_ids))
            ticket_seleccionado = tickets_df[tickets_df["Número"] == numero_ticket].iloc[-1]
        else:
            nombres = tickets_df["Cliente"].dropna().unique().tolist()
            nombre_cliente = st.selectbox("Selecciona el cliente:", sorted(nombres))
            tickets_cliente = tickets_df[tickets_df["Cliente"] == nombre_cliente]
            ticket_ids = tickets_cliente["Número"].unique().tolist()
            numero_ticket = st.selectbox("Selecciona el número de ticket del cliente:", sorted(ticket_ids))
            ticket_seleccionado = tickets_cliente[tickets_cliente["Número"] == numero_ticket].iloc[-1]
    
        st.info(f"Reclamo seleccionado: #{numero_ticket} — Cliente: {ticket_seleccionado['Cliente']}")
    
        archivos = st.file_uploader(
            "Selecciona uno o más archivos (PDF o imagen)",
            type=["jpg", "jpeg", "png", "pdf"],
            accept_multiple_files=True,
            key=f"upload_docs_ticket_{numero_ticket}"
        )
            
        if archivos:
            bucket_name = 'insurapp-fotos'
            s3 = boto3.client(
                's3',
                aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                region_name='us-east-1'
            )
    
            hoja_adjuntos = spreadsheet_sin_cache.worksheet("archivos_adjuntos")
            bucket_name = 'insurapp-fotos'
            for archivo in archivos:
                subir_y_mostrar_archivo(archivo=archivo, bucket_name=bucket_name, numero_ticket=numero_ticket, hoja_adjuntos=hoja_adjuntos,  usuario=ticket_seleccionado['Cliente'])
         
        if st.button("Descargar todos los archivos del reclamo"):
            import zipfile
            import requests
            df_adjuntos = cargar_df("archivos_adjuntos")
            archivos_ticket = df_adjuntos[df_adjuntos["Número Ticket"] == numero_ticket]
    
            if archivos_ticket.empty:
                st.warning("No hay archivos subidos para este ticket.")
            else:
                buffer = BytesIO()
                with zipfile.ZipFile(buffer, "w") as zip_file:
                    for _, row in archivos_ticket.iterrows():
                        url = row["URL"]
                        nombre_archivo = row["Nombre Archivo"]
                        try:
                            response = requests.get(url)
                            if response.status_code == 200:
                                zip_file.writestr(nombre_archivo, response.content)
                        except Exception as e:
                            st.error(f"Error descargando {nombre_archivo}: {e}")
                buffer.seek(0)
                nombre_zip = f"ticket_{numero_ticket}.zip"
                st.download_button(
                    label="Descargar ZIP",
                    data=buffer,
                    file_name=nombre_zip,
                    mime="application/zip"
                )                
        

  
def descargar_tickets():
    with st.spinner("Cargando datos..."):
        df_tickets = cargar_tickets()
        df_pagados, df_pendientes, df_asegurados = cargar_datos_dashboard_desde_sheets()

    hoja = st.selectbox(
        "Selecciona qué hoja quieres descargar:",
        ["Tickets", "Reclamos Pagados", "Reclamos Pendientes"]
    )

    formato = st.selectbox("Formato de descarga", ["CSV", "Excel", "JSON"])

    if hoja == "Tickets":
        df = df_tickets
        nombre_archivo = "tickets"
    elif hoja == "Reclamos Pagados":
        df = df_pagados
        nombre_archivo = "reclamos_pagados"
    elif hoja == "Reclamos Pendientes":
        df = df_pendientes
        nombre_archivo = "reclamos_pendientes"

    if not df.empty:
        if formato == "CSV":
            st.download_button(
                f"Descargar {hoja} en CSV",
                df.to_csv(index=False),
                f"{nombre_archivo}.csv",
                mime="text/csv"
            )
        elif formato == "Excel":
            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button(
                f"Descargar {hoja} en Excel",
                output.getvalue(),
                f"{nombre_archivo}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif formato == "JSON":
            st.download_button(
                f"Descargar {hoja} en JSON",
                df.to_json(orient="records"),
                f"{nombre_archivo}.json",
                mime="application/json"
            )

        encabezado_sin_icono("Vista Previa", "h3")
        base=df.tail()
        render_tabla_html(base,height=400)
    else:
        st.warning(f"⚠️ No hay datos disponibles en la hoja seleccionada ({hoja}).")


if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
if 'mostrar_login' not in st.session_state:
    st.session_state.mostrar_login = False
if 'mostrar_formulario_cotizacion' not in st.session_state:
    st.session_state.mostrar_formulario_cotizacion = False

if not st.session_state.autenticado:
    if st.session_state.mostrar_formulario_cotizacion:
        formulario_cotizacion()
    elif not st.session_state.mostrar_login:
        landing_page()
        st.stop()
    else:
        if not autenticacion():
            st.stop()
else:
    if st.session_state.rol == 'cliente':
        portal_cliente()
    else:
        portal_administracion()
