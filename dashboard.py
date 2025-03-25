import streamlit as st
import pandas as pd
import io
import dropbox  # Cliente oficial de Dropbox
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

# ==============================================================================
# CONFIGURACIÓN DE ACCESO A DROPBOX
# ==============================================================================
# Leemos el token desde el archivo secrets.toml (seguro)
DROPBOX_TOKEN = st.secrets["dropbox"]["access_token"]
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Ruta en Dropbox donde están los reportes
DROPBOX_BASE_PATH = "/Apps/productos_panel_app/salidas"

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def list_dropbox_folders(path):
    """Lista las carpetas dentro de la ruta 'salidas'."""
    try:
        folders = dbx.files_list_folder(path).entries
        return sorted([f.name for f in folders if isinstance(f, dropbox.files.FolderMetadata)])
    except Exception as e:
        st.error(f"No se pudieron listar carpetas en Dropbox: {e}")
        return []

def list_excel_files_in_folder(folder_name):
    """Lista los archivos .xlsx dentro de una subcarpeta (producto)."""
    folder_path = f"{DROPBOX_BASE_PATH}/{folder_name}"
    try:
        entries = dbx.files_list_folder(folder_path).entries
        return sorted([f.name for f in entries if f.name.endswith(".xlsx")])
    except Exception as e:
        st.error(f"No se pudieron listar archivos: {e}")
        return []

def leer_excel_desde_dropbox(file_path, sheet_name):
    """Lee un archivo Excel directamente desde Dropbox."""
    try:
        metadata, res = dbx.files_download(file_path)
        file_content = io.BytesIO(res.content)
        df = pd.read_excel(file_content, sheet_name=sheet_name, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"No se pudo leer el archivo desde Dropbox: {e}")
        return pd.DataFrame()

def generar_excel_para_descargar(df, nombre_hoja):
    """Genera bytes para descargar el DataFrame como archivo Excel."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=nombre_hoja)
    output.seek(0)
    return output.read()

# ==============================================================================
# INTERFAZ STREAMLIT
# ==============================================================================

st.title("PANEL de Reportes de Productos")
st.write("Seleccione un producto y un reporte para visualizar los datos directamente desde Dropbox.")

productos = list_dropbox_folders(DROPBOX_BASE_PATH)

if productos:
    producto_sel = st.sidebar.selectbox("Seleccione el producto", productos)
    archivos = list_excel_files_in_folder(producto_sel)
    
    if archivos:
        archivo_sel = st.sidebar.selectbox("Seleccione el archivo Excel", archivos)
        hoja_sel = st.sidebar.radio("Seleccione la hoja", ["Reporte REG", "Reporte REC"])

        if st.sidebar.button("Cargar Reporte"):
            ruta_archivo = f"{DROPBOX_BASE_PATH}/{producto_sel}/{archivo_sel}"
            df = leer_excel_desde_dropbox(ruta_archivo, hoja_sel)

            if not df.empty:
                st.success("Reporte cargado exitosamente.")
                st.dataframe(df)

                excel_bytes = generar_excel_para_descargar(df, hoja_sel)

                st.download_button(
                    label="Descargar Reporte",
                    data=excel_bytes,
                    file_name=f"{producto_sel}_{archivo_sel}_{hoja_sel}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    else:
        st.warning("No hay archivos Excel en esta carpeta.")
else:
    st.warning("No se encontraron productos.")
