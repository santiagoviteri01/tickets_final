import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io

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
            st.header("⚙️ Configuración del Analisis de Suma Asegurada")
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
        orden_meses = meses_orden
    
        resumen_aseguradoras_total = pagados.groupby('COMPAÑÍA').agg(
            Media_Reclamo=('VALOR RECLAMO', 'mean'),
            Mediana_Reclamo=('VALOR RECLAMO', 'median'),
            Total_Reclamo=('VALOR RECLAMO', 'sum'),
            Media_Deducible=('DEDUCIBLE', 'mean')
        ).round(2)
    
        with st.sidebar:
            st.header("⚙️ Configuración del Análisis de Reclamos")
            año_analisis = st.selectbox("Seleccionar Año", [2024, 2025], key="año_reclamos")
            top_n = st.slider("Top N Marcas", 3, 10, 5, key="top_n")
            bins_hist = st.slider("Bins para Histograma", 10, 100, 30, key="bins_hist")
            if len(resumen_aseguradoras_total) >= 1:
                aseguradoras_seleccionadas = st.multiselect(
                    "Selecciona las aseguradoras para comparar",
                    options=resumen_aseguradoras_total.index.tolist(),
                    default=resumen_aseguradoras_total.index.tolist()[:2]
                )
    
        pagados_filtrados = pagados[pagados['BASE'] == año_analisis].reset_index(drop=True)
        pendientes_filtrados = pendientes[pendientes['BASE'] == año_analisis].reset_index(drop=True)
    
        pagos_aseguradora_data = pagados_filtrados[pagados_filtrados['COMPAÑÍA'].isin(aseguradoras_seleccionadas)]
        pendientes_aseguradora_data = pendientes_filtrados[pendientes_filtrados['CIA. DE SEGUROS'].isin(aseguradoras_seleccionadas)]
    
        with st.expander("📁 Datos Generales"):
            st.subheader("Reclamos Pagados")
            st.dataframe(pagos_aseguradora_data[['COMPAÑÍA', 'VALOR RECLAMO', 'FECHA SINIESTRO', 'EVENTO']].head(3), use_container_width=True)
    
            st.subheader("Reclamos Pendientes")
            st.dataframe(pendientes_aseguradora_data[['CIA. DE SEGUROS', 'VALOR SINIESTRO', 'FECHA DE SINIESTRO', 'ESTADO ACTUAL']].head(3), use_container_width=True)
    
        st.header("📅 Distribución Temporal")
        pagos_aseguradora_data['FECHA SINIESTRO'] = pd.to_datetime(pagos_aseguradora_data['FECHA SINIESTRO'], dayfirst=True, errors='coerce')
        pagos_aseguradora_data['MES'] = pagos_aseguradora_data['FECHA SINIESTRO'].dt.month
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.countplot(data=pagos_aseguradora_data, x='MES', palette='viridis', ax=ax)
        ax.set_xticks(range(0, 12))
        ax.set_xticklabels(meses_orden, rotation=45)
        ax.set_title('Reclamos por Mes')
        st.pyplot(fig)
    
        st.header("💰 Análisis de Valores")
        grafico_valores = st.radio("Elegir gráfico de análisis de valores", ["Histograma", "Boxplot", "Por Rangos"], horizontal=True)
        if grafico_valores == "Histograma":
            fig = plt.figure(figsize=(10, 4))
            sns.histplot(pagos_aseguradora_data['VALOR RECLAMO'], bins=bins_hist, kde=True)
            st.pyplot(fig)
        elif grafico_valores == "Boxplot":
            fig = plt.figure(figsize=(10, 4))
            sns.boxplot(x=pagos_aseguradora_data['VALOR RECLAMO'], color='lightgreen')
            st.pyplot(fig)
        elif grafico_valores == "Por Rangos":
            max_val = int(pagos_aseguradora_data['VALOR RECLAMO'].max())
            bin_size = st.slider("Tamaño del bin ($)", 500, max_val, 500, step=500)
            bins = list(range(0, max_val + bin_size, bin_size))
            labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
            pagos_aseguradora_data['Rango'] = pd.cut(pagos_aseguradora_data['VALOR RECLAMO'], bins=bins, labels=labels, right=False)
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.countplot(y='Rango', data=pagos_aseguradora_data, order=labels, color='salmon', ax=ax)
            st.pyplot(fig)
    
        st.header("📄 Generar Informe Anual")
        if st.button("Generar Informe"):
            resumen_mes = pd.pivot_table(
                pagados_filtrados,
                values='VALOR RECLAMO',
                index='MES',
                columns='COMPAÑÍA',
                aggfunc=['sum', 'count'],
                fill_value=0,
                margins=True
            )
            resumen_mes.columns = [f"{aggfunc} {compa}" for aggfunc, compa in resumen_mes.columns]
            talleres = pagados_filtrados.pivot_table(values='VALOR RECLAMO', index='TALLER DE REPARACION', columns='COMPAÑÍA', aggfunc='count', fill_value=0)
            causas = pagados_filtrados.pivot_table(values='VALOR RECLAMO', index='EVENTO', aggfunc=['sum', 'count'], fill_value=0)
            causas.columns = ['Total_Reclamo', 'Cantidad_Reclamos']
            pendientes_estado = pendientes_filtrados.pivot_table(values='VALOR SINIESTRO', index='ESTADO ACTUAL', columns='CIA. DE SEGUROS', aggfunc='count', fill_value=0)
    
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                resumen_mes.to_excel(writer, sheet_name='Resumen Mes')
                talleres.to_excel(writer, sheet_name='Talleres')
                causas.to_excel(writer, sheet_name='Causas')
                pendientes_estado.to_excel(writer, sheet_name='Pendientes')
            output.seek(0)
            st.download_button(
                label="Descargar Reporte",
                data=output,
                file_name=f"Reporte_Retorno_{año_analisis}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

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
