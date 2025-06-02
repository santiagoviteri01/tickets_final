import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import io


# Configuración inicial
def mostrar_dashboard_analisis(pagados, pendientes, asegurados):
    st.title("📊 Análisis de la Cuenta")

    if any(df is None or df.empty for df in [pagados, pendientes, asegurados]):
        st.warning("Por favor verifica que los DataFrames no estén vacíos.")
        return
    meses_orden = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                       'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    mes_actual = datetime.now().month
    seccion = st.radio(
        "Selecciona una sección:",
        ["🔍 Suma Asegurada", "📁 Reclamos", "🔥 Siniestralidad","📊 Comisiones por Canal"],
        horizontal=True
    )
    

    if seccion == "🔍 Suma Asegurada":
        asegurados['FECHA'] = pd.to_datetime(asegurados['FECHA'], dayfirst=True, errors='coerce')
        asegurados['MES'] = asegurados['FECHA'].dt.month
        asegurados['MES_NOMBRE'] = asegurados['FECHA'].dt.month_name()
        asegurados['AÑO'] = asegurados['FECHA'].dt.year

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
        
            # Crear tabla pivote
            df_temporal = df_filtrado.pivot_table(
                values='VALOR ASEGURADO', index='MES', columns='AÑO', aggfunc='sum'
            ).reindex(range(1, 13))
        
            # Reemplazar índice numérico por nombre del mes
            df_temporal.index = pd.Categorical(
                [meses_orden[m-1] for m in df_temporal.index], categories=meses_orden, ordered=True
            )
        
            # Reemplazar ceros por NaN si en una columna (año) todos los valores desde cierto punto son ceros
            for col in df_temporal.columns:
                # Encuentra el último mes con un valor distinto de cero
                non_zero_mask = df_temporal[col] != 0
                if non_zero_mask.any():
                    last_valid_index = non_zero_mask[non_zero_mask].index[-1]
                    last_valid_pos = df_temporal.index.get_loc(last_valid_index)
                    # Desde el siguiente al último valor válido en adelante, pon NaN si es cero
                    for i in range(last_valid_pos + 1, len(df_temporal)):
                        if df_temporal.iloc[i][col] == 0:
                            df_temporal.iloc[i, df_temporal.columns.get_loc(col)] = np.nan
        
            # Graficar con matplotlib
            fig, ax = plt.subplots(figsize=(10, 5))
            df_temporal.plot(ax=ax, marker='o')
            ax.set_title("Evolución Anual de la Suma Asegurada")
            ax.set_xlabel("Mes")
            ax.set_ylabel("Suma Asegurada")
            ax.grid(True)
            plt.xticks(rotation=45)
        
            st.pyplot(fig)
        
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
                Suma_Asegurada=('VALOR ASEGURADO', 'sum')
            ).fillna(0)
        
            # Plot con matplotlib
            fig, ax = plt.subplots(figsize=(10, 4))
            evolucion.plot(ax=ax, marker='o', legend=False)
            ax.set_title("Evolución de la Suma Asegurada")
            ax.set_xlabel("Periodo")
            ax.set_ylabel("Suma Asegurada")
            ax.grid(True)
            plt.xticks(rotation=45)
        
            st.pyplot(fig)
        
        if "Tasa Mensual" in mostrar_graficos:
            st.subheader("📉 Tasa Mensual")
        
            # Agrupar y calcular la tasa
            tasa_mensual = df_filtrado.groupby(['AÑO', 'MES']).agg(
                Prima_Total=('PRIMA TOTAL VEHÍCULOS', 'sum'),
                Suma_Asegurada_Total=('VALOR ASEGURADO', 'sum')
            ).reset_index()
        
            # Calcular tasa como porcentaje
            tasa_mensual['Tasa'] = (tasa_mensual['Prima_Total'] / tasa_mensual['Suma_Asegurada_Total']) * 100
        
            # Crear columna de periodo legible
            tasa_mensual['Periodo'] = tasa_mensual['MES'].apply(lambda x: meses_orden[x-1]) + '-' + tasa_mensual['AÑO'].astype(str)
        
            # Ordenar por año y mes
            tasa_mensual = tasa_mensual.sort_values(['AÑO', 'MES'])
            tasa_mensual['Periodo'] = pd.Categorical(
                tasa_mensual['Periodo'], categories=tasa_mensual['Periodo'].unique(), ordered=True
            )
        
            # Graficar con matplotlib
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(tasa_mensual['Periodo'], tasa_mensual['Tasa'], marker='o')
            ax.set_title("Tasa Mensual de Prima vs. Suma Asegurada")
            ax.set_xlabel("Periodo")
            ax.set_ylabel("Tasa (%)")
            ax.grid(True)
            plt.xticks(rotation=45)
        
            st.pyplot(fig)
    
        if "Top Marcas" in mostrar_graficos:
            st.subheader("🏅 Top Marcas")
        
            # Obtener top 10 marcas
            top_marcas = df_filtrado['MARCA'].value_counts().nlargest(10)
        
            # Graficar con matplotlib
            fig, ax = plt.subplots(figsize=(8, 4))
            top_marcas.plot(kind='barh', ax=ax)
            ax.set_title("Top 10 Marcas Más Aseguradas")
            ax.set_xlabel("Marca")
            ax.set_ylabel("Cantidad")
            ax.grid(axis='y')
            plt.xticks(rotation=45)
        
            st.pyplot(fig)

    
    elif seccion == "📁 Reclamos":
    
        # Asegurar formato de fecha
        pagados['FECHA SINIESTRO'] = pd.to_datetime(pagados['FECHA SINIESTRO'], errors='coerce')
        pendientes['FECHA DE SINIESTRO'] = pd.to_datetime(pendientes['FECHA DE SINIESTRO'], errors='coerce')
    
        # Forzar que BASE sea el año de la fecha siniestro
        pagados['BASE'] = pagados['FECHA SINIESTRO'].dt.year.astype('Int64')
        pendientes['BASE'] = pendientes['FECHA DE SINIESTRO'].dt.year.astype('Int64')
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
    
        st.header("📁 Datos Generales")
        st.dataframe(pagos_aseguradora_data[['COMPAÑÍA', 'VALOR RECLAMO', 'FECHA SINIESTRO', 'EVENTO']].head(3))
        st.dataframe(pendientes_aseguradora_data[['CIA. DE SEGUROS', 'VALOR SINIESTRO', 'FECHA DE SINIESTRO', 'ESTADO ACTUAL']].head(3))
    
        st.header("🗕️ Distribución Temporal")
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
            bins_hist = st.slider("📊 Número de Bins", 10, 100, 30, 5)
            fig = plt.figure(figsize=(10, 4))
            sns.histplot(pagos_aseguradora_data['VALOR RECLAMO'], bins=bins_hist, kde=True)
            st.pyplot(fig)
        elif grafico_valores == "Boxplot":
            fig = plt.figure(figsize=(10, 4))
            sns.boxplot(x=pagos_aseguradora_data['VALOR RECLAMO'], color='lightgreen')
            st.pyplot(fig)
        elif grafico_valores == "Por Rangos":
            max_val = int(pagos_aseguradora_data['VALOR RECLAMO'].max())
            bin_size = st.slider("Tamaño del bin ($)", 2000, max_val, 500, 500)
            bins = list(range(0, max_val + bin_size, bin_size))
            labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]
            pagos_aseguradora_data['Rango'] = pd.cut(pagos_aseguradora_data['VALOR RECLAMO'], bins=bins, labels=labels, right=False)
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.countplot(y='Rango', data=pagos_aseguradora_data, order=labels, color='salmon', ax=ax)
            st.pyplot(fig)
    
        # Nuevo selector de tipo de severidad
        st.header("Análisis de Variables")
        tipo_severidad = st.radio("Tipo de severidad", ["Promedio", "Total"], horizontal=True)
    
        def plot_severidad(tipo, campo, titulo):
            agrupado = pagos_aseguradora_data.groupby(campo)['VALOR RECLAMO']
            datos = agrupado.mean() if tipo == "Promedio" else agrupado.sum()
            datos = datos.sort_values(ascending=False).head(10)
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=datos.values, y=datos.index, ax=ax, palette='viridis')
            ax.set_title(titulo)
            ax.set_xlabel(f"{'Promedio' if tipo == 'Promedio' else 'Total'} ($)")
            st.pyplot(fig)
    
        cols = ["EVENTO", "TALLER DE REPARACION", "CIUDAD OCURRENCIA", "MARCA"]
        titulos = [
            "Severidad por Evento",
            "Severidad por Taller de Reparación",
            "Severidad por Ciudad",
            "Severidad por Marca"
        ]
    
        for col, titulo in zip(cols, titulos):
            plot_severidad(tipo_severidad, col, titulo)
    
        st.header("📄 Generar Informe Anual")
        if st.button("Generar Informe"):
            resumen_mes = pagados_filtrados.pivot_table(values='VALOR RECLAMO', index='MES', columns='COMPAÑÍA', aggfunc=['sum', 'count'], fill_value=0, margins=True)
            resumen_mes.columns = [f"{aggfunc} {col}" for aggfunc, col in resumen_mes.columns]
            talleres = pagados_filtrados.pivot_table(values='VALOR RECLAMO', index='TALLER DE REPARACION', columns='COMPAÑÍA', aggfunc='count', fill_value=0)
            causas = pagados_filtrados.pivot_table(values='VALOR RECLAMO', index='EVENTO', aggfunc=['sum', 'count'], fill_value=0)
            causas.columns = ['Total_Reclamo', 'Cantidad_Reclamos']
            pendientes_estado = pendientes_filtrados.pivot_table(values='VALOR SINIESTRO', index='ESTADO ACTUAL', columns='CIA. DE SEGUROS', aggfunc='count', fill_value=0)
    
            # Severidad resumen
            def resumen_severidad(df, campo):
                return pd.DataFrame({
                    'Severidad Promedio': df.groupby(campo)['VALOR RECLAMO'].mean().round(2),
                    'Severidad Total': df.groupby(campo)['VALOR RECLAMO'].sum().round(2)
                }).sort_values('Severidad Total', ascending=False)
    
            sev_evento = resumen_severidad(pagos_aseguradora_data, 'EVENTO')
            sev_taller = resumen_severidad(pagos_aseguradora_data, 'TALLER DE REPARACION')
            sev_ciudad = resumen_severidad(pagos_aseguradora_data, 'CIUDAD OCURRENCIA')
            sev_marca = resumen_severidad(pagos_aseguradora_data, 'MARCA')
    
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                resumen_mes.to_excel(writer, sheet_name='Resumen Mes')
                talleres.to_excel(writer, sheet_name='Talleres')
                causas.to_excel(writer, sheet_name='Causas')
                pendientes_estado.to_excel(writer, sheet_name='Pendientes')
                sev_evento.to_excel(writer, sheet_name='Severidad Eventos')
                sev_taller.to_excel(writer, sheet_name='Severidad Talleres')
                sev_ciudad.to_excel(writer, sheet_name='Severidad Ciudades')
                sev_marca.to_excel(writer, sheet_name='Severidad Marcas')
            output.seek(0)
    
            st.download_button(
                label="📂 Descargar Reporte",
                data=output,
                file_name=f"Reporte_Reclamos_{año_analisis}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    elif seccion == "🔥 Siniestralidad":
        st.header("📉 Siniestralidad Mensual por Aseguradora")
    
        # Estándar de nombres desde pendientes
        mapeo_columnas = {
            'CIA. DE SEGUROS': 'COMPAÑÍA',
            'VALOR SINIESTRO': 'VALOR RECLAMO',
            'FECHA DE SINIESTRO': 'FECHA SINIESTRO'
        }
        pendientes_estandarizado = pendientes.rename(columns=mapeo_columnas)
    
        # Asegurar tipos correctos
        pagados['FECHA SINIESTRO'] = pd.to_datetime(pagados['FECHA SINIESTRO'], errors='coerce')
        pagados['VALOR RECLAMO'] = pd.to_numeric(pagados['VALOR RECLAMO'], errors='coerce')
    
        pendientes_estandarizado['FECHA SINIESTRO'] = pd.to_datetime(pendientes_estandarizado['FECHA SINIESTRO'], errors='coerce')
        pendientes_estandarizado['VALOR RECLAMO'] = pd.to_numeric(pendientes_estandarizado['VALOR RECLAMO'], errors='coerce')
    
        # Unir reclamos pagados + pendientes
        df_completo = pd.concat([
            pagados[['COMPAÑÍA', 'FECHA SINIESTRO', 'VALOR RECLAMO']],
            pendientes_estandarizado[['COMPAÑÍA', 'FECHA SINIESTRO', 'VALOR RECLAMO']]
        ], ignore_index=True).dropna(subset=['FECHA SINIESTRO'])
    
        # Generar columnas de año y mes
        df_completo['FECHA_SINIESTRO'] = pd.to_datetime(df_completo['FECHA SINIESTRO'], errors='coerce')
        df_completo['AÑO'] = df_completo['FECHA_SINIESTRO'].dt.year.astype('Int64')
        df_completo['MES'] = df_completo['FECHA_SINIESTRO'].dt.month.astype('Int64')
    
        # Valor asegurado por mes
        valor_asegurado = asegurados.groupby(['ASEGURADORA', 'AÑO', 'MES']).agg(
            Prima_Vehiculos=('PRIMA VEHÍCULOS', 'sum')
        ).reset_index()
    
        # Reclamos agregados
        reclamos_agrupados = df_completo.groupby(['COMPAÑÍA', 'AÑO', 'MES']).agg(
            Total_Reclamos=('VALOR RECLAMO', 'count'),
            Monto_Total_Reclamos=('VALOR RECLAMO', 'sum')
        ).reset_index().rename(columns={'COMPAÑÍA': 'ASEGURADORA'})
    
        # Unión con asegurados
        df_siniestralidad = pd.merge(
            valor_asegurado,
            reclamos_agrupados,
            on=['ASEGURADORA', 'AÑO', 'MES'],
            how='left'
        ).fillna(0)
    
        df_siniestralidad['Siniestralidad'] = np.where(
            df_siniestralidad['Prima_Vehiculos'] > 0,
            df_siniestralidad['Monto_Total_Reclamos'] / df_siniestralidad['Prima_Vehiculos'],
            0
        )
    
        df_siniestralidad['PERIODO'] = df_siniestralidad['AÑO'].astype(str) + '-' + df_siniestralidad['MES'].astype(str).str.zfill(2)
        df_siniestralidad['FECHA'] = pd.to_datetime(df_siniestralidad['PERIODO'] + '-01', errors='coerce')
    
        # Filtros
        col1, col2 = st.columns(2)
        with col1:
            años_disponibles = sorted(df_siniestralidad['AÑO'].dropna().unique(), reverse=True)
            año_sel = st.selectbox("Año de análisis", options=['Todos'] + list(años_disponibles), key='sini_año')
        with col2:
            aseguradora_sel = st.selectbox("Aseguradora", options=['Todas'] + sorted(df_siniestralidad['ASEGURADORA'].unique()), key='sini_aseguradora')
    
        # Filtro por año
        if año_sel != 'Todos':
            df_filtrado = df_siniestralidad[df_siniestralidad['AÑO'] == int(año_sel)]
        else:
            df_filtrado = df_siniestralidad.copy()
    
        # Filtro por aseguradora
        if aseguradora_sel != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['ASEGURADORA'] == aseguradora_sel]
        else:
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
            df_filtrado['FECHA'] = pd.to_datetime(df_filtrado['PERIODO'] + '-01', errors='coerce')
    
        # Gráfico
        df_filtrado = df_filtrado.sort_values('FECHA')
        fig, ax = plt.subplots(figsize=(14, 6))
        sns.lineplot(data=df_filtrado, x='PERIODO', y='Siniestralidad', marker='o', color='#E53935', ax=ax)
        ax.set_ylabel("Ratio Siniestralidad", color='#E53935')
        ax.tick_params(axis='y', colors='#E53935')
    
        num_periodos = len(df_filtrado['PERIODO'].unique())
        rotation = 45 if num_periodos > 6 else 0
        step = max(1, num_periodos // 12)
        ax.set_xticks(df_filtrado['PERIODO'].unique()[::step])
        ax.set_xticklabels(df_filtrado['PERIODO'].unique()[::step], rotation=rotation)
    
        if aseguradora_sel != 'Todas':
            ax2 = ax.twinx()
            sns.barplot(data=df_filtrado, x='PERIODO', y='Monto_Total_Reclamos', color='#1E88E5', alpha=0.3, ax=ax2)
            ax2.set_ylabel("Monto Total Reclamos ($)", color='#1E88E5')
            ax2.tick_params(axis='y', colors='#1E88E5')
    
        titulo = f"Siniestralidad {'por Aseguradora' if aseguradora_sel != 'Todas' else 'Acumulada'}"
        titulo += f" ({'Histórico Completo' if año_sel == 'Todos' else año_sel})"
        plt.title(titulo)
        st.pyplot(fig)
    
        st.subheader("📊 Datos Detallados")
        columnas = ['PERIODO', 'ASEGURADORA', 'Prima_Vehiculos', 'Total_Reclamos', 'Monto_Total_Reclamos', 'Siniestralidad'] if aseguradora_sel != 'Todas' else ['PERIODO', 'Prima_Vehiculos', 'Total_Reclamos', 'Monto_Total_Reclamos', 'Siniestralidad']
        st.dataframe(
            df_filtrado[columnas]
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
    
    elif seccion == "📊 Comisiones por Canal":
        st.header("📊 Análisis de Comisiones por Canal")
    
        # Asegurar formato de fecha y crear columnas de año y mes
        asegurados['FECHA'] = pd.to_datetime(asegurados['FECHA'], dayfirst=True, errors='coerce')
        asegurados['MES'] = asegurados['FECHA'].dt.month
        asegurados['AÑO'] = asegurados['FECHA'].dt.year

        # Sidebar de filtros
        with st.sidebar:
            st.header("⚙️ Filtros de Comisiones")
            aseguradoras = ['Todas'] + sorted(asegurados['ASEGURADORA'].dropna().unique())
            aseguradora_sel = st.selectbox("Seleccionar Aseguradora", aseguradoras, key="aseg_comisiones")

            años_disponibles = sorted(asegurados['AÑO'].dropna().unique())
            años_sel = st.multiselect("Seleccionar Años", años_disponibles, default=años_disponibles, key="años_comisiones")

        # Filtrar aseguradora y años
        df_com = asegurados.copy()
        if aseguradora_sel != 'Todas':
            df_com = df_com[df_com['ASEGURADORA'] == aseguradora_sel]

        if años_sel:
            df_com = df_com[df_com['AÑO'].isin(años_sel)]
        else:
            st.warning("Selecciona al menos un año")
            st.stop()

        # Columnas de comisiones
        columnas_comision = [
            "COMISIÓN PRIMA VEHÍCULOS",
            "COMISIÓN CONCESIONARIO VEHÍCULOS",
            "COMISIÓN BROKER LIDERSEG VEHÍCULOS",
            "COMISIÓN BROKER INSURATLAN VEHÍCULOS"
        ]

        # Agrupar por año y mes
        df_comisiones = df_com.groupby(['AÑO', 'MES'])[columnas_comision].sum().reset_index()

        # Crear columna "Periodo"
        df_comisiones['Periodo'] = df_comisiones['MES'].apply(lambda x: meses_orden[x - 1]) + '-' + df_comisiones['AÑO'].astype(str)
        df_comisiones = df_comisiones.sort_values(['AÑO', 'MES'])
        df_comisiones['Periodo'] = pd.Categorical(df_comisiones['Periodo'], categories=df_comisiones['Periodo'].unique(), ordered=True)
        df_comisiones.set_index('Periodo', inplace=True)

        # Total comisiones
        st.subheader("🔢 Total Comisiones Pagadas")
        total_comisiones = df_comisiones[columnas_comision].sum().sum()
        st.metric("Total USD", f"${total_comisiones:,.2f}")

        # Gráfico apilado por canal
        st.subheader("📈 Evolución de Comisiones por Canal")
        fig, ax = plt.subplots(figsize=(12, 5))
        df_comisiones[columnas_comision].plot(kind='bar', stacked=True, ax=ax)
        ax.set_ylabel("USD ($)")
        ax.set_title("Pago de Comisiones por Canal y Mes")
        ax.legend(title="Canal", bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(fig)

        # Gráficos individuales por canal
        st.subheader("📊 Comisiones por Canal - Individual")
        for col in columnas_comision:
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_comisiones.index, df_comisiones[col], marker='o', label=col)
            ax.set_title(col)
            ax.set_xlabel("Periodo")
            ax.set_ylabel("USD ($)")
            ax.grid(True)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Tabla detallada
        st.subheader("📄 Tabla Detallada")
        st.dataframe(df_comisiones[columnas_comision].round(2), use_container_width=True)

        # Exportar a Excel
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df_comisiones.reset_index()[['Periodo'] + columnas_comision].to_excel(writer, sheet_name='Comisiones Mensuales', index=False)
        output.seek(0)
        st.download_button(
            label="📥 Descargar Comisiones en Excel",
            data=output,
            file_name="comisiones_por_canal.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

