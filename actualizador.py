import csv
import subprocess
import os

def limpiar_datos():
    print("Limpiando y formateando el archivo de Abaco...")
    archivo = 'TIENDA.csv'
    datos_limpios = []
    
    try:
        # 1. Leer el archivo de Abaco
        with open(archivo, 'r', encoding='latin-1') as f:
            primera_linea = f.readline()
            delimitador_entrada = ';' if ';' in primera_linea else '\t'
            f.seek(0)
            
            lector = csv.reader(f, delimiter=delimitador_entrada)
            
            for fila in lector:
                # Nos aseguramos de que la fila no esté vacía
                if len(fila) > 2:
                    ean = fila[1].strip()
                    
                    # Saltar la cabecera o las filas vacías
                    if ean.upper() == 'EAN' or not ean:
                        continue
                        
                    # Extraer las columnas por su posición exacta
                    desc = fila[2].strip() if len(fila) > 2 else ""
                    stock = fila[3].strip() if len(fila) > 3 else ""
                    pvc = fila[4].strip() if len(fila) > 4 else ""
                    
                    # Nos saltamos fila[5] porque es la columna fantasma de Abaco
                    fecha = fila[6].strip() if len(fila) > 6 else ""
                    ventas = fila[7].strip() if len(fila) > 7 else ""
                    
                    # Limpiar la hora de la fecha
                    if '/' in fecha and ':' in fecha and ' ' in fecha:
                        fecha = fecha.split(' ')[0]
                        
                    # Guardamos solo las 6 columnas perfectas para la PWA
                    datos_limpios.append([ean, desc, stock, pvc, fecha, ventas])
                
    except Exception as e:
        print(f"Error al leer el archivo de Abaco: {e}")
        return False
        
    try:
        # 2. Guardar el archivo formateado
        with open(archivo, 'w', encoding='utf-8', newline='') as f:
            escritor = csv.writer(f, delimiter=';')
            escritor.writerows(datos_limpios)
            
        print(f"¡Limpieza completada! {len(datos_limpios)} artículos formateados correctamente.")
        return True
        
    except Exception as e:
        print(f"Error al guardar el archivo limpio: {e}")
        return False

def subir_a_github():
    print("Iniciando sincronización con GitHub...")
    try:
        # Usamos '.' en vez de 'TIENDA.csv' para registrar index.html y cualquier otro cambio
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Actualizacion automatica de interfaz y stock por RPA'])
        subprocess.run(['git', 'push'], check=True)
        print("¡Sincronización completada! Todos los archivos (web y datos) ya están en la nube.")
    except Exception as e:
        print(f"Error al intentar subir los datos a GitHub: {e}")

if __name__ == '__main__':
    if limpiar_datos():
        subir_a_github()
    
    input("\nPresiona ENTER para cerrar esta ventana...")