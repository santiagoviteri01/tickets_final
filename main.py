import time
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
#from streamlit_gsheets import GSheetsConnection
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from pathlib import Path
import numpy as np

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


# Verificar que todas las credenciales estén presentes
required_keys = ["private_key_id", "private_key", "client_email", "client_id"]
missing_keys = [key for key in required_keys if not creds_dict.get(key)]

if missing_keys:
    st.error(f"❌ Faltan credenciales: {', '.join(missing_keys)}")
    st.stop()

# Convertir las credenciales a un formato JSON
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

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
    
def cargar_datos():
    try:
        # Convertir los datos de la hoja a un DataFrame
        data = sheet.get_all_records()  # Obtiene todos los registros (como una lista de diccionarios)
        df = pd.DataFrame(data)  # Convertirlo en un DataFrame de pandas
        
        # Mostrar el DataFrame
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame()

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
    
    tab1, tab2, tab3 = st.tabs(["Mis Datos y Coberturas", "Mis Tickets", "Nuevo Reclamo"])
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
            # Filtrar tickets del cliente
            mis_tickets = df[df['Cliente'] == st.session_state.usuario_actual]
            
            # Filtro por estado
            estado_filtro = st.selectbox("Filtrar por estado:", 
                                        ["Todos", "Abiertos", "Cerrados"])
            
            if estado_filtro == "Abiertos":
                mis_tickets = mis_tickets[mis_tickets['Estado'] != 'cerrado']
            elif estado_filtro == "Cerrados":
                mis_tickets = mis_tickets[mis_tickets['Estado'] == 'cerrado']
            
            if not mis_tickets.empty:
                # Mostrar resumen de estados
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Tickets Abiertos", 
                             len(mis_tickets[mis_tickets['Estado'] != 'cerrado']['Número'].unique()))
                with col2:
                    st.metric("Tickets Cerrados", 
                             len(mis_tickets[mis_tickets['Estado'] == 'cerrado']['Número'].unique()))
                with col3:
                    ultimo_ticket = mis_tickets.iloc[-1]
                    st.metric("Último Estado", ultimo_ticket['Estado'])
                
                # Mostrar tickets con detalles
                for _, ticket in mis_tickets.iterrows():
                    with st.expander(f"Ticket #{ticket['Número']} - {ticket['Título']}"):
                        col_left, col_right = st.columns([1, 3])
                        
                        with col_left:
                            # Icono y color según estado
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
                            st.write(f"**Descripción:**")
                            st.write(ticket['Descripción'])
                            
                            if pd.notna(ticket['Tiempo_Cambio']):
                                st.write("**Historial de cambios:**")
                                cambios = ticket['Tiempo_Cambio'].split(';')
                                for cambio in cambios:
                                    st.write(f"- {cambio.strip()}")
            else:
                st.info("No se encontraron tickets con los filtros seleccionados")
        else:
            st.warning("No hay tickets registrados")
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
    
            ubicacion_actual = None
            if necesita_grua == "Sí" or asistencia_legal == "Sí":
                ubicacion_actual = st.text_input("📍 Pega aquí tu ubicación de Google Maps:")
    
            st.subheader("Información sobre el Siniestro")
            siniestro_vehicular = st.selectbox("¿Fue un siniestro vehicular?", ["No", "Sí"])
            enviar_vehiculos = st.form_submit_button("Enviar Foto")

            foto_siniestro = None
            ruta_foto = None
            if siniestro_vehicular == "Sí":
                foto_siniestro = st.file_uploader("📸 Sube una foto del siniestro (opcional)", type=["jpg", "jpeg", "png"])
    
            # Botón de enviar reclamo
            enviar_reclamo = st.form_submit_button("Enviar Reclamo")
    
            if enviar_reclamo:
                if not all([titulo, descripcion]):
                    st.error("❌ Por favor completa todos los campos obligatorios.")
                else:
                    # Crear carpeta si no existe
                    if foto_siniestro:
                        if not os.path.exists('fotos_siniestros'):
                            os.makedirs('fotos_siniestros')
                        ruta_foto = f'fotos_siniestros/{foto_siniestro.name}'
                        with open(ruta_foto, 'wb') as f:
                            f.write(foto_siniestro.getbuffer())
    
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
                        'Ruta_Foto': ruta_foto if ruta_foto else "No adjuntó foto"
                    }
    
                    # Convertir todo a strings para evitar problemas al guardar en Sheets
                    nuevo_ticket_serializable = {k: str(v) for k, v in nuevo_ticket.items()}
                    sheet.append_row(list(nuevo_ticket_serializable.values()))
    
                    st.success(f"✅ Reclamo #{nuevo_numero} creado exitosamente 🚀")
        


def modulo_cotizaciones_mauricio():
    st.title("📋 Gestión de Cotizaciones")

    hoja_cotizaciones = spreadsheet.worksheet("cotizaciones")
    cotizaciones_data = hoja_cotizaciones.get_all_records()
    cotizaciones_df = pd.DataFrame(cotizaciones_data)

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
        visualizar_tickets()

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
                    # Convertir a string y extraer los días
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
            
            # Mostrar la métrica
            st.metric("Tiempo Resolución Promedio", 
                      f"{tiempo_promedio:.1f} días" if tiempo_promedio is not None else "N/A")

        # Filtros
        st.subheader("Filtros")
        area = st.selectbox("Área", ["Todas"] + list(df['Área'].unique()))
        estado = st.selectbox("Estado", ["Todos"] + list(df['Estado'].unique()))

        # Aplicar filtros
        if area != "Todas":
            df = df[df['Área'] == area]
        if estado != "Todos":
            df = df[df['Estado'] == estado]

        # Mostrar datos
        st.dataframe(df, use_container_width=True, height=500)
        
        # Gráficos
        st.subheader("Estadísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.bar_chart(df['Área'].value_counts())
        with col2:
            st.bar_chart(df['Estado'].value_counts())
        st.subheader("Tiempo por Estado")
        df_resultados = procesar_tiempos_estado(df['Tiempo_Cambio'])
        if not df_resultados.empty:
            st.bar_chart(df_resultados.set_index('Estado'))
        else:
            st.warning("No hay datos de tiempo por estado")
        st.subheader("Actividad por Usuario")
        col1, col2 = st.columns(2)
        with col1:
            creados = df['Usuario_Creación'].value_counts()
            st.bar_chart(creados, use_container_width=True)
            st.caption("Tickets creados por usuario")
        with col2:
            modificados = df['Usuario_Modificacion'].value_counts()
            st.bar_chart(modificados, use_container_width=True)
            st.caption("Tickets modificados por usuario")
    else:
        st.warning("No se encontraron tickets")

# Función para manejar tickets
def manejar_tickets():
    df = cargar_datos()  # Cargar tickets existentes desde Google Sheets
    
    # Mostrar opciones
        # Mostrar opciones
    opcion_ticket = st.radio("Seleccione una acción:", ["Ver tickets en cola","Crear nuevo ticket", "Modificar ticket existente"])
    
    if opcion_ticket == "Ver tickets en cola":
        st.subheader("🔍 Ver tickets en cola")
        df = cargar_datos()
        
        if not df.empty:
            ultimos_registros = df.sort_values('Fecha_Modificacion').groupby('Número').last().reset_index()
            
            # Filtrar tickets donde el último en modificar fue cliente y no están cerrados
            tickets_cola = ultimos_registros[
                (ultimos_registros['Usuario_Modificacion'] == 'cliente') &
                (ultimos_registros['Estado'] != 'cerrado')
            ]
            
            if not tickets_cola.empty:
                st.metric("Tickets Pendientes", len(tickets_cola))
                
                # Mostrar tabla detallada
                st.dataframe(
                    tickets_cola[[
                        'Número', 'Título', 'Cliente', 'Estado', 
                        'Fecha_Modificacion', 'Usuario_Modificacion'
                    ]].sort_values('Fecha_Modificacion', ascending=False),
                    use_container_width=True,
                    height=400
                )
                
                # Botón para tomar ticket
                selected_ticket = st.number_input("Seleccionar Número de Ticket para gestionar:", min_value=min(tickets_cola['Número']))
                
                if st.button("Tomar Ticket"):
                    if selected_ticket in tickets_cola['Número'].values:
                        st.session_state.ticket_actual = tickets_cola[tickets_cola['Número'] == selected_ticket].iloc[0].to_dict()
                        st.success(f"Ticket #{selected_ticket} asignado para gestión")
                    else:
                        st.error("Número de ticket inválido")
            else:
                st.info("No hay tickets pendientes de clientes")
        else:
            st.warning("No se encontraron tickets")
        
    if opcion_ticket == "Crear nuevo ticket":
        with st.form("nuevo_ticket"):
            st.subheader("📝 Nuevo Ticket")
            titulo = st.text_input("Título del Ticket*")
            area = st.selectbox("Área*", ["crediprime", "generales"])
            estado = st.selectbox("Estado*", ["inicial", "documentacion pendiente", "documentacion enviada", "en reparacion"])
            descripcion = st.text_area("Descripción detallada*")
            
            if st.form_submit_button("Guardar Ticket"):
                if not all([titulo, area, estado, descripcion]):
                    st.error("Todos los campos marcados con * son obligatorios")
                else:
                    # Obtener el último número de ticket desde Google Sheets
                    if not df.empty:
                        ultimo_ticket = df['Número'].max()
                    else:
                        ultimo_ticket = 0
                    
                    nuevo_numero = ultimo_ticket+1
                    nuevo_numero =nuevo_numero.astype("float")
                   

                    # Crear registro
                    fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    nuevo_ticket = {
                        'Número': nuevo_numero,
                        'Título': titulo,
                        'Área': area,
                        'Estado': estado,
                        'Descripción': descripcion,
                        'Fecha_Creación': fecha_creacion,
                        'Usuario_Creación': st.session_state.usuario_actual,
                        'Fecha_Modificación': fecha_creacion,
                        'Usuario_Modificación': st.session_state.usuario_actual,
                        'Tiempo_Cambio': '0d'  # Sin cambios al principio
                    }

                    
                    # Guardar en Google Sheetssheet.append_row(list(nuevo_ticket.values()))

                    nuevo_ticket_serializable = {
                        key: (int(value) if isinstance(value, (pd.Int64Dtype, int, float)) else value)
                        for key, value in nuevo_ticket.items()
                    }
                    nuevo_ticket_serializable['Fecha_Creación'] = str(nuevo_ticket_serializable['Fecha_Creación'])
                    nuevo_ticket_serializable['Fecha_Modificación'] = str(nuevo_ticket_serializable['Fecha_Modificación'])

                    # Guardar en Google Sheets
                    # Aquí asumo que `sheet` es una instancia de tu hoja de Google Sheets autenticada
                    sheet.append_row(list(nuevo_ticket_serializable.values()))
                    st.success("Ticket creado correctamente!")
    
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
            with st.form("modificar_ticket"):
                st.subheader(f"✏️ Modificando Ticket #{st.session_state.ticket_actual['Número']}")
                
                nuevo_estado = st.selectbox(
                    "Nuevo estado:",
                    ["inicial", "documentacion pendiente", "documentacion enviada", "en reparacion", "cerrado"],
                    index=["creado por usuario","inicial", "documentacion pendiente", "documentacion enviada", "en reparacion", "cerrado"]
                        .index(st.session_state.ticket_actual['Estado'])
                )
                
                nueva_descripcion = st.text_area(
                    "Descripción actualizada:",
                    value=st.session_state.ticket_actual['Descripción']
                )
                
                if st.form_submit_button("Guardar Cambios"):
                    fecha_modificacion = datetime.now()
                    
                    # Calcular días desde última modificación
                    ultima_fecha = datetime.strptime(st.session_state.ticket_actual['Fecha_Creación'], "%Y-%m-%d %H:%M:%S")
                    dias_transcurridos = (fecha_modificacion - ultima_fecha).days
                    
                    # Usar flecha ASCII en lugar de Unicode
                    if nuevo_estado != st.session_state.ticket_actual['Estado']:
                        registro_dias = f"{dias_transcurridos}d ({st.session_state.ticket_actual['Estado']} -> {nuevo_estado})"
                    else:
                        registro_dias = "Sin cambio de estado"
                    
                    # Crear el registro actualizado
                    ticket_actualizado = {
                        'Número': st.session_state.ticket_actual['Número'],
                        'Título': st.session_state.ticket_actual['Título'],
                        'Área': st.session_state.ticket_actual['Área'],
                        'Estado': nuevo_estado,
                        'Descripción': nueva_descripcion,
                        'Fecha_Creación': st.session_state.ticket_actual['Fecha_Creación'],
                        'Usuario_Creación': st.session_state.ticket_actual['Usuario_Creación'],
                        'Fecha Modificación': fecha_modificacion.strftime('%Y-%m-%d %H:%M:%S'),
                        'Usuario_Modificacion': st.session_state.usuario_actual,
                        'Tiempo_Cambio': registro_dias,
                        'Cliente': st.session_state.ticket_actual['Cliente']
                        
                    }
                    
                    # Actualizar en Google Sheets
                    #sheet = auth_google_sheets()
                    row_index = df[df['Número'] == st.session_state.ticket_actual['Número']].index[0] + 2  # +2 porque la hoja tiene encabezado
                    sheet.append_row(list(ticket_actualizado.values()))
                    #sheet.update('A' + str(row_index), list(ticket_actualizado.values()))
                    st.success("Ticket actualizado correctamente!")
                    del st.session_state.ticket_actual

# Función para descargar datos
def descargar_tickets():
    df = cargar_datos()
    if not df.empty:
        formato = st.selectbox("Formato de descarga", ["CSV", "Excel", "JSON"])
        
        if formato == "CSV":
            st.download_button("Descargar CSV", df.to_csv(), "tickets.csv")
        elif formato == "Excel":
            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button("Descargar Excel", output.getvalue(), "tickets.xlsx")
        elif formato == "JSON":
            st.download_button("Descargar JSON", df.to_json(), "tickets.json")
        
        st.write("Vista previa:")
        st.dataframe(df.tail())
    else:
        st.warning("No hay datos para descargar")



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
