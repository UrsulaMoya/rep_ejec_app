import streamlit as st
import os
import pandas as pd
import io
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

# ==============================================================================
# CONFIGURACIÓN DE RUTAS
# ==============================================================================
# Define la ruta base a la carpeta "salidas" donde se encuentran los reportes en Excel.
BASE_DIR_EXIT = r"C:\Users\umoya\Dropbox\PRIAX UM\Prueba_DespliegueFantasia\Productos\salidas"

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def get_products():
    """
    Retorna una lista ordenada de productos disponibles en la carpeta 'salidas'.
    Cada producto es representado por una subcarpeta (por ejemplo: "chicle" o "pastilla").
    """
    if not os.path.exists(BASE_DIR_EXIT):
        return []
    # Se listan solo los directorios (productos) y se ordenan alfabéticamente.
    products = [d for d in os.listdir(BASE_DIR_EXIT) if os.path.isdir(os.path.join(BASE_DIR_EXIT, d))]
    return sorted(products)

def get_report_files(product):
    """
    Dado un producto, retorna una lista de archivos Excel (.xlsx) disponibles en la
    subcarpeta correspondiente (se asume que el nombre de la carpeta es el producto en minúsculas).
    """
    product_path = os.path.join(BASE_DIR_EXIT, product.lower())
    if not os.path.exists(product_path):
        return []
    # Se filtran los archivos que terminen en .xlsx
    files = [f for f in os.listdir(product_path) if f.endswith('.xlsx')]
    return sorted(files)

@st.cache_data(show_spinner=False)
def load_excel(file_path, sheet_name):
    """
    Carga el contenido de un archivo Excel de la hoja indicada usando pandas.
    Se utiliza st.cache_data para evitar recargar el mismo archivo repetidamente y así optimizar tiempo y memoria.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')

@st.cache_data(show_spinner=False)
def generate_excel_bytes(df, sheet_name):
    """
    A partir de un DataFrame y el nombre de la hoja, genera un archivo Excel en memoria.
    Devuelve los bytes del archivo, los cuales se usarán para la descarga.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output.read()

# ==============================================================================
# INTERFAZ DE USUARIO CON STREAMLIT
# ==============================================================================

st.title("PANEL de Reportes de Productos")
st.write("Utilice los controles de la barra lateral para seleccionar el producto, el reporte y la hoja que desea visualizar.")

# ------------------------------------------------------------------------------
# SECCIÓN: Selección de Producto
# ------------------------------------------------------------------------------
# Llama a la función get_products() para obtener la lista de productos (subcarpetas en 'salidas')
products = get_products()
if products:
    selected_product = st.sidebar.selectbox("Seleccione el producto", products)
else:
    st.sidebar.error("No se encontraron productos en la carpeta 'salidas'.")
    selected_product = None

if selected_product:
    # ------------------------------------------------------------------------------
    # SECCIÓN: Selección del Archivo de Reporte
    # ------------------------------------------------------------------------------
    report_files = get_report_files(selected_product)
    if report_files:
        selected_report_file = st.sidebar.selectbox("Seleccione el reporte", report_files)
    else:
        st.sidebar.error("No se encontraron reportes para el producto seleccionado.")
        selected_report_file = None

    # ------------------------------------------------------------------------------
    # SECCIÓN: Selección de la Hoja (Pestaña) del Reporte
    # ------------------------------------------------------------------------------
    sheet_options = ["Reporte REG", "Reporte REC"]
    selected_sheet = st.sidebar.radio("Seleccione la pestaña del reporte", sheet_options)

    # ------------------------------------------------------------------------------
    # SECCIÓN: Botón para Cargar y Mostrar el Reporte Completo
    # ------------------------------------------------------------------------------
    if st.sidebar.button("Cargar Reporte"):
        if selected_report_file:
            # Construir la ruta completa al archivo Excel
            file_path = os.path.join(BASE_DIR_EXIT, selected_product.lower(), selected_report_file)
            try:
                # Se carga el reporte completo con la función cacheada para optimizar recursos.
                df_report = load_excel(file_path, selected_sheet)
                st.success(f"Reporte cargado: {selected_report_file} - {selected_sheet}")
                
                # Mostrar el reporte completo en la aplicación.
                st.dataframe(df_report)
                
                # Generar los bytes del Excel para la descarga.
                excel_bytes = generate_excel_bytes(df_report, selected_sheet)
                st.download_button(
                    label="Descargar Reporte",
                    data=excel_bytes,
                    file_name=f"{selected_product}_{selected_report_file}_{selected_sheet}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Error al cargar el reporte: {e}")
        else:
            st.error("No se ha seleccionado un reporte.")

# ==============================================================================
# FIN DEL PANEL
# ==============================================================================
