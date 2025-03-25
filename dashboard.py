import streamlit as st
import pandas as pd
import io
import dropbox  # Cliente oficial de Dropbox
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

# ==============================================================================
# CONFIGURACIÓN DE ACCESO A DROPBOX
# ==============================================================================

# Cargamos el token desde el archivo secrets.toml
DROPBOX_TOKEN = st.secrets["dropbox"]["access_token"]
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# Ruta en Dropbox donde están las carpetas de reportes por producto
DROPBOX_BASE_PATH = "/Apps/productos_panel_app/salidas"

# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def list_dropbox_folders(path):
    """Devuelve una lista de nombres de carpetas dentro de la ruta dada en Dropbox."""
    try:
        folders = dbx.files_list_folder(path).entries
        return sorted([f.name for f in folders if isinstance(f, dropbox.files.FolderMetadata)])
    except Exception as e:
        st.error(f"No se pudieron listar carpetas en Dropbox: {e}")
        return []

def list_excel_files_in_folder(folder_name):
    """Devuelve una lista de archivos .xlsx dentro de una subcarpeta de producto."""
    folder_path = f"{DROPBOX_BASE_PATH}/{folder_name}"
    try:
        entries = dbx.files_list_folder(folder_path).entries
        return sorted([f.name for f in entries if f.name.endswith(".xlsx")])
    except Exception as e:
        st.error(f"No se pudieron listar archivos: {e}")
        return []

def leer_excel_desde_dropbox(file_path, sheet_name):
    """Lee un archivo Excel directamente desde Dropbox y lo retorna como DataFrame."""
    try:
        metadata, res = dbx.files_download(file_path)
        file_content = io.BytesIO(res.content)
        df = pd.read_excel(file_content, sheet_name=sheet_name, engine="openpyxl")
        return df
    except Exception as e:
        st.error(f"No se pudo leer el archivo desde Dropbox: {e}")
        return pd.DataFrame()

def generar_excel_para_descargar(df, nombre_hoja):
    """Convierte un DataFrame en un archivo Excel en memoria para descarga."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=nombre_hoja)
    output.seek(0)
    return output.read()

# ==============================================================================
# INTERFAZ DE USUARIO STREAMLIT
# ==============================================================================

st.set_page_config(page_title="Panel de Productos", layout="centered")
st.title("PANEL de Reportes de Productos")
st.write("Seleccione un producto y un reporte para visualizar los datos directamente desde Dropbox.")

# ----------------------------------------------------
# Sección 1: Selección de producto (carpeta)
# ----------------------------------------------------
productos = list_dropbox_folders(DROPBOX_BASE_PATH)

if productos:
    producto_sel = st.sidebar.selectbox("Seleccione el producto", productos)
    
    # ------------------------------------------------
    # Sección 2: Selección de archivo dentro del producto
    # ------------------------------------------------
    archivos = list_excel_files_in_folder(producto_sel)
    
    if archivos:
        archivo_sel = st.sidebar.selectbox("Seleccione el archivo Excel", archivos)
        hoja_sel = st.sidebar.radio("Seleccione la hoja", ["Reporte REG", "Reporte REC"])

        # ------------------------------------------------
        # Sección 3: Cargar y mostrar el reporte
        # ------------------------------------------------
        if st.sidebar.button("Cargar Reporte"):
            ruta_archivo = f"{DROPBOX_BASE_PATH}/{producto_sel}/{archivo_sel}"
            df = leer_excel_desde_dropbox(ruta_archivo, hoja_sel)

            if not df.empty:
                st.success("Reporte cargado exitosamente.")
                st.dataframe(df, use_container_width=True)

                # Descarga
                excel_bytes = generar_excel_para_descargar(df, hoja_sel)
                st.download_button(
                    label="📥 Descargar Reporte",
                    data=excel_bytes,
                    file_name=f"{producto_sel}_{archivo_sel}_{hoja_sel}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.warning("El archivo está vacío o no se pudo cargar.")
    else:
        st.warning("No hay archivos Excel en esta carpeta.")
else:
    st.warning("No se encontraron productos.")
