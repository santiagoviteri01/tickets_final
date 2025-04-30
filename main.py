import time
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
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


st.set_page_config(
    page_title="Insurapp",
    page_icon="",
    layout="wide"
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

# Convertir las credenciales a un formato JSON
creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

# Autenticarse con Google
client = gspread.authorize(creds)
# Autenticación con la cuenta de servicio
#creds = Credentials.from_service_account_info(st.secrets["general"], scopes=SCOPES)
#client = gspread.authorize(creds)
spreadsheet = client.open_by_key("13hY8la9Xke5-wu3vmdB-tNKtY5D6ud4FZrJG2_HtKd8")
sheet = spreadsheet.worksheet("hoja")      
asegurados = spreadsheet.worksheet("asegurados")
#sheet1 = spreadsheet.worksheet("sheet")        # Reemplaza "sheet" por el nombre real si es distinto
#sheet2 = spreadsheet.worksheet(asegurados)
# Obtén los datos de ambas hojas (opcional)
# Configuración inicial de la página

# Configuración de usuarios y contraseñas
USUARIOS = {
    "cliente1": {"password": "pass1", "rol": "cliente"},
    "cliente2": {"password": "pass2", "rol": "cliente"},
    "carlosserrano": {"password": "crediprime2", "rol": "admin"},
    "mauriciodavila": {"password": "insuratlan1", "rol": "admin"},
    "santiagoviteri": {"password": "insuratlan2", "rol": "admin"},
}
asegurados = asegurados.get_all_records()
asegurados_df = pd.DataFrame(asegurados)

for _, row in asegurados_df.iterrows():
    client_id = str(row["NOMBRE COMPLETO"])
    USUARIOS[client_id] = {
        "password": client_id,  # Contraseña = ID en texto plano
        "rol": "cliente"
    }
    
#@st.cache_data(ttl=300)   
#def cargar_datos():
#    try:
#        # Convertir los datos de la hoja a un DataFrame
#        data = sheet.get_all_records()  # Obtiene todos los registros (como una lista de diccionarios)
#        df = pd.DataFrame(data)  # Convertirlo en un DataFrame de pandas
#        
#        # Mostrar el DataFrame
#        return df
#    except Exception as e:
#        st.error(f"Error cargando datos: {str(e)}")
#        return pd.DataFrame()

@st.cache_data(ttl=300) 
def cargar_datos():
    try:
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
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



def subir_y_mostrar_archivo(archivo, bucket_name, numero_ticket, hoja_adjuntos, usuario="admin"):
    import io
    import base64

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
        f"{st.session_state.usuario_actual} ({usuario})",
        numero_ticket,
        archivo.name,
        file_type,
        archivo_url
    ])

    # ✅ Mostrar feedback visual
    st.success(f"✅ `{archivo.name}` subido correctamente al ticket #{numero_ticket}")

    if file_type == "application/pdf":
        base64_pdf = base64.b64encode(archivo_bytes).decode("utf-8")
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.image(io.BytesIO(archivo_bytes), caption=archivo.name, use_container_width=True)

    st.markdown(f"[🔗 Ver archivo en S3]({archivo_url})")
    st.markdown("---")
    
def formulario_cotizacion():
    st.header("📝 Cotizador de Seguros")

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
                hoja_cotizaciones = spreadsheet.worksheet("cotizaciones")
                nueva_fila = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), tipo_seguro, nombre, apellidos, correo, telefono, "no cotizada"]
                hoja_cotizaciones.append_row(nueva_fila)
                st.success("🎉 Tu solicitud ha sido enviada exitosamente. Pronto nos contactaremos contigo.")
                time.sleep(1.5)
                st.session_state.mostrar_formulario_cotizacion = False
                st.rerun()

    with col2:
        if st.button("⬅️ Volver"):
            st.session_state.mostrar_formulario_cotizacion = False
            st.rerun()

if 'recargar_tickets' not in st.session_state:
    st.session_state.recargar_tickets = False
    
def landing_page():
    st.markdown("""
        <style>
            .main-container {
                padding: 2rem;
                text-align: center;
                font-family: 'Segoe UI', sans-serif;
            }
            .logo-bar {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem 2rem;
                background-color: white;
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
                margin-bottom: 2rem;
            }
            .logo-text {
                font-size: 1.8rem;
                font-weight: bold;
                color: #ff0083;
                display: flex;
                align-items: center;
            }
            .logo-text img {
                height: 32px;
                margin-right: 10px;
            }
            .hero-title {
                font-size: 3rem;
                color: #ff0083;
                margin-bottom: 1rem;
                text-align: center;
            }
            .hero-subtitle {
                font-size: 1.2rem;
                color: #444;
                max-width: 700px;
                margin: 0 auto 2rem auto;
                text-align: center;
            }
            .hero-buttons button {
                margin: 0 1rem;
                padding: 0.8rem 2rem;
                font-size: 1rem;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }
        </style>
    """, unsafe_allow_html=True)

    # Barra superior con logo y botón de cuenta
    st.markdown("""
    <div class="logo-bar">
        <div class="logo-text">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/Insurance_icon.svg/1200px-Insurance_icon.svg.png" />
            InsurApp
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Contenido principal
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    st.markdown("<div class='hero-title'>Bienvenido a InsurApp</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-subtitle'>Tu sistema inteligente de gestión de seguros y reclamos. Rápido, seguro y accesible desde cualquier lugar.</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔐 Mi Cuenta", use_container_width=True):
            st.session_state.mostrar_login = True
            st.session_state.mostrar_formulario_cotizacion = False
            st.rerun()

    with col2:
        if st.button("📄 Cotiza con Nosotros", use_container_width=True):
            st.session_state.mostrar_login = False
            st.session_state.mostrar_formulario_cotizacion = True
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

       
def autenticacion():
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        with st.container():
            st.title("🔒 Inicio de Sesión")
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
                if st.button("⬅️ Volver"):
                    st.session_state.mostrar_login = False
                    st.rerun()
        return False
    return True


from folium.plugins import LocateControl

geolocator = Nominatim(user_agent="mi_app_insurapp")


# Si no necesitas reverse geocoding, puedes eliminar Geolocator
def obtener_ubicacion():
    # 1) Pedir permiso y guardar coords en session_state
    if "ubicacion_coords" not in st.session_state:
        st.subheader("📍 Solicitando permiso de ubicación…")
        js = '''
        new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(
                pos => resolve({lat: pos.coords.latitude, lon: pos.coords.longitude}),
                err => reject(err.message),
                {enableHighAccuracy: true, timeout:10000, maximumAge:0}
            );
        })
        '''
        coords = streamlit_js_eval(js_expressions=js, key="get_geo", debounce=1.0)

        if not coords or "lat" not in coords:
            st.warning(
                "⚠️ Para continuar, **permite** el acceso a tu ubicación en el navegador "
                "pulsar el botón permitir ubicación."
            )
            return ""

        # Guardar coordenadas
        st.session_state.ubicacion_coords = {"lat": coords["lat"], "lon": coords["lon"]}
        st.success("🎉 Permiso concedido y ubicación obtenida.")

    # 2) Usar coords guardadas
    lat = st.session_state.ubicacion_coords["lat"]
    lon = st.session_state.ubicacion_coords["lon"]

    # 3) Mostrar mapa y marcador draggable
    m = folium.Map(location=[lat, lon], zoom_start=16)
    LocateControl(auto_start=False, flyTo=True).add_to(m)
    folium.Marker(
        [lat, lon],
        draggable=True,
        icon=folium.Icon(color="red", icon="map-pin", prefix="fa"),
        popup="📍 Arrastra para ajustar"
    ).add_to(m)

    out = st_folium(m, height=450, width=700, returned_objects=["last_clicked"])
    if out and out.get("last_clicked"):
        p = out["last_clicked"]
        lat, lon = p["lat"], p["lng"]
        st.session_state.ubicacion_coords = {"lat": lat, "lon": lon}
        st.success(f"🔄 Coordenadas ajustadas: {lat:.6f}, {lon:.6f}")

    # 4) Generar y mostrar link de Google Maps
    maps_link = f"https://www.google.com/maps?q={lat:.6f},{lon:.6f}"
    st.markdown(f"**[🔗 Ver en Google Maps]({maps_link})**")

    # 5) Devolver el link para guardar en tu sheet
    return maps_link
    
# Portal del Cliente
def portal_cliente():
    st.title(f"👤 Portal del Cliente - {st.session_state.usuario_actual}")
        # Botón de cerrar sesión en el sidebar
    st.sidebar.title("Menú Cliente")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.autenticado = False
        st.session_state.mostrar_login = False
        st.success("Sesión cerrada exitosamente")
        time.sleep(1)
        st.rerun()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Mis Datos y Coberturas", "Mis Tickets", "Nuevo Reclamo", "📎 Subir Archivos"])
    with tab1:
        st.header("🧾 Mis Datos Personales y del Vehículo")
    
        cliente_id = st.session_state.usuario_actual
        cliente_data = asegurados_df[asegurados_df["NOMBRE COMPLETO"].astype(str) == cliente_id]
    
        if not cliente_data.empty:
            datos = cliente_data.iloc[0]
    
            # Mostrar en columnas
            st.subheader("Información Personal")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Nombre Completo:** {datos['NOMBRE COMPLETO']}")
                st.write(f"**Género:** {datos['GENERO']}")
                st.write(f"**Estado Civil:** {datos['ESTADO CIVIL']}")
                st.write(f"**Ciudad:** {datos['CIUDAD CLIENTE']}")
                st.write(f"**Fecha de Nacimiento:** {datos['FECHA NACIMIENTO']}")
                st.write(f"**Correo:** {datos['CORREO ELECTRÓNICO']}")
    
            with col2:
                st.write(f"**Dirección Oficina:** {datos['DIRECCIÓN OFICINA']}")
                st.write(f"**Teléfono Oficina:** {datos['TELÉFONO OFICINA']}")
                st.write(f"**Dirección Domicilio:** {datos['DIRECCIÓN DOMICILIO']}")
                st.write(f"**Teléfono Domicilio:** {datos['TELÉFONO DOMICILIO']}")
    
            st.subheader("Información de la Póliza")
            st.write(f"**Póliza Maestra:** {datos['POLIZA MAESTRA']}")
            st.write(f"**Número Certificado:** {datos['NÚMERO CERTIFICADO']}")
            st.write(f"**Fecha Vigencia:** {datos['FECHA VIGENCIA']}")
            st.write(f"**Fecha Expiración:** {datos['FECHA EXPIRACIÓN']}")
            st.write(f"**Aseguradora:** {datos['ASEGURADORA']}")
            st.write(f"**Plan:** {datos['PLAN']}")
    
            st.subheader("Información del Vehículo")
            col3, col4 = st.columns(2)
            with col3:
                st.write(f"**Marca:** {datos['MARCA']}")
                st.write(f"**Modelo:** {datos['MODELO']}")
                st.write(f"**Año:** {datos['AÑO']}")
                st.write(f"**Clase (Tipo):** {datos['CLASE (TIPO)']}")
            with col4:
                st.write(f"**Motor:** {datos['MOTOR']}")
                st.write(f"**Chasis:** {datos['CHASIS']}")
                st.write(f"**Color:** {datos['COLOR']}")
                st.write(f"**Tipo Placa:** {datos['TIPO PLACA']}")
                st.write(f"**Placa:** {datos['PLACA']}")
    
            st.write(f"**Accesorios:** {datos['ACCESORIOS']}")
            st.write(f"**Valor Asegurado:** {datos['VALOR ASEGURADO']}")
    
            # Mostrar coberturas según aseguradora
            aseguradora = datos["ASEGURADORA"].strip().upper()
    
            st.subheader("📋 Ver Coberturas")
            if aseguradora == "ZURICH SEGUROS":
                st.info("Coberturas ZURICH")
                with open("archivos_coberturas/certificado_zurich.pdf", "rb") as file:
                    st.download_button(label="📥 Descargar Coberturas ZURICH", data=file, file_name="Coberturas_ZURICH.pdf", mime="application/pdf")
            elif aseguradora == "MAPFRE":
                st.info("Coberturas MAPFRE")
                with open("archivos_coberturas/certificado_mapfre.pdf", "rb") as file:
                    st.download_button(label="📥 Descargar Coberturas MAPFRE", data=file, file_name="Coberturas_MAPFRE.pdf", mime="application/pdf")
            elif aseguradora == "AIG":
                st.info("Coberturas AIG")
                with open("archivos_coberturas/certificado_aig.pdf", "rb") as file:
                    st.download_button(label="📥 Descargar Coberturas AIG", data=file, file_name="Coberturas_AIG.pdf", mime="application/pdf")
        else:
            st.error("No se encontró información para tu cuenta.")
    
    with tab2:
        st.header("Mis Tickets")
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
                                'nuevo': '🔵',
                                'en proceso': '🟡',
                                'resuelto': '🟢',
                                'cerrado': '✅',
                                'documentacion pendiente': '🟠'
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
                                    st.subheader("📸 Foto del Siniestro")
                                    st.image(ticket['Foto_URL'], caption="Imagen del siniestro", use_container_width=True)
                                except Exception as e:
                                    st.warning(f"⚠️ Error mostrando la imagen: {e}")
                            else:
                                st.info("No se adjuntó foto del siniestro.")
            else:
                st.info("No se encontraron tickets con los filtros seleccionados.")
        else:
            st.warning("No hay tickets registrados.")

    UPLOAD_DIR = "uploads"
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    with tab3:
        st.header("Nuevo Reclamo")
        with st.form("nuevo_reclamo"):
            titulo = st.text_input("Título del Reclamo*")
            descripcion = st.text_area("Descripción detallada*")
            area = st.selectbox("Área*", ["Todas", "Vehicular", "Vida", "Salud"])
    
            st.subheader("Asistencia Adicional")
            necesita_grua = st.selectbox("¿Necesitas grúa?", ["No", "Sí"])
            asistencia_legal = st.selectbox("¿Necesitas asistencia legal en el punto?", ["No", "Sí"])
            enviar_asistencias = st.form_submit_button("Enviar Asistencias")
            
            # Sección de ubicación automática con GPS solo si es necesario
            ubicacion_actual = ""
            if necesita_grua == "Sí" or asistencia_legal == "Sí":
                ubicacion_actual = obtener_ubicacion()
                permiso_ubicacion = st.form_submit_button("permitir ubicación")
    
            st.subheader("Información sobre el Siniestro")
            siniestro_vehicular = st.selectbox("¿Fue un siniestro vehicular?", ["No", "Sí"])
            enviar_vehiculos = st.form_submit_button("Enviar Foto")

            foto_siniestro = None
            if siniestro_vehicular == "Sí":
                foto_siniestro = None
                
                # Opción 1: Capturar desde la cámara
                foto_siniestro = st.camera_input("Toma una foto del siniestro (opcional)")
                
                # Opción 2: Subir desde el dispositivo si no se usa la cámara
                if foto_siniestro is None:
                    foto_siniestro = st.file_uploader("O bien, sube una imagen desde tu dispositivo", type=["jpg", "jpeg", "png"])
            
            enviar_reclamo = st.form_submit_button("Enviar Reclamo")   
            if enviar_reclamo:
                if not all([titulo, descripcion]):
                    st.error("❌ Por favor completa todos los campos obligatorios.")
                else:
                    # 🔥 Subir foto a S3 si existe
                    foto_url = None
                    if foto_siniestro is not None:
                        s3 = boto3.client(
                            's3',
                            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                            region_name='us-east-1'
                        )
                    
                        bucket_name = 'insurapp-fotos'
                        extension = foto_siniestro.name.split('.')[-1]
                        unique_filename = f"reclamos/{str(uuid.uuid4())}.{extension}"
                    
                        s3.upload_fileobj(
                            foto_siniestro,
                            bucket_name,
                            unique_filename,
                            ExtraArgs={
                                'ContentType': foto_siniestro.type,
                                'ACL': 'public-read'  # 👈 SUPER IMPORTANTE
                            }
                        )
                        foto_url = f"https://{bucket_name}.s3.us-east-1.amazonaws.com/{unique_filename}"
    
                    # Guardar el reclamo
                    df = cargar_datos()
                    ultimo_ticket = df['Número'].max() if not df.empty else 0
                    nuevo_numero = int(ultimo_ticket) + 1
    
                    nuevo_ticket = {
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
                        'Grua': necesita_grua,
                        'Asistencia_Legal': asistencia_legal,
                        'Ubicacion': ubicacion_actual,
                        'Foto_URL': foto_url if foto_url else None
                    }
    
                    nuevo_ticket_serializable = {k: str(v) for k, v in nuevo_ticket.items()}
                    sheet.append_row(list(nuevo_ticket_serializable.values()))
    
                    st.success(f"✅ Reclamo #{nuevo_numero} creado exitosamente 🚀")
        
    with tab4:
        st.header("📎 Subir Archivos Adicionales a un Reclamo")
    
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
    
                hoja_adjuntos = spreadsheet.worksheet("archivos_adjuntos")
    
                for archivo in archivos:
                    file_type = archivo.type
                    extension = archivo.name.split('.')[-1]
                    unique_filename = f"adjuntos/{str(uuid.uuid4())}.{extension}"
    
                    # Subir a S3
                    s3.upload_fileobj(
                        archivo,
                        bucket_name,
                        unique_filename,
                        ExtraArgs={'ContentType': file_type, 'ACL': 'public-read'}
                    )
                    archivo_url = f"https://{bucket_name}.s3.us-east-1.amazonaws.com/{unique_filename}"
    
                    # Guardar en hoja de Google Sheets
                    hoja_adjuntos.append_row([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        st.session_state.usuario_actual,
                        numero_reclamo,
                        archivo.name,
                        file_type,
                        archivo_url
                    ])
    
                    # Mostrar resultado
                    st.success(f"✅ Archivo `{archivo.name}` subido y vinculado al reclamo #{numero_reclamo}")
    
                    if file_type == "application/pdf":
                        archivo.seek(0)
                        base64_pdf = base64.b64encode(archivo.read()).decode("utf-8")
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                    else:
                        st.image(archivo, caption=f"Vista previa: {archivo.name}", use_container_width=True)
    
                    st.markdown(f"🔗 **[Ver archivo en S3]({archivo_url})**")
                    st.markdown("---")
            
def modulo_cotizaciones_mauricio():
    st.title("📋 Gestión de Cotizaciones")

    hoja_cotizaciones = spreadsheet.worksheet("cotizaciones")
    cotizaciones_data = hoja_cotizaciones.get_all_records()
    cotizaciones_df = pd.DataFrame(cotizaciones_data)
    # 🔥 Aquí agregas la recarga automática
    if st.session_state.get("recargar_cotizaciones"):
        cotizaciones_df = pd.DataFrame(hoja_cotizaciones.get_all_records())
        st.session_state.recargar_cotizaciones = False

    if cotizaciones_df.empty:
        st.info("No hay cotizaciones registradas.")
        return

    # Asegurarse que la columna de estado existe
    if 'Estado' not in cotizaciones_df.columns:
        cotizaciones_df['Estado'] = 'no cotizada'

    estados = ["no cotizada", "en proceso", "cotizada", "aceptada", "rechazada"]
    

    def actualizar_estado(index, nuevo_estado):
        hoja_cotizaciones.update_cell(index + 2, cotizaciones_df.columns.get_loc('Estado') + 1, nuevo_estado)
        st.success(f"Cotización actualizada a '{nuevo_estado}'.")
        time.sleep(1)
        st.session_state.recargar_cotizaciones = True
        st.rerun()


    # Sección 1: Nuevas Cotizaciones
    st.subheader("🔵 Cotizaciones Nuevas (No Cotizadas)")
    nuevas = cotizaciones_df[cotizaciones_df['Estado'] == 'no cotizada']
    for idx, row in nuevas.iterrows():
        with st.expander(f"🆕 {row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']}"):
            st.write(f"**Correo:** {row['Correo']}")
            st.write(f"**Teléfono:** {row['Teléfono']}")
            if st.button(f"Tomar Cotización #{idx}", key=f"tomar_{idx}"):
                actualizar_estado(idx, "en proceso")

    # Sección 2: Cotizaciones en Proceso
    st.subheader("🟡 Cotizaciones en Proceso")
    en_proceso = cotizaciones_df[cotizaciones_df['Estado'] == 'en proceso']
    for idx, row in en_proceso.iterrows():
        with st.expander(f"🔄 {row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']}"):
            st.write(f"**Correo:** {row['Correo']}")
            st.write(f"**Teléfono:** {row['Teléfono']}")
            opcion = st.selectbox(f"Actualizar estado Cotización #{idx}", ["cotizada", "rechazada"], key=f"proceso_{idx}")
            if st.button(f"Actualizar Estado #{idx}", key=f"btn_proceso_{idx}"):
                actualizar_estado(idx, opcion)

    # Sección 3: Cotizaciones Cotizadas
    st.subheader("🟢 Cotizaciones Cotizadas")
    cotizadas = cotizaciones_df[cotizaciones_df['Estado'] == 'cotizada']
    for idx, row in cotizadas.iterrows():
        with st.expander(f"✅ {row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']}"):
            st.write(f"**Correo:** {row['Correo']}")
            st.write(f"**Teléfono:** {row['Teléfono']}")
            opcion = st.selectbox(f"Actualizar estado Cotización #{idx}", ["aceptada", "rechazada"], key=f"cotizada_{idx}")
            if st.button(f"Actualizar Estado #{idx}", key=f"btn_cotizada_{idx}"):
                actualizar_estado(idx, opcion)

    # Sección 4: Cotizaciones Finalizadas
    st.subheader("⚪ Cotizaciones Finalizadas (Aceptadas o Rechazadas)")
    finalizadas = cotizaciones_df[cotizaciones_df['Estado'].isin(['aceptada', 'rechazada'])]
    for idx, row in finalizadas.iterrows():
        with st.expander(f"🏁 {row['Nombre']} {row['Apellidos']} - {row['Tipo Seguro']} - {row['Estado'].capitalize()}"):
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
                'nuevo': '🔵', 'en proceso': '🟡', 'resuelto': '🟢',
                'cerrado': '✅', 'documentacion pendiente': '🟠'
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
                st.markdown(f"[📍 Ver en Google Maps]({ubic})", unsafe_allow_html=True)

            # Foto del siniestro
            url = ticket.get('Foto_URL', '')
            if isinstance(url, str) and url.startswith("http"):
                st.subheader("📸 Foto del Siniestro")
                st.image(url, caption="Imagen del siniestro", use_container_width=True)
                st.markdown(f"[🔗 Ver imagen en nueva pestaña]({url})", unsafe_allow_html=True)
            else:
                st.info("No se adjuntó foto del siniestro.")



# Portal de Administración (Usuarios)
def portal_administracion():
    st.sidebar.title("Menú Admin")
    opciones = [
        "Inicio", 
        "Gestión de Tickets", 
        "Análisis", 
        "Descargar Datos"
    ]
    
    
    if st.session_state.usuario_actual == "mauriciodavila":
        opciones.insert(1, "Gestión de Cotizaciones")

    opciones.append("Cerrar Sesión")
    
    opcion = st.sidebar.radio("Opciones", opciones)

    if opcion == "Inicio":
        st.title("🏠 Panel de Administración")
        st.markdown("""
        **Bienvenido al panel de administración**
        Selecciona una opción del menú lateral para comenzar.
        """)

    elif opcion == "Gestión de Tickets":
        st.title("📋 Gestión de Tickets")
        manejar_tickets()
        

    elif opcion == "Análisis":
        st.title("📈 Análisis de Datos")
        visualizar_tickets()

    elif opcion == "Descargar Datos":
        st.title("⬇️ Descargar Datos")
        descargar_tickets()
        
    elif opcion == "Gestión de Cotizaciones" and st.session_state.usuario_actual == "mauriciodavila":
        modulo_cotizaciones_mauricio()
        
    elif opcion == "Cerrar Sesión":
        st.session_state.autenticado = False
        st.session_state.mostrar_login = False
        st.success("Sesión cerrada exitosamente")
        time.sleep(1)
        st.rerun()


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

        # Filtros
        st.subheader("Filtros")
        area = st.selectbox("Área", ["Todas"] + list(df['Área'].unique()))
        estado = st.selectbox("Estado", ["Todos"] + list(df['Estado'].unique()))
        if area != "Todas":
            df = df[df['Área'] == area]
        if estado != "Todos":
            df = df[df['Estado'] == estado]

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
                        'nuevo': '🔵',
                        'en proceso': '🟡',
                        'resuelto': '🟢',
                        'cerrado': '✅',
                        'documentacion pendiente': '🟠'
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
                        st.markdown(f"[📍 Ver en Google Maps]({ubic})", unsafe_allow_html=True)

                    # Foto del siniestro
                    url = ticket.get('Foto_URL', '')
                    if isinstance(url, str) and url.startswith("http"):
                        st.subheader("📸 Foto del Siniestro")
                        st.image(url, caption="Imagen del siniestro", use_container_width=True)
                        st.markdown(f"[🔗 Ver imagen en nueva pestaña]({url})", unsafe_allow_html=True)
                    else:
                        st.info("No se adjuntó foto del siniestro.")
# Versión cacheada para uso general
@st.cache_data(ttl=300)
def _cargar_tickets():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Función pública para permitir limpieza de caché
def cargar_tickets(clear_cache=False):
    if clear_cache:
        st.cache_data.clear()
    return _cargar_tickets()
    

def manejar_tickets():
    # ✅ Nuevo bloque más limpio y eficiente
    df = cargar_tickets(clear_cache=st.session_state.get("recargar_tickets", False))
    st.session_state.recargar_tickets = False

    # 3) Radio controlada por session_state
    opcion_ticket = st.radio(
        "Seleccione una acción:",
        ["Ver tickets en cola", "Crear nuevo ticket", "Modificar ticket existente", "Subir documentación a ticket"]
    )
    
    if opcion_ticket == "Ver tickets en cola":
        
        st.subheader("🔍 Ver tickets en cola")
        if df.empty:
            st.warning("No se encontraron tickets")
            return

        ultimos = (df.sort_values('Fecha_Modificacion')
                     .groupby('Número')
                     .last()
                     .reset_index())
        cola = ultimos[(ultimos['Usuario_Modificacion'] == 'cliente') &
                      (ultimos['Estado'] != 'cerrado')]

        if cola.empty:
            st.info("No hay tickets pendientes de clientes")
            return

        st.metric("Tickets Pendientes", len(cola))
        st.dataframe(
            cola[['Número','Título','Cliente','Estado','Fecha_Modificacion']]
            .sort_values('Fecha_Modificacion', ascending=False),
            use_container_width=True, height=300
        )

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
                st.session_state.opcion_ticket = "Modificar ticket existente"
                st.success(f"✅ Ticket #{selected} asignado para gestión") 
        else:
            st.info("Selecciona un número válido de la tabla anterior")
    elif opcion_ticket == "Crear nuevo ticket":
        with st.form("nuevo_ticket"):
            st.subheader("📝 Crear nuevo ticket con datos del asegurado")
    
            # Paso 1: Buscar cliente por cédula o póliza
            asegurados_data = asegurados_df.copy()
            tipo_busqueda = st.radio("Buscar por:", ["Cédula", "Número de Póliza"])
            if tipo_busqueda == "Cédula":
                cedula = st.text_input("Ingrese el número:")
                coincidencias = asegurados_data[asegurados_data["CÉDULA"].astype(str) == cedula]
            else:
                poliza = st.text_input("Ingrese número de póliza:")
                coincidencias = asegurados_data[asegurados_data["POLIZA MAESTRA"].astype(str) == poliza]
    
            if not coincidencias.empty:
                vehiculo = st.selectbox(
                    "Selecciona el vehículo asegurado:",
                    coincidencias.apply(lambda row: f"{row['MARCA']} {row['MODELO']} ({row['PLACA']})", axis=1)
                )
                vehiculo_info = coincidencias.iloc[list(coincidencias.apply(lambda row: f"{row['MARCA']} {row['MODELO']} ({row['PLACA']})", axis=1)).index(vehiculo)]
    
                # Relleno automático
                cliente = vehiculo_info["NOMBRE COMPLETO"]
                cedula = vehiculo_info["CÉDULA"]
                concesionario = vehiculo_info.get("CONCESIONARIO", "")
                id_liderseg = vehiculo_info.get("ID_LIDERSEG", "")
                aseguradora = vehiculo_info["ASEGURADORA"]
                ciudad = vehiculo_info["CIUDAD CLIENTE"]
                marca = vehiculo_info["MARCA"]
                modelo = vehiculo_info["MODELO"]
                anio = vehiculo_info["AÑO"]
                placa = vehiculo_info["PLACA"]
                suma_asegurada = vehiculo_info["VALOR ASEGURADO"]
            else:
                st.warning("No se encontraron coincidencias.")
                st.stop()
    
            # Paso 4: Datos del ticket
            titulo = st.text_input("Título del Ticket*")
            area = st.selectbox("Área*", ["crediprime", "generales"])
            estado = st.selectbox("Estado*", ["inicial", "documentacion pendiente", "documentacion enviada", "en reparacion"])
            descripcion = st.text_area("Descripción detallada*")
            ciudad_ocurrencia = st.text_input("Ciudad donde ocurrió el siniestro*")
            fecha_ocurrencia = st.date_input("Fecha de ocurrencia")
            #valor_siniestro = st.number_input("Valor estimado del siniestro", min_value=0.0, format="%.2f")
            #deducible = st.text_input("Deducible (si aplica)")
            causa = st.selectbox("Causa*", ["ROBO", "ROBO PARCIAL", "PERDIDA TOTAL", "PERDIDA PARCIAL"])
            #rasa = st.text_input("RASA")
            #liquidacion = st.text_input("Liquidación")
    
            necesita_grua = st.selectbox("¿Necesita grúa?", ["No", "Sí"])
            asistencia_legal = st.selectbox("¿Requiere asistencia legal?", ["No", "Sí"])
    
            if st.form_submit_button("Guardar Ticket"):
                fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ultimo_ticket = df["Número"].max() if not df.empty else 0
                nuevo_numero = int(ultimo_ticket) + 1
    
                nuevo_ticket = {
                    'Número': nuevo_numero,
                    'Título': titulo,
                    'Área': area,
                    'Estado': estado,
                    'Descripción': descripcion,
                    'Fecha_Creación': fecha_creacion,
                    'Usuario_Creación': st.session_state.usuario_actual,
                    'Fecha_Modificacion': fecha_creacion,
                    'Usuario_Modificacion': st.session_state.usuario_actual,
                    'Tiempo_Cambio': '0d',
                    'Cliente': cliente,
                    'Cedula': cedula,
                    'CONCESIONARIO': concesionario,
                    'ID_LIDERSEG': id_liderseg,
                    'ASEGURADORA': aseguradora,
                    'CIUDAD OCURRENCIA': ciudad_ocurrencia,
                    'MARCA': marca,
                    'MODELO': modelo,
                    'AÑO': anio,
                    'PLACA': placa,
                    'fecha_ocurrecia': fecha_ocurrencia.strftime("%Y-%m-%d"),
                    'SUMA ASEGURADA': suma_asegurada,
                    'VALOR SINIESTRO': None,
                    'DEDUCIBLE': None,
                    'RASA':None,
                    'LIQUIDACION': None,
                    'CAUSA': causa,
                    'Necesita Grua': necesita_grua,
                    'Asistencia Legal': asistencia_legal,
                    'Ubicacion': None,
                    'Foto_URL': None
                }
    
                nuevo_ticket_serializable = {k: str(v) for k, v in nuevo_ticket.items()}
    
                sheet.append_row(list(nuevo_ticket_serializable.values()))
                st.success(f"✅ Ticket #{nuevo_numero} registrado correctamente.")
                st.session_state.recargar_tickets = True
                st.rerun()



    elif opcion_ticket == "Modificar ticket existente":
        with st.form("buscar_ticket"):
            st.subheader("🔍 Buscar Ticket")
            ticket_id = st.number_input("Ingrese el número de ticket:", min_value=1, step=1)

            if st.form_submit_button("Buscar"):
                ticket_encontrado = df[df['Número'] == ticket_id]

                if not ticket_encontrado.empty:
                    ticket = ticket_encontrado.iloc[-1]
                    if ticket['Estado'] == "cerrado":
                        st.error("No se puede modificar un ticket cerrado")
                    else:
                        st.session_state.ticket_actual = ticket.to_dict()
                else:
                    st.error("Ticket no encontrado")
        
        if 'ticket_actual' in st.session_state:
            st.subheader(f"✏️ Modificando Ticket #{st.session_state.ticket_actual['Número']}")
        
            # Paso 1: Selección de estado y descripción (dentro del formulario)
            with st.form("seleccion_estado_form"):
                nuevo_estado = st.selectbox(
                    "Nuevo estado:",
                    ["inicial", "documentacion pendiente", "documentacion enviada", "en reparacion", "cerrado"],
                    index=["creado por usuario", "inicial", "documentacion pendiente", "documentacion enviada", "en reparacion", "cerrado"].index(
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
                estado_final = st.session_state.estado_seleccionado
                descripcion_final = st.session_state.descripcion_modificada
        
                if estado_final == "cerrado":
                    st.markdown("### 📝 Información final del siniestro (opcional)")
                    valor_siniestro = st.number_input("Valor estimado del siniestro", min_value=0.0, format="%.2f", key="valor_siniestro")
                    deducible = st.text_input("Deducible (si aplica)", key="deducible")
                    causa = st.text_input("Causa del siniestro (breve)", key="causa")
                    rasa = st.text_input("RASA", key="rasa")
                    liquidacion = st.text_input("Liquidación", key="liquidacion")
                else:
                    valor_siniestro = ""
                    deducible = ""
                    causa = ""
                    rasa = ""
                    liquidacion = ""
        
                # Botón final para guardar cambios
                if st.button("💾 Guardar Cambios"):
                    fecha_modificacion = datetime.now()
                    ultima_fecha = datetime.strptime(st.session_state.ticket_actual['Fecha_Creación'], "%Y-%m-%d %H:%M:%S")
                    dias_transcurridos = (fecha_modificacion - ultima_fecha).days
        
                    if estado_final != st.session_state.ticket_actual['Estado']:
                        registro_dias = f"{dias_transcurridos}d ({st.session_state.ticket_actual['Estado']} -> {estado_final})"
                    else:
                        registro_dias = "Sin cambio de estado"
        
                    ticket_actual = st.session_state.ticket_actual
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
                        'Cliente': ticket_actual['Cliente'],
                        'Grua': ticket_actual.get('Grua'),
                        'Asistencia_Legal': ticket_actual.get('Asistencia_Legal'),
                        'Ubicacion': ticket_actual.get('Ubicacion'),
                        'Foto_URL': ticket_actual.get('Foto_URL'),
                        'VALOR SINIESTRO': valor_siniestro,
                        'DEDUCIBLE': deducible,
                        'CAUSA': causa,
                        'RASA': rasa,
                        'LIQUIDACION': liquidacion,
                    }
        
                    ticket_actualizado_serializable = {
                        k: int(v) if isinstance(v, (int, float)) else v for k, v in ticket_actualizado.items()
                    }
        
                    with st.spinner("Actualizando ticket..."):
                        sheet.append_row(list(ticket_actualizado_serializable.values()))
                        st.success("Ticket actualizado correctamente ✅")
                        st.session_state.recargar_tickets = True
                        del st.session_state.ticket_actual
                        del st.session_state.estado_seleccionado
                        del st.session_state.descripcion_modificada
                        st.rerun()
                    
    elif opcion_ticket == "Subir documentación a ticket":
        st.subheader("📎 Subir documentación a un ticket existente")
    
        tickets_df = cargar_tickets()
        if tickets_df.empty:
            st.warning("No hay tickets disponibles.")
            return
    
        # Opciones de búsqueda
        busqueda_tipo = st.radio("Buscar por:", ["Número de Ticket", "Nombre del Cliente"])
    
        if busqueda_tipo == "Número de Ticket":
            ticket_ids = tickets_df["Número"].unique().tolist()
            numero_ticket = st.selectbox("Selecciona el número de ticket:", sorted(ticket_ids))
            ticket_seleccionado = tickets_df[tickets_df["Número"] == numero_ticket].iloc[-1]
        else:
            nombres = tickets_df["Cliente"].dropna().unique().tolist()
            nombre_cliente = st.selectbox("Selecciona el cliente:", sorted(nombres))
            tickets_cliente = tickets_df[tickets_df["Cliente"] == nombre_cliente]
            ticket_ids = tickets_cliente["Número"].unique().tolist()
            numero_ticket = st.selectbox("Selecciona el número de ticket del cliente:", sorted(ticket_ids))
            ticket_seleccionado = tickets_cliente[tickets_cliente["Número"] == numero_ticket].iloc[-1]
    
        st.info(f"📄 Ticket seleccionado: #{numero_ticket} — Cliente: {ticket_seleccionado['Cliente']}")
    
        archivos = st.file_uploader(
            "📤 Selecciona uno o más archivos (PDF o imagen)",
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
    
            hoja_adjuntos = spreadsheet.worksheet("archivos_adjuntos")
            bucket_name = 'insurapp-fotos'
            for archivo in archivos:
                subir_y_mostrar_archivo(
                    archivo=archivo,
                    bucket_name=bucket_name,
                    numero_ticket=numero_ticket,
                    hoja_adjuntos=hoja_adjuntos,
                    usuario="admin"  # o "cliente" si estás en el portal del cliente
                )
        

  
def descargar_tickets():
    with st.spinner("🔄 Cargando tickets para descarga..."):
        df = cargar_tickets()  # usa la función cacheada que definimos antes

    if not df.empty:
        formato = st.selectbox("Formato de descarga", ["CSV", "Excel", "JSON"])

        if formato == "CSV":
            st.download_button("📥 Descargar CSV", df.to_csv(index=False), "tickets.csv", mime="text/csv")
        elif formato == "Excel":
            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("📥 Descargar Excel", output.getvalue(), "tickets.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        elif formato == "JSON":
            st.download_button("📥 Descargar JSON", df.to_json(orient="records"), "tickets.json", mime="application/json")

        st.write("📊 Vista previa de los últimos registros:")
        st.dataframe(df.tail(), use_container_width=True)
    else:
        st.warning("⚠️ No hay datos disponibles para descargar.")



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
