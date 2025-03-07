import os
import pandas as pd
import streamlit as st
import plotly.express as px

# 📁 Carpeta base donde están los reportes
BASE_DIR = r"C:\Users\umoya\Dropbox\Espacio familiar\Commodities\outputs"

# 📌 Obtener la lista de commodities desde la carpeta outputs
def listar_commodities(base_dir):
    """Lista todas las carpetas dentro del directorio de outputs."""
    try:
        return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    except FileNotFoundError:
        st.error("❌ Error: No se encontró la carpeta de commodities.")
        return []

# 📌 Obtener la lista de reportes disponibles para un commodity
def listar_reportes(commodity):
    """Lista los archivos .xlsx dentro de la carpeta del commodity seleccionado."""
    path = os.path.join(BASE_DIR, commodity)
    try:
        return [f for f in os.listdir(path) if f.endswith(".xlsx")]
    except FileNotFoundError:
        st.error(f"❌ Error: No se encontraron reportes para {commodity}.")
        return []

# 📌 Cargar el archivo Excel seleccionado
@st.cache_data
def cargar_reporte(commodity, reporte):
    """Carga el archivo Excel en un DataFrame de Pandas."""
    file_path = os.path.join(BASE_DIR, commodity, reporte)
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        st.error(f"❌ Error al cargar el archivo: {e}")
        return pd.DataFrame()

# 📌 Configuración del Dashboard
st.set_page_config(page_title="Dashboard de Commodities", layout="wide")

# 🎨 Título del Dashboard
st.title("📊 Dashboard Interactivo de Commodities (versión prueba)")

# 📍 Selección del commodity
commodities = listar_commodities(BASE_DIR)
commodity_seleccionado = st.selectbox("Selecciona un commodity:", commodities)

# 📍 Selección del reporte
if commodity_seleccionado:
    reportes = listar_reportes(commodity_seleccionado)
    reporte_seleccionado = st.selectbox("Selecciona un reporte:", reportes)

    if reporte_seleccionado:
        df = cargar_reporte(commodity_seleccionado, reporte_seleccionado)

        # Verifica si el DataFrame tiene contenido
        if not df.empty:
            st.subheader("📋 Datos del Reporte")
            st.dataframe(df)  # Muestra la tabla interactiva

            # 🎯 Pestañas para REG y REC
            tab1, tab2 = st.tabs(["REG", "REC"])

            with tab1:
                st.header("📊 Análisis de REG")
                if "N_Casos_Hits_MU" in df.columns and "N_Casos_NoHits_MU" in df.columns:
                    fig1 = px.bar(
                        df,
                        x=df.index,
                        y=["N_Casos_Hits_MU", "N_Casos_NoHits_MU"],
                        labels={"value": "Cantidad de Casos", "variable": "Tipo"},
                        title="Comparación de Hits y No Hits (REG)",
                        barmode="group"
                    )
                    st.plotly_chart(fig1)

                if "Rent_Real_Promedio_Hits_a_la_Sem1 (%)" in df.columns and "Rent_Real_Promedio_NoHits_a_la_Sem1 (%)" in df.columns:
                    fig2 = px.line(
                        df,
                        x=df.index,
                        y=["Rent_Real_Promedio_Hits_a_la_Sem1 (%)", "Rent_Real_Promedio_NoHits_a_la_Sem1 (%)"],
                        labels={"value": "Rentabilidad (%)", "variable": "Tipo"},
                        title="Rentabilidad Promedio a la Semana 1 (REG)"
                    )
                    st.plotly_chart(fig2)

            with tab2:
                st.header("📊 Análisis de REC")
                if "N_Casos_Hits_MU" in df.columns and "N_Casos_NoHits_MU" in df.columns:
                    fig3 = px.bar(
                        df,
                        x=df.index,
                        y=["N_Casos_Hits_MU", "N_Casos_NoHits_MU"],
                        labels={"value": "Cantidad de Casos", "variable": "Tipo"},
                        title="Comparación de Hits y No Hits (REC)",
                        barmode="group"
                    )
                    st.plotly_chart(fig3)

                if "Rent_Real_Promedio_Hits_a_la_Sem1 (%)" in df.columns and "Rent_Real_Promedio_NoHits_a_la_Sem1 (%)" in df.columns:
                    fig4 = px.line(
                        df,
                        x=df.index,
                        y=["Rent_Real_Promedio_Hits_a_la_Sem1 (%)", "Rent_Real_Promedio_NoHits_a_la_Sem1 (%)"],
                        labels={"value": "Rentabilidad (%)", "variable": "Tipo"},
                        title="Rentabilidad Promedio a la Semana 1 (REC)"
                    )
                    st.plotly_chart(fig4)

        else:
            st.warning("⚠️ El archivo está vacío o tiene errores en la lectura.")
