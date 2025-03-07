import streamlit as st
import pandas as pd
import numpy as np
import os
import dropbox
import pickle

# 📌 Configuración de acceso a Dropbox
DROPBOX_ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUÍ"
dbx = dropbox.Dropbox(DROPBOX_ACCESS_TOKEN)

# 📌 Configuración de rutas
DROPBOX_DATA_PATH = "/Commodities/data/"
DROPBOX_PROCESSED_PATH = "/Commodities/processed_commodities/"
DROPBOX_REPORTS_PATH = "/Commodities/outputs/"

# 📌 Función para listar los commodities disponibles
def listar_commodities():
    _, res = dbx.files_list_folder(DROPBOX_PROCESSED_PATH, recursive=False).items()
    commodities = [entry.name.replace("df_final_", "").replace(".pkl", "") for entry in res]
    return commodities

# 📌 Función para cargar el pickle desde Dropbox
def cargar_pickle(commodity):
    file_path = f"{DROPBOX_PROCESSED_PATH}df_final_{commodity}.pkl"
    _, res = dbx.files_download(file_path)
    df = pickle.loads(res.content)
    return df

# 📌 Función para procesar nuevos datos y generar un nuevo pickle
def procesar_nuevos_datos(commodity):
    # 🚀 Simulación de procesamiento (reemplaza esto con tu pipeline real)
    df_nuevo = pd.DataFrame(np.random.rand(10, 5), columns=[f"Var{i}" for i in range(5)])
    
    # Guardar en Dropbox
    pickle_data = pickle.dumps(df_nuevo)
    dbx.files_upload(pickle_data, f"{DROPBOX_PROCESSED_PATH}df_final_{commodity}.pkl", mode=dropbox.files.WriteMode("overwrite"))
    return df_nuevo

# 📌 Función para generar un reporte basado en el pickle cargado
def generar_reporte(df, commodity):
    output_path = f"Reporte_{commodity}.xlsx"
    df.to_excel(output_path, index=False)

    # Subir el reporte a Dropbox
    with open(output_path, "rb") as f:
        dbx.files_upload(f.read(), f"{DROPBOX_REPORTS_PATH}Reporte_{commodity}.xlsx", mode=dropbox.files.WriteMode("overwrite"))

    return output_path

# 📌 Interfaz con Streamlit
st.title("📊 Generador de Reportes para Commodities")

# 📌 Selección de commodity
commodities = listar_commodities()
commodity_seleccionado = st.selectbox("Selecciona un Commodity", commodities)

# 📌 Botón para cargar datos procesados
if st.button("📂 Cargar Datos Procesados"):
    df = cargar_pickle(commodity_seleccionado)
    st.write(df)

# 📌 Botón para procesar nuevos datos y actualizar pickle
if st.button("🔄 Procesar Nuevos Datos"):
    df_nuevo = procesar_nuevos_datos(commodity_seleccionado)
    st.success(f"Datos procesados y guardados para {commodity_seleccionado}.")
    st.write(df_nuevo)

# 📌 Botón para generar y descargar el reporte
if st.button("📊 Generar Reporte"):
    df = cargar_pickle(commodity_seleccionado)
    reporte_path = generar_reporte(df, commodity_seleccionado)
    st.success(f"Reporte generado: {reporte_path}")
    with open(reporte_path, "rb") as f:
        st.download_button("📥 Descargar Reporte", f, file_name=reporte_path)
