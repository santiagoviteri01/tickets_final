import streamlit as st
import pandas as pd


# Configuración inicial
def mostrar_dashboard_analisis(pagados, pendientes, asegurados):
    st.title("📊 Dashboard Optimizado de Análisis de Seguros")

    if any(df is None or df.empty for df in [pagados, pendientes, asegurados]):
        st.warning("Por favor verifica que los DataFrames no estén vacíos.")
        return

    tab1, tab2, tab3 = st.tabs(["🔍 Suma Asegurada", "📁 Reclamos", "🔥 Siniestralidad"])

    with tab1:
        st.sidebar.header("📌 Suma Asegurada")
        if st.sidebar.checkbox("Mostrar KPIs", True):
            col1, col2, col3 = st.columns(3)
            col1.metric("Suma Asegurada", f"${asegurados['VALOR ASEGURADO'].sum():,.0f}")
            col2.metric("Prima Total", f"${asegurados['PRIMA TOTAL VEHÍCULOS'].sum():,.0f}")
            col3.metric("N° de Pólizas", f"{asegurados['NÚMERO CERTIFICADO'].nunique()}")

        if st.sidebar.checkbox("Evolución Mensual", True):
            asegurados['MES'] = pd.to_datetime(asegurados['FECHA'], errors='coerce').dt.month
            resumen_mensual = asegurados.groupby("MES")[["VALOR ASEGURADO", "PRIMA TOTAL VEHÍCULOS"]].sum()
            st.line_chart(resumen_mensual)

        if st.sidebar.checkbox("Top Marcas", False):
            top_marcas = asegurados['MARCA'].value_counts().nlargest(10)
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
