import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración inicial
def mostrar_dashboard_analisis(pagados, pendientes, asegurados):
    st.title("📊 Dashboard Optimizado de Análisis de Seguros")

    if any(df is None or df.empty for df in [pagados, pendientes, asegurados]):
        st.warning("Por favor verifica que los DataFrames no estén vacíos.")
        return

    tab1, tab2, tab3 = st.tabs(["🔍 Suma Asegurada", "📁 Reclamos", "🔥 Siniestralidad"])

    with tab1:
        asegurados['FECHA'] = pd.to_datetime(asegurados['FECHA'], dayfirst=True, errors='coerce')
        asegurados['MES'] = asegurados['FECHA'].dt.month
        asegurados['MES_NOMBRE'] = asegurados['FECHA'].dt.month_name()
        asegurados['AÑO'] = asegurados['FECHA'].dt.year
    
        meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        mes_actual = datetime.now().month
    
        st.header("📈 Análisis de Suma Asegurada")
        with st.sidebar:
            st.header("⚙️ Configuración")
            aseguradoras = ['Todas'] + sorted(asegurados['ASEGURADORA'].dropna().unique().tolist())
            aseguradora_sel = st.selectbox("Seleccionar Aseguradora", aseguradoras)
    
            años_disponibles = sorted(asegurados['AÑO'].dropna().unique())
            años_sel = st.multiselect("Seleccionar Años", años_disponibles, default=años_disponibles)
    
            mostrar_graficos = st.multiselect("Gráficos a mostrar", [
                "Distribuciones", "Evolución Anual", "Evolución Continua", "Tasa Mensual", "Top Marcas"])
    
        df_filtrado = asegurados.copy()
        if aseguradora_sel != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['ASEGURADORA'] == aseguradora_sel]
    
        if años_sel:
            df_filtrado = df_filtrado[df_filtrado['AÑO'].isin(años_sel)]
        else:
            st.warning("Selecciona al menos un año")
            st.stop()
    
        titulo_años = f"{', '.join(map(str, años_sel))}" if len(años_sel) > 1 else f"{años_sel[0]}"
    
        st.subheader(f"📊 Métricas Clave - {titulo_años}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Suma Asegurada Total", f"${df_filtrado['VALOR ASEGURADO'].sum():,.2f}")
        with col2:
            st.metric("Prima Total", f"${df_filtrado['PRIMA TOTAL VEHÍCULOS'].sum():,.2f}")
        with col3:
            st.metric("Valor Promedio Asegurado", f"${df_filtrado['VALOR ASEGURADO'].mean():,.2f}")

        if "Distribuciones" in mostrar_graficos:
            st.subheader("📉 Distribuciones")
            col4, col5 = st.columns(2)
            with col4:
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.histplot(df_filtrado['PRIMA TOTAL VEHÍCULOS'], kde=True, bins=30, ax=ax, color='orange')
                ax.set_title("Distribución de Prima Total")
                ax.set_xlabel("Prima Total ($)")
                ax.set_ylabel("Frecuencia")
                st.pyplot(fig)
            with col5:
                fig, ax = plt.subplots(figsize=(8, 4))
                sns.histplot(df_filtrado['VALOR ASEGURADO'], kde=True, bins=30, ax=ax, color='teal')
                ax.set_title("Distribución de Valor Asegurado")
                ax.set_xlabel("Valor Asegurado ($)")
                ax.set_ylabel("Frecuencia")
                st.pyplot(fig)

        if "Evolución Anual" in mostrar_graficos:
            st.subheader("📈 Evolución Anual")
            df_temporal = df_filtrado.pivot_table(
                values='VALOR ASEGURADO', index='MES', columns='AÑO', aggfunc='sum'
            ).fillna(0).reindex(range(1, 13))
            df_temporal.index = pd.Categorical(
                [meses_orden[m-1] for m in df_temporal.index], categories=meses_orden, ordered=True
            )
            st.line_chart(df_temporal)
        
        if "Evolución Continua" in mostrar_graficos:
            st.subheader("📅 Evolución Continua desde Oct 2023")
            hoy = datetime.now()
            df_periodo = asegurados.copy()
            if aseguradora_sel != 'Todas':
                df_periodo = df_periodo[df_periodo['ASEGURADORA'] == aseguradora_sel]
        
            df_periodo['Periodo'] = df_periodo['MES'].apply(lambda x: meses_orden[x-1][:3]) + '-' + df_periodo['AÑO'].astype(str)
        
            # Generar orden correcto de periodos
            periodos_ordenados = df_periodo.sort_values(['AÑO', 'MES'])['Periodo'].unique()
            df_periodo['Periodo'] = pd.Categorical(df_periodo['Periodo'], categories=periodos_ordenados, ordered=True)
        
            evolucion = df_periodo.groupby('Periodo').agg(
                Prima_Total=('PRIMA TOTAL VEHÍCULOS', 'sum'),
                Suma_Asegurada=('VALOR ASEGURADO', 'sum')
            ).fillna(0)
            st.line_chart(evolucion)
        
        if "Tasa Mensual" in mostrar_graficos:
            st.subheader("📉 Tasa Mensual")
            tasa_mensual = df_filtrado.groupby(['AÑO', 'MES']).agg(
                Prima_Total=('PRIMA TOTAL VEHÍCULOS', 'sum'),
                Suma_Asegurada_Total=('VALOR ASEGURADO', 'sum')
            ).reset_index()
            tasa_mensual['Tasa'] = (tasa_mensual['Prima_Total'] / tasa_mensual['Suma_Asegurada_Total']) * 100
            tasa_mensual['Periodo'] = tasa_mensual['MES'].apply(lambda x: meses_orden[x-1]) + '-' + tasa_mensual['AÑO'].astype(str)
        
            # Orden correcto
            tasa_mensual = tasa_mensual.sort_values(['AÑO', 'MES'])
            tasa_mensual['Periodo'] = pd.Categorical(tasa_mensual['Periodo'], categories=tasa_mensual['Periodo'].unique(), ordered=True)
        
            st.line_chart(tasa_mensual.set_index('Periodo')['Tasa'])
    
        if "Top Marcas" in mostrar_graficos:
            st.subheader("🏅 Top Marcas")
            top_marcas = df_filtrado['MARCA'].value_counts().nlargest(10)
            st.bar_chart(top_marcas)


    with tab2:
        st.sidebar.header("📁 Reclamos")
        pagados['MES'] = pd.to_datetime(pagados['FECHA SINIESTRO'], errors='coerce').dt.month

        if st.sidebar.checkbox("Distribución por Mes", True):
            reclamos_mes = pagados['MES'].value_counts().sort_index()
            st.bar_chart(reclamos_mes)

        if st.sidebar.checkbox("Distribución por Aseguradora", False):
            resumen = pagados.groupby('COMPAÑÍA')['VALOR RECLAMO'].sum()
            st.bar_chart(resumen)

        if st.sidebar.checkbox("Estados Pendientes", False):
            pendientes_estados = pendientes['ESTADO ACTUAL'].value_counts()
            st.bar_chart(pendientes_estados)

    with tab3:
        st.sidebar.header("🔥 Siniestralidad")
        pagados['MES'] = pd.to_datetime(pagados['FECHA SINIESTRO'], errors='coerce').dt.month
        primas = asegurados.groupby("MES")["PRIMA VEHÍCULOS"].sum()
        siniestros = pagados.groupby("MES")["VALOR RECLAMO"].sum()
        ratio = (siniestros / primas).fillna(0)

        if st.sidebar.checkbox("Siniestralidad Mensual", True):
            st.line_chart(ratio.rename("Siniestralidad"))

        if st.sidebar.checkbox("Tabla Detallada", False):
            tabla = pd.concat([primas, siniestros, ratio.rename("SINIESTRALIDAD")], axis=1)
            tabla.columns = ['Prima Vehículos', 'Valor Reclamos', 'Siniestralidad']
            st.dataframe(tabla.round(2))
