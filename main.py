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

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# Definir el alcance
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]

# Cargar las credenciales de Google desde los secretos de Streamlit
creds_dict = {
    "type": "service_account",
    "project_id": "tidy-arena-453718-r8",
    "private_key_id": st.secrets["general"]["private_key_id"],
    "private_key": st.secrets["general"]["private_key"],  # Aquí es donde Streamlit toma el secreto
    "client_email": st.secrets["general"]["client_email"],
    "client_id": st.secrets["general"]["client_id"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/insura2%40tidy-arena-453718-r8.iam.gserviceaccount.com"
}

# Convertir las credenciales a un formato JSON
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

# Autenticarse con Google
client = gspread.authorize(creds)
# Autenticación con la cuenta de servicio
#creds = Credentials.from_service_account_info(st.secrets["general"], scopes=SCOPES)
#client = gspread.authorize(creds)
spreadsheet = client.open_by_key("13hY8la9Xke5-wu3vmdB-tNKtY5D6ud4FZrJG2_HtKd8")
sheet = spreadsheet.sheet1
#sheet.update([["Columna1", "Columna2"], ["Dato1", "Dato2"]])  # Solo un ejemplo para verificar la escritura

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Tickets y Análisis",
    page_icon="📊",
    layout="wide"
)

#conn = st.connection("gsheets", type=GSheetsConnection)


# Configuración de usuarios y contraseñas
USUARIOS = {
    "wiga": "contraseña_secreta123",
    "admin": "admin123",
    "dany": "futbol123"
}

# Función de autenticación mejorada
def autenticacion():
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        with st.container():
            st.title("🔒 Inicio de Sesión")
            usuario = st.text_input("Usuario")
            contraseña = st.text_input("Contraseña", type="password")
            
            if st.button("Ingresar"):
                if USUARIOS.get(usuario) == contraseña:
                    st.session_state.autenticado = True
                    st.session_state.usuario_actual = usuario
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
        return False
    return True

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
    opcion_ticket = st.radio("Seleccione una acción:", ["Crear nuevo ticket", "Modificar ticket existente"])
    
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
    
    else:  # Modificar ticket
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
                    index=["inicial", "documentacion pendiente", "documentacion enviada", "en reparacion", "cerrado"]
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
                        'Usuario Modificación': st.session_state.usuario_actual,
                        'Tiempo_Cambio': registro_dias
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

# Flujo principal de la aplicación
if not autenticacion():
    st.stop()

st.sidebar.title("Menú")
opcion = st.sidebar.radio("Opciones", [
    "Inicio", 
    "Gestión de Tickets", 
    "Análisis", 
    "Descargar Datos",
    "Cerrar Sesión"
])

if opcion == "Inicio":
    st.title("🏠 Sistema de Gestión de Tickets")
    st.markdown("""
    **Bienvenido** a la plataforma de gestión de tickets.
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

elif opcion == "Cerrar Sesión":
    st.session_state.autenticado = False
    st.success("Sesión cerrada exitosamente")
    time.sleep(1)
    st.rerun()
