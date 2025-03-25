import subprocess
import sys
import os

# Obtener la ruta del directorio donde está el ejecutable o script
base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Construir la ruta al script de Streamlit (dashboard.py)
script_path = os.path.join(base_dir, "dashboard.py")

# Verificar si el archivo dashboard.py existe en la ubicación esperada
if not os.path.exists(script_path):
    print(f"Error: No se encontró el archivo {script_path}")
    sys.exit(1)

# Comando para ejecutar Streamlit desde la carpeta correcta
command = f'cd "{base_dir}" && streamlit run "{script_path}"'

print(f"Ejecutando: {command}")  # Mensaje de depuración

# Ejecutar el comando en la terminal
subprocess.run(command, shell=True, check=True)
