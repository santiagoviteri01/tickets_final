import streamlit as st
import pandas as pd
import numpy as np
matplotlib.use("Agg")  # Esto debe ir antes de importar pyplot
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configuración inicial
def mostrar_dashboard_analisis(pagados,pendientes,asegurados):    
    st.title('📊 Dashboard de Análisis de Seguros')
    if pagados is not None and pendientes is not None and asegurados is not None:
        # Procesamiento de datos de asegurados
        asegurados['FECHA'] = pd.to_datetime(asegurados['FECHA'], dayfirst=True, errors='coerce')
        asegurados['MES'] = asegurados['FECHA'].dt.month
        asegurados['MES_NOMBRE'] = asegurados['FECHA'].dt.month_name()
        asegurados['AÑO'] = asegurados['FECHA'].dt.year
        
        # Orden de meses y configuración temporal
        meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        mes_actual = datetime.now().month

        # Crear pestañas
        tab1, tab2, tab3, = st.tabs(["📈 Análisis de Suma Asegurada", "📊 Análisis de Reclamos", "Siniestralidad Mensual"])
                
        with tab1:
                        
            st.header("📈 Análisis de Suma Asegurada")
            
            # Sidebar controls
            with st.sidebar:
                st.header("Configuración del Análisis")
                
                # Filtros principales
                aseguradoras = ['Todas'] + sorted(asegurados['ASEGURADORA'].unique().tolist())
                aseguradora_sel = st.selectbox("Seleccionar Aseguradora", aseguradoras)
                
                años_disponibles = sorted(asegurados['AÑO'].unique())
                años_sel = st.multiselect("Seleccionar Años", años_disponibles, default=años_disponibles)
                
                # Controles de visualización
                bins_prima = st.slider("Bins para primas", 10, 100, 30)
                bins_suma = st.slider("Bins para suma asegurada", 10, 100, 30)
                top_n = st.slider("Top N Marcas", 5, 20, 10)
                tipo_grafico = st.radio("Tipo de gráfico", ["Líneas", "Barras"], index=0)
                metrica = st.selectbox("Métrica", ["Suma Asegurada", "Prima Total", "Pólizas"])

            # Filtrar datos
            df_filtrado = asegurados.copy()
            if aseguradora_sel != 'Todas':
                df_filtrado = df_filtrado[df_filtrado['ASEGURADORA'] == aseguradora_sel]
            
            if años_sel:
                df_filtrado = df_filtrado[df_filtrado['AÑO'].isin(años_sel)]
            else:
                st.warning("Selecciona al menos un año")
                st.stop()

            # Aplicar filtros temporales
            def aplicar_filtro_temporal(df, año):
                if año == 2023:
                    return df[df['MES'] >= 10]
                elif año == 2025:
                    return df[df['MES'] <= mes_actual]
                return df
            
            if len(años_sel) == 1:
                df_filtrado = aplicar_filtro_temporal(df_filtrado, años_sel[0])

            # Calcular métricas
            titulo_años = f"Años {', '.join(map(str, años_sel))}" if len(años_sel) > 1 else f"Año {años_sel[0]}"
            
            # Sección de métricas
            st.subheader(f"Métricas Clave - {titulo_años}")
            col1, col2, col3 = st.columns(3)
            with col1:
                total_asegurado = df_filtrado['VALOR ASEGURADO'].sum()
                st.metric("Suma Asegurada Total", f"${total_asegurado:,.2f}")
            with col2:
                prima_total = df_filtrado['PRIMA TOTAL VEHÍCULOS'].sum()
                st.metric("Prima Total", f"${prima_total:,.2f}")
            with col3:
                avg_valor = df_filtrado['VALOR ASEGURADO'].mean()
                st.metric("Valor Promedio", f"${avg_valor:,.2f}")

            # Sección de distribuciones
            st.subheader("Distribuciones")
            col4, col5 = st.columns(2)
            with col4:
                fig, ax = plt.subplots(figsize=(10,5))
                sns.histplot(df_filtrado['PRIMA TOTAL VEHÍCULOS'], bins=bins_prima, kde=True, color='orange')
                plt.title(f'Distribución de Primas ({titulo_años})')
                st.pyplot(fig)
            
            with col5:
                fig, ax = plt.subplots(figsize=(10,5))
                sns.histplot(df_filtrado['VALOR ASEGURADO'], bins=bins_suma, kde=True, color='teal')
                plt.title(f'Distribución de Suma Asegurada ({titulo_años})')
                st.pyplot(fig)

            # Evolución temporal
            st.subheader(f"Evolución de {metrica}")
            if metrica == "Suma Asegurada":
                col_metrica = 'VALOR ASEGURADO'
                funcion = 'sum'
            elif metrica == "Prima Total":
                col_metrica = 'PRIMA TOTAL VEHÍCULOS'
                funcion = 'sum'
            else:
                col_metrica = 'NÚMERO CERTIFICADO'
                funcion = 'count'

            df_temporal = df_filtrado.pivot_table(
                values=col_metrica,
                index='MES',
                columns='AÑO',
                aggfunc=funcion
            ).fillna(0).reindex(range(1,13))

            fig, ax = plt.subplots(figsize=(12,6))
            if tipo_grafico == "Líneas":
                for año in df_temporal.columns:
                    ax.plot(df_temporal.index, df_temporal[año], marker='o', label=año)
            else:
                width = 0.8 / len(df_temporal.columns)
                offsets = np.arange(1,13) - (0.4 - width/2)
                for i, año in enumerate(df_temporal.columns):
                    ax.bar(offsets + i*width, df_temporal[año], width=width, label=año)

            ax.set_xticks(range(1,13))
            ax.set_xticklabels(meses_orden, rotation=45)
            ax.set_xlabel("Mes")
            ax.set_ylabel(metrica)
            ax.legend(title="Año")
            ax.grid(True, linestyle='--', alpha=0.7)
            st.pyplot(fig)
            # Sección de Evolución Temporal
            # Sección de Evolución Temporal Continua

            st.subheader("📅 Evolución Continua desde Oct 2023")
            
            # Obtener fecha actual
            hoy = datetime.now()
            año_actual = hoy.year
            mes_actual = hoy.month
            
            # Crear rango de meses continuos desde Oct 2023 hasta el mes actual
            periodos = []
            current_year = 2023
            current_month = 10  # Comenzar en Octubre 2023
            
            while (current_year < año_actual) or (current_year == año_actual and current_month <= mes_actual):
                periodos.append(f"{meses_orden[current_month-1][:3]}-{current_year}")
                
                # Avanzar al siguiente mes
                current_month += 1
                if current_month > 12:
                    current_month = 1
                    current_year += 1
            
            # Filtrar y procesar los datos
            df_periodo = asegurados.copy()
            if aseguradora_sel != 'Todas':
                df_periodo = df_periodo[df_periodo['ASEGURADORA'] == aseguradora_sel]
            
            # Crear columna de periodo para agrupación
            df_periodo['Periodo'] = df_periodo['MES'].apply(lambda x: meses_orden[x-1][:3]) + '-' + df_periodo['AÑO'].astype(str)
            
            # Agrupar por periodo
            evolucion = df_periodo.groupby('Periodo').agg(
                Prima_Total=('PRIMA TOTAL VEHÍCULOS', 'sum'),
                Suma_Asegurada=('VALOR ASEGURADO', 'sum')
            ).reindex(periodos).fillna(0)
            
            # Crear figura con dos subplots (uno arriba, otro abajo)
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
            
            # --- PRIMER GRÁFICO (ARRIBA): PRIMA TOTAL ---
            sns.lineplot(
                x=evolucion.index,
                y=evolucion['Prima_Total'],
                marker='o',
                color='#FF6F00',
                label='Prima Total ($)',
                ax=ax1
            )
            
            # Configuración del primer gráfico
            ax1.set_title(f'Prima Total desde Oct 2023 hasta {meses_orden[mes_actual-1][:3]}-{año_actual}')
            ax1.set_xlabel('Periodo (Mes-Año)')
            ax1.set_ylabel('Monto ($)')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(True, linestyle='--', alpha=0.3)
            
            # Mostrar valores cada 3 meses
            for i, (periodo, row) in enumerate(evolucion.iterrows()):
                if i % 3 == 0:
                    ax1.text(periodo, row['Prima_Total'], f"${row['Prima_Total']/1e6:.1f}M", 
                            ha='center', va='bottom', color='#FF6F00')
            
            # --- SEGUNDO GRÁFICO (ABAJO): SUMA ASEGURADA ---
            sns.lineplot(
                x=evolucion.index,
                y=evolucion['Suma_Asegurada'],
                marker='o',
                color='#009688',
                label='Suma Asegurada ($)',
                ax=ax2
            )
            
            # Configuración del segundo gráfico
            ax2.set_title(f'Suma Asegurada desde Oct 2023 hasta {meses_orden[mes_actual-1][:3]}-{año_actual}')
            ax2.set_xlabel('Periodo (Mes-Año)')
            ax2.set_ylabel('Monto ($)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.grid(True, linestyle='--', alpha=0.3)
            
            # Mostrar valores cada 3 meses
            for i, (periodo, row) in enumerate(evolucion.iterrows()):
                if i % 3 == 0:
                    ax2.text(periodo, row['Suma_Asegurada'], f"${row['Suma_Asegurada']/1e6:.1f}M", 
                            ha='center', va='bottom', color='#009688')
            
            # Ajustar espacio entre gráficos
            plt.tight_layout()
            
            # Mostrar los gráficos en Streamlit
            st.pyplot(fig)



            # Tabla detallada
            st.subheader("Detalle por Mes")
            tabla_detalle = df_temporal.copy()
            tabla_detalle.index = meses_orden
            st.dataframe(tabla_detalle.style.format("${:,.2f}"), use_container_width=True)
            
            # Sección de Tasa Mensual
            st.subheader("📉 Análisis de Tasa Mensual")
    
            # Calcular prima total y suma asegurada por mes
            tasa_mensual = df_filtrado.groupby(['AÑO', 'MES']).agg(
               Prima_Total=('PRIMA TOTAL VEHÍCULOS', 'sum'),
               Suma_Asegurada_Total=('VALOR ASEGURADO', 'sum')
            ).reset_index()
    
            # Calcular tasa
            tasa_mensual['Tasa'] = (tasa_mensual['Prima_Total'] / tasa_mensual['Suma_Asegurada_Total']) * 100
    
            # Control en sidebar para agrupar por año
            with st.sidebar:
               agrupar_por_año = st.checkbox("Mostrar tasa agrupada por año", value=True)
    
            # Preparar datos para visualización
            if agrupar_por_año:
               tasa_mensual['Periodo'] = tasa_mensual['MES'].astype(str) + '-' + tasa_mensual['AÑO'].astype(str)
               orden_periodos = sorted(tasa_mensual['Periodo'].unique(), 
                                 key=lambda x: (int(x.split('-')[1]), int(x.split('-')[0])))
            else:
               tasa_mensual = tasa_mensual.groupby('MES').agg(
                  Prima_Total=('Prima_Total', 'sum'),
                  Suma_Asegurada_Total=('Suma_Asegurada_Total', 'sum')
               ).reset_index()
               tasa_mensual['Tasa'] = (tasa_mensual['Prima_Total'] / tasa_mensual['Suma_Asegurada_Total']) * 100
               tasa_mensual['Periodo'] = tasa_mensual['MES'].apply(lambda x: meses_orden[x-1])
               orden_periodos = meses_orden
    
            # Gráfico de Tasa Mensual
            fig_tasa, ax_tasa = plt.subplots(figsize=(12, 6))
            sns.lineplot(
               x='Periodo', 
               y='Tasa', 
               data=tasa_mensual,
               marker='o',
               color='purple',
               ax=ax_tasa
            )
    
            plt.title(f'Tasa Mensual ({titulo_años})')
            plt.xlabel('Mes' if not agrupar_por_año else 'Mes-Año')
            plt.ylabel('Tasa (%)')
            plt.xticks(rotation=45)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.ylim(0, tasa_mensual['Tasa'].max() * 1.1)
            st.pyplot(fig_tasa)
    
            # Tabla detallada de tasas
            st.subheader("Detalle de Tasas Mensuales")
    
            # Formatear tabla
            tasa_detalle = tasa_mensual[['Periodo', 'Prima_Total', 'Suma_Asegurada_Total', 'Tasa']].copy()
            tasa_detalle['Tasa'] = tasa_detalle['Tasa'].round(2)
            tasa_detalle['Prima_Total'] = tasa_detalle['Prima_Total'].apply(lambda x: f"${x:,.2f}")
            tasa_detalle['Suma_Asegurada_Total'] = tasa_detalle['Suma_Asegurada_Total'].apply(lambda x: f"${x:,.2f}")
            tasa_detalle['Tasa'] = tasa_detalle['Tasa'].apply(lambda x: f"{x}%")
    
            st.dataframe(
               tasa_detalle.style.set_properties(**{
                  'text-align': 'center',
                  'font-size': '12px'
               }).set_table_styles([{
                  'selector': 'th',
                  'props': [('background-color', '#f0f2f6'), ('font-weight', 'bold')]
               }]), 
               use_container_width=True,
               hide_index=True
            )

            # Top Marcas
            st.subheader(f"Top {top_n} Marcas ({titulo_años})")
            top_marcas = df_filtrado['MARCA'].value_counts().nlargest(top_n)
    
            fig_marcas, ax_marcas = plt.subplots(figsize=(12, 6))
            sns.barplot(x=top_marcas.values, y=top_marcas.index, palette="viridis", ax=ax_marcas)
            ax_marcas.set_xlabel("Cantidad de Pólizas")
            ax_marcas.set_ylabel("Marca")
            ax_marcas.set_title(f"Top {top_n} Marcas con Más Pólizas")
    
            for i, v in enumerate(top_marcas.values):
               ax_marcas.text(v + 3, i, str(v), color='black', va='center')
    
            st.pyplot(fig_marcas)

  
        
        with tab2:
            orden_meses=meses_orden
            resumen_aseguradoras_total = pagados.groupby('COMPAÑÍA').agg(
                Media_Reclamo=('VALOR RECLAMO', 'mean'),
                Mediana_Reclamo=('VALOR RECLAMO', 'median'),
                Total_Reclamo=('VALOR RECLAMO', 'sum'),
                Media_Deducible=('DEDUCIBLE', 'mean')
            ).round(2)
            # --- ANÁLISIS DE RECLAMOS ---
            # Sidebar para controles
            with st.sidebar:
                st.header("Configuración del Análisis")
                año_analisis = st.selectbox("Seleccionar Año", [2024, 2025], key="año_reclamos")
                top_n = st.slider("Top N Marcas", 3, 10, 5, key="top_n")
                bins_hist = st.slider("Bins para Histograma", 10, 100, 30, key="bins_hist")
                if len(resumen_aseguradoras_total) >= 1:
                    aseguradoras_seleccionadas = st.multiselect(
                        "Selecciona las aseguradoras para comparar",
                        options=resumen_aseguradoras_total.index.tolist(),
                        default=resumen_aseguradoras_total.index.tolist()[:2]
                    )
                else:
                    st.warning("No hay suficientes aseguradoras en los datos para generar el gráfico.")
                    
            # Sección 1: Estructura de datos
            #pagados_filtrados = pagados[pagados['BASE'] == año_analisis]
            #pendientes_filtrados = pendientes[pendientes['BASE'] == año_analisis]
            
            pagados_filtrados = pagados[pagados['BASE'] == año_analisis].reset_index(drop=True)
            pendientes_filtrados = pendientes[pendientes['BASE'] == año_analisis].reset_index(drop=True)


            pagos_aseguradora_data = (
                pagados_filtrados[pagados_filtrados['COMPAÑÍA'].isin(aseguradoras_seleccionadas)]
                .reset_index(drop=True)
            )
            
            pendientes_aseguradora_data = (
                pendientes_filtrados[pendientes_filtrados['CIA. DE SEGUROS'].isin(aseguradoras_seleccionadas)]
                .reset_index(drop=True)
            )

            st.header("📁 Estructura de Datos")
            st.subheader("Reclamos Pagados")
            st.write(f"Registros: {pagos_aseguradora_data.shape[0]} | Columnas: {pagos_aseguradora_data.shape[1]}")
            st.dataframe(pagos_aseguradora_data.head(3), use_container_width=True,hide_index=True)
                
            st.subheader("Reclamos Pendientes")
            st.write(f"Registros: {pendientes_aseguradora_data.shape[0]} | Columnas: {pendientes_aseguradora_data.shape[1]}")
            st.dataframe(pendientes_aseguradora_data.head(3), use_container_width=True,hide_index=True)

            # Sección 2: Análisis temporal ordenado
            st.header("📅 Distribución Temporal")
            
            # Convertir y ordenar meses
            pagos_aseguradora_data['FECHA SINIESTRO'] = pd.to_datetime(pagos_aseguradora_data['FECHA SINIESTRO'])
            pagos_aseguradora_data['MES'] = pagos_aseguradora_data['FECHA SINIESTRO'].dt.month
            #pagos_aseguradora_data['MES'] = pd.Categorical(pagos_aseguradora_data['MES'], categories=orden_meses, ordered=True)
            
            # Crear el gráfico con Seaborn (más control)
            plt.figure(figsize=(12, 6))
            ax = sns.countplot(
                data=pagos_aseguradora_data,
                x='MES',
                palette='viridis'
            )
            
            # Personalización
            plt.title('Reclamos por Mes (Orden Cronológico) 🗓️', fontsize=14, fontweight='bold')
            plt.xlabel('Mes', fontsize=12)
            plt.ylabel('Cantidad de Reclamos', fontsize=12)
            plt.xticks(rotation=45, ha='right')
            
            # Añadir etiquetas de valores
            for p in ax.patches:
                ax.annotate(
                    f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 5), textcoords='offset points'
                )
            
            st.pyplot(plt.gcf())

            # Sección 3: Análisis de valores
            st.header("💰 Análisis de Valores")
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                # Histograma interactivo
                st.subheader("Distribución de Valores")
                fig = plt.figure(figsize=(10, 5))
                sns.histplot(pagos_aseguradora_data['VALOR RECLAMO'], bins=bins_hist, kde=True)
                plt.title('Distribución de Valores Reclamados')
                st.pyplot(fig)
                
            with col4:
                # Boxplot mejorado
                st.subheader("Diagrama de Caja")
                fig = plt.figure(figsize=(10, 5))
                sns.boxplot(x=pagos_aseguradora_data['VALOR RECLAMO'], color='lightgreen', whis=1.5)
                plt.title('Distribución de Valores (Boxplot)')
                st.pyplot(fig)
                
            with col5:
                # Creación de rangos
                st.subheader("Distribución por Rangos")

                # Slider para seleccionar el número de bins
                min_val = int(pagos_aseguradora_data['VALOR RECLAMO'].min())
                max_val = int(pagos_aseguradora_data['VALOR RECLAMO'].max())
                bin_size = st.slider(
                    "Selecciona el tamaño de los bins (en $)", 
                    min_value=500, 
                    max_value=max_val, 
                    value=500,
                    step=500
                )

                # Crear los bins dinámicamente
                bins = list(range(0, max_val + bin_size, bin_size))
                if bins[-1] < max_val:
                    bins.append(max_val + 1)

                bins = sorted(set(bins))
                labels = [f"{bins[i]} - {bins[i+1]}" for i in range(len(bins)-1)]

                pagos_aseguradora_data['Rango'] = pd.cut(pagos_aseguradora_data['VALOR RECLAMO'], bins=bins, labels=labels, right=False)

                fig, ax = plt.subplots(figsize=(10, 6))
                sns.countplot(y='Rango', data=pagos_aseguradora_data, order=labels, color='salmon', ax=ax)
                plt.title('Distribución por Rangos de Valores')
                plt.xlabel('Cantidad')
                plt.ylabel('Rango de Valores ($)')
                plt.grid(axis='x', linestyle='--', alpha=0.7)
                st.pyplot(fig)
            
            st.header("🏢 Comparativa entre Aseguradoras")
                    
            resumen_aseguradoras = pagos_aseguradora_data.groupby('COMPAÑÍA').agg(
                Media_Reclamo=('VALOR RECLAMO', 'mean'),
                Mediana_Reclamo=('VALOR RECLAMO', 'median'),
                Total_Reclamo=('VALOR RECLAMO', 'sum'),
                Media_Deducible=('DEDUCIBLE', 'mean')
            ).round(2)

            st.dataframe(
                resumen_aseguradoras.style.background_gradient(cmap='Blues'), 
                use_container_width=True
            )
            
            col6, col7 = st.columns(2)
            with col6:
                    st.subheader("Distribución de Pagos por Aseguradora")
                    if aseguradoras_seleccionadas:
                        fig, ax = plt.subplots(figsize=(10, 6))
                        colores = ['skyblue', 'salmon', 'lightgreen', 'orange', 'purple', 'pink']

                        for i, aseguradora in enumerate(aseguradoras_seleccionadas):
                            pagos_aseguradora = pagados_filtrados[pagados_filtrados['COMPAÑÍA'] == aseguradora]['VALOR RECLAMO']
                            sns.histplot(pagos_aseguradora, bins=30, color=colores[i % len(colores)], label=aseguradora, kde=True, ax=ax)

                        plt.title('Distribución de Pagos por Aseguradora')
                        plt.xlabel('Valor Reclamado')
                        plt.ylabel('Frecuencia')
                        plt.legend(title="Aseguradoras")
                        st.pyplot(fig)
                    else:
                        st.warning("Selecciona al menos una aseguradora para generar el gráfico.")

            with col7:
                pagos_aseguradoras = pagados_filtrados.groupby('COMPAÑÍA')['VALOR RECLAMO'].sum()
                fig, ax = plt.subplots(figsize=(2, 2))
                pagos_aseguradoras.plot(kind='pie', autopct='%1.1f%%', startangle=90, ax=ax, labels=None)
                plt.ylabel('')
                plt.legend(pagos_aseguradoras.index, title="Aseguradoras", loc="center left", bbox_to_anchor=(1, 0.5))
                st.pyplot(fig)
            
            # Sección 4: Análisis de variables categóricas
            st.header("📈 Análisis de Variables Categóricas")

            col8, col9 = st.columns(2)

            with col8:
                if aseguradoras_seleccionadas:
                    pagos_aseguradora_data = pagados_filtrados[pagados_filtrados['COMPAÑÍA'].isin(aseguradoras_seleccionadas)]
                    st.subheader("Distribución de Eventos")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.countplot(y='EVENTO', data=pagos_aseguradora_data, order=pagos_aseguradora_data['EVENTO'].value_counts().index, palette='viridis')
                    plt.title('Frecuencia de Eventos')
                    plt.xlabel('Frecuencia')
                    plt.ylabel('Evento')
                    st.pyplot(fig)
                else:
                        st.warning("Selecciona al menos una aseguradora para generar el gráfico.")
                    
            with col9:
                if aseguradoras_seleccionadas:
                    st.subheader("Top 10 Talleres de Reparación")
                    top_talleres = pagos_aseguradora_data['TALLER DE REPARACION'].value_counts().nlargest(10)
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(x=top_talleres.values, y=top_talleres.index, palette='magma')
                    plt.title('Top 10 Talleres de Reparación')
                    plt.xlabel('Frecuencia')
                    plt.ylabel('Taller de Reparación')
                    st.pyplot(fig)
                else:
                    st.warning("Selecciona al menos una aseguradora para generar el gráfico.")

            col10, col11 = st.columns(2)
            with col10:
                if aseguradoras_seleccionadas:
                    st.subheader("Distribución por Ciudad de Ocurrencia")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.countplot(y='CIUDAD OCURRENCIA', data=pagos_aseguradora_data, order=pagos_aseguradora_data['CIUDAD OCURRENCIA'].value_counts().index, palette='plasma')
                    plt.title('Frecuencia por Ciudad de Ocurrencia')
                    plt.xlabel('Frecuencia')
                    plt.ylabel('Ciudad de Ocurrencia')
                    st.pyplot(fig)
                else:
                    st.warning("Selecciona al menos una aseguradora para generar el gráfico.")

            with col11:
                if aseguradoras_seleccionadas:
                    st.subheader("Marcas con Más Reclamos")
                    top_marcas = pagos_aseguradora_data['MARCA'].value_counts().nlargest(10)
                    fig, ax = plt.subplots(figsize=(10, 6))
                    top_marcas.plot(kind='bar', color='skyblue', ax=ax)
                    plt.title('Top 10 Marcas con Más Reclamos')
                    plt.xlabel('Marca')
                    plt.ylabel('Cantidad de Reclamos')
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
            
            # Sección 5: Análisis de pendientes
            st.header("⏳ Reclamos Pendientes")
            
            col12, col13 = st.columns(2)
            
            with col12:
                st.subheader("Estados Actuales")
                estados = pendientes_filtrados['ESTADO ACTUAL'].value_counts()
                fig = plt.figure(figsize=(8, 8))
                plt.pie(estados, labels=estados.index, autopct='%1.1f%%')
                plt.title('Distribución de Estados')
                st.pyplot(fig)
            
            with col13:
                st.subheader("Tiempo de Resolución")
                if 'FECHA DE SINIESTRO' in pendientes_filtrados.columns:
                    pendientes_filtrados['DIAS PENDIENTES'] = (pd.to_datetime('today') - pd.to_datetime(pendientes_filtrados['FECHA DE SINIESTRO'], dayfirst=True, errors='coerce')).dt.days
                    avg_dias = pendientes_filtrados['DIAS PENDIENTES'].mean().round(1)
                    st.metric("Días promedio pendientes", f"{avg_dias} días")
                    fig = plt.figure(figsize=(10, 4))
                    sns.histplot(pendientes_filtrados['DIAS PENDIENTES'], bins=20, kde=True)
                    plt.title('Distribución de Días Pendientes')
                    st.pyplot(fig)
                else:
                    st.warning("Columna 'FECHA DE SINIESTRO' no encontrada")

            # Sección 6: Generar informe
            st.header("📄 Generar Informe Anual")
            
            if st.button("Generar Informe"):
                #pagados_filtrados = pagados[pagados['BASE'] == año_analisis]
                #pendientes_filtrados = pendientes[pendientes['BASE'] == año_analisis]
                #pagados_filtrados = pagados[pagados['BASE'] == año_analisis]
                #pendientes_filtrados = pendientes[pendientes['BASE'] == año_analisis]
                resumen_mes = pd.pivot_table(
                    pagados_filtrados,
                    values='VALOR RECLAMO',
                    index='MES',
                    columns='COMPAÑÍA',
                    aggfunc=['sum', 'count'],
                    fill_value=0,
                    margins=True
                )

                resumen_mes.columns = [
                    f"{aggfunc} {compañía}" 
                    for aggfunc, compañía in resumen_mes.columns
                ]

                talleres = pd.pivot_table(
                    pagados_filtrados,
                    values='VALOR RECLAMO',
                    index='TALLER DE REPARACION',
                    columns='COMPAÑÍA',
                    aggfunc='count',
                    fill_value=0
                ).astype(int)

                causas = pd.pivot_table(
                    pagados_filtrados,
                    values='VALOR RECLAMO',
                    index='EVENTO',
                    aggfunc=['sum', 'count'],
                    fill_value=0
                )

                causas.columns = ['Total_Reclamo', 'Cantidad_Reclamos']

                pendientes_estado = pd.pivot_table(
                    pendientes_filtrados,
                    values='VALOR SINIESTRO',
                    index='ESTADO ACTUAL',
                    columns='CIA. DE SEGUROS',
                    aggfunc='count',
                    fill_value=0
                )
    
                st.subheader("Resumen por Mes y Aseguradora")
                st.write(resumen_mes.style.background_gradient(cmap='Blues'))

                st.subheader("Total reclamos por Taller")
                st.write(talleres)

                st.subheader("Causas de siniestro")
                st.write(causas)

                st.subheader("Pendientes por Estado")
                st.write(pendientes_estado)

                nombre_archivo = f"Reporte_Retorno_{año_analisis}.xlsx"
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    resumen_mes.to_excel(writer, sheet_name='Resumen Mes')
                    talleres.to_excel(writer, sheet_name='Talleres')
                    causas.to_excel(writer, sheet_name='Causas')
                    pendientes_estado.to_excel(writer, sheet_name='Pendientes')
            
                output.seek(0)  # Muy importante: volver al inicio del archivo para descargarlo
            
                st.success(f"Reporte {año_analisis} generado.")
            
                # Ahora sí: ofrecer el botón de descarga
                st.download_button(
                    label="Descargar Reporte",
                    data=output,
                    file_name=f"Reporte_Retorno_{año_analisis}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with tab3:
            # --- ANÁLISIS DE SINIESTRALIDAD ---
            st.header("📉 Siniestralidad Mensual por Aseguradora")
            mapeo_columnas = {
                'CIA. DE SEGUROS': 'COMPAÑÍA',
                'VALOR SINIESTRO': 'VALOR RECLAMO',
                'FECHA DE SINIESTRO': 'FECHA SINIESTRO'
            }
            
            pendientes_estandarizado = pendientes.rename(columns=mapeo_columnas)
            
            #print(asegurados)
            # 1. Obtener valor asegurado
            valor_asegurado = asegurados.groupby(['ASEGURADORA', 'AÑO', 'MES']).agg(
                Prima_Vehiculos=('PRIMA VEHÍCULOS', 'sum')
            ).reset_index()
            #print(valor_asegurado)
            # 2. Combinar datos de reclamos
            df_completo = pd.concat([
                pagados[['COMPAÑÍA', 'FECHA SINIESTRO', 'VALOR RECLAMO']],
                pendientes_estandarizado[['COMPAÑÍA', 'FECHA SINIESTRO', 'VALOR RECLAMO']]
            ])
            
            reclamos = df_completo.copy()
            reclamos['FECHA_SINIESTRO'] = pd.to_datetime(reclamos['FECHA SINIESTRO'], errors='coerce')
            reclamos = reclamos.dropna(subset=['FECHA_SINIESTRO'])
            
            # Extraer año y mes
            reclamos['AÑO'] = reclamos['FECHA_SINIESTRO'].dt.year
            reclamos['MES'] = reclamos['FECHA_SINIESTRO'].dt.month
            
            # Agrupar reclamos
            reclamos_agrupados = reclamos.groupby(['COMPAÑÍA', 'AÑO', 'MES']).agg(
                Total_Reclamos=('VALOR RECLAMO', 'count'),
                Monto_Total_Reclamos=('VALOR RECLAMO', 'sum')
            ).reset_index()
            
            # 3. Unificar nombres y combinar datos
            reclamos_agrupados = reclamos_agrupados.rename(columns={'COMPAÑÍA': 'ASEGURADORA'})
            
            df_siniestralidad = pd.merge(
                valor_asegurado,
                reclamos_agrupados,
                on=['ASEGURADORA', 'AÑO', 'MES'],
                how='left'
            ).fillna(0)
            
            # 4. Calcular ratio y periodo
            df_siniestralidad['Siniestralidad'] = np.where(
                df_siniestralidad['Prima_Vehiculos'] > 0,
                df_siniestralidad['Monto_Total_Reclamos'] / df_siniestralidad['Prima_Vehiculos'],
                0
            )
            
            df_siniestralidad['PERIODO'] = df_siniestralidad['AÑO'].astype(str) + '-' + df_siniestralidad['MES'].astype(str).str.zfill(2)
            df_siniestralidad['FECHA'] = pd.to_datetime(df_siniestralidad['AÑO'].astype(str) + '-' + df_siniestralidad['MES'].astype(str) + '-01')
            
            # 5. Selectores interactivos (con opción "Todos")
            col1, col2 = st.columns(2)
            with col1:
                años_disponibles = sorted(df_siniestralidad['AÑO'].unique(), reverse=True)
                año_sel = st.selectbox(
                    "Año de análisis",
                    options=['Todos'] + años_disponibles,
                    key='sini_año'
                )
            with col2:
                aseguradora_sel = st.selectbox(
                    "Aseguradora",
                    options=['Todas'] + sorted(df_siniestralidad['ASEGURADORA'].unique()),
                    key='sini_aseguradora'
                )
            
            # 6. Filtrar datos
            if año_sel == 'Todos':
                df_filtrado = df_siniestralidad.copy()
            else:
                df_filtrado = df_siniestralidad[df_siniestralidad['AÑO'] == int(año_sel)]
            
            if aseguradora_sel != 'Todas':
                df_filtrado = df_filtrado[df_filtrado['ASEGURADORA'] == aseguradora_sel]
            else:
                # Agrupar por periodo (sumando todas aseguradoras)
                group_cols = ['PERIODO', 'AÑO', 'MES', 'FECHA'] if año_sel == 'Todos' else ['PERIODO', 'AÑO', 'MES']
                df_filtrado = df_filtrado.groupby(group_cols).agg({
                    'Prima_Vehiculos': 'sum',
                    'Total_Reclamos': 'sum',
                    'Monto_Total_Reclamos': 'sum'
                }).reset_index()
                
                df_filtrado['Siniestralidad'] = np.where(
                    df_filtrado['Prima_Vehiculos'] > 0,
                    df_filtrado['Monto_Total_Reclamos'] / df_filtrado['Prima_Vehiculos'],
                    0
                )
            #print(df_filtrado)
            # Ordenar por fecha cronológica
            #df_filtrado = df_filtrado.sort_values('FECHA')
            #print(df_filtrado)
            # 7. Gráfico de siniestralidad
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # Línea de siniestralidad
            sns.lineplot(
                data=df_filtrado,
                x='PERIODO',
                y='Siniestralidad',
                marker='o',
                color='#E53935',
                ax=ax
            )
            ax.set_ylabel("Ratio Siniestralidad", color='#E53935')
            ax.tick_params(axis='y', colors='#E53935')
            
            # Ajustar etiquetas del eje X según cantidad de periodos
            num_periodos = len(df_filtrado['PERIODO'].unique())
            rotation = 45 if num_periodos > 6 else 0
            step = max(1, num_periodos // 12)  # Mostrar aproximadamente 12 etiquetas
            
            ax.set_xticks(df_filtrado['PERIODO'].unique()[::step])
            ax.set_xticklabels(df_filtrado['PERIODO'].unique()[::step], rotation=rotation)
            
            # Barras para reclamos (solo si no es "Todas")
            if aseguradora_sel != 'Todas':
                ax2 = ax.twinx()
                sns.barplot(
                    data=df_filtrado,
                    x='PERIODO',
                    y='Monto_Total_Reclamos',
                    color='#1E88E5',
                    alpha=0.3,
                    ax=ax2
                )
                ax2.set_ylabel("Monto Total Reclamos ($)", color='#1E88E5')
                ax2.tick_params(axis='y', colors='#1E88E5')
            
            titulo = f'Siniestralidad {"por Aseguradora" if aseguradora_sel != "Todas" else "Acumulada"}'
            titulo += f" ({'Histórico Completo' if año_sel == 'Todos' else año_sel})"
            plt.title(titulo)
            st.pyplot(fig)
            
            # 8. Tabla resumen
            st.subheader("📊 Datos Detallados")
            
            if aseguradora_sel != 'Todas':
                columns_to_show = ['PERIODO', 'ASEGURADORA', 'Prima_Vehiculos', 'Total_Reclamos', 'Monto_Total_Reclamos', 'Siniestralidad']
            else:
                columns_to_show = ['PERIODO', 'Prima_Vehiculos', 'Total_Reclamos', 'Monto_Total_Reclamos', 'Siniestralidad']
            
            st.dataframe(
                df_filtrado[columns_to_show]
                .style.format({
                    'Prima_Vehiculos': '${:,.2f}',
                    'Total_Reclamos': '{:,.0f}',
                    'Monto_Total_Reclamos': '${:,.2f}',
                    'Siniestralidad': '{:.2%}'
                })
                .background_gradient(subset=['Siniestralidad'], cmap='Reds'),
                use_container_width=True,
                height=400
            )
            
            # 9. KPIs destacados
            st.subheader("🔍 Indicadores Clave")
            
            if not df_filtrado.empty:
                ultimo_mes = df_filtrado.iloc[-1]
                primer_mes = df_filtrado.iloc[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Periodo Inicial", primer_mes['PERIODO'])
                with col2:
                    st.metric("Periodo Final", ultimo_mes['PERIODO'])
                with col3:
                    st.metric("Total Periodos", len(df_filtrado))
                
                col4, col5, col6 = st.columns(3)
                with col4:
                    st.metric("Prima Vehículos Promedio", f"${df_filtrado['Prima_Vehiculos'].mean():,.2f}")
                with col5:
                    st.metric("Siniestralidad Promedio", f"{df_filtrado['Siniestralidad'].mean():.2%}")
                with col6:
                    st.metric("Total Reclamos", f"{df_filtrado['Total_Reclamos'].sum():,.0f}")
    else:
        st.warning("Por favor verifica que los DataFrames no estén vacíos.")
