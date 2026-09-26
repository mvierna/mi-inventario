import csv
import subprocess
import os

def limpiar_datos():
    print("Analizando el archivo TIENDA.csv...")
    archivo = 'TIENDA.csv'
    
    # Comprobar si el archivo existe
    if not os.path.exists(archivo):
        print(f"Error: No se encuentra el archivo '{archivo}'.")
        return False

    datos_limpios = []
    
    try:
        # 1. Leer el archivo para inspeccionar su estructura
        with open(archivo, 'r', encoding='latin-1') as f:
            primera_linea = f.readline()
            delimitador_entrada = ';' if ';' in primera_linea else '\t'
            f.seek(0)
            
            lector = list(csv.reader(f, delimiter=delimitador_entrada))

        if not lector:
            print("El archivo está vacío.")
            return False

        # Buscar la primera fila de datos real (saltando cabeceras)
        fila_muestra = None
        for fila in lector:
            if len(fila) > 1 and fila[0].strip().upper() != 'EAN' and fila[1].strip().upper() != 'EAN':
                fila_muestra = fila
                break

        if not fila_muestra:
            print("No se encontraron filas con datos de productos.")
            return False

        # COMPROBACIÓN INTELIGENTE: ¿El archivo ya está limpio para la PWA?
        # Si tiene 6 columnas y la primera columna (fila[0]) es numérica/EAN, ya está procesado.
        if len(fila_muestra) == 6 and (fila_muestra[0].strip().isdigit() or len(fila_muestra[0].strip()) >= 8):
            print("--> El archivo TIENDA.csv YA está limpio y preparado para la PWA.")
            print("--> Se conservará el archivo intacto sin modificar la columna A.")
            return True

        print("--> Se ha detectado una exportación nueva de Ábaco. Iniciando limpieza...")

        # Processar la exportación bruta de Ábaco
        for fila in lector:
            if len(fila) > 2:
                ean = fila[1].strip()
                
                # Saltar cabecera o filas sin EAN
                if ean.upper() == 'EAN' or not ean:
                    continue
                    
                desc = fila[2].strip() if len(fila) > 2 else ""
                stock = fila[3].strip() if len(fila) > 3 else ""
                pvc = fila[4].strip() if len(fila) > 4 else ""
                
                # Omitir columna fantasma de Ábaco (fila[5])
                fecha = fila[6].strip() if len(fila) > 6 else ""
                ventas = fila[7].strip() if len(fila) > 7 else ""
                
                # Limpiar hora si existe en el campo fecha
                if '/' in fecha and ':' in fecha and ' ' in fecha:
                    fecha = fecha.split(' ')[0]
                    
                datos_limpios.append([ean, desc, stock, pvc, fecha, ventas])

    except Exception as e:
        print(f"Error al leer el archivo de Ábaco: {e}")
        return False

    # Seguridad: Si no se extrajo ningún dato, no sobrescribir el archivo
    if not datos_limpios:
        print("Atención: No se generaron datos. Operación abortada para no dañar la base de datos.")
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
    print("\nIniciando sincronización con GitHub...")
    try:
        # 1. Preparar todos los archivos modificados
        subprocess.run(['git', 'add', '.'], check=True)
        
        # 2. Crear el commit local
        subprocess.run(['git', 'commit', '-m', 'Actualización automática de interfaz y stock por RPA'], check=False)
        
        # 3. Traer cambios remotos y reordenar el historial
        print("Sincronizando con los datos remotos de GitHub...")
        subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=False)
        
        # 4. Enviar cambios a la nube
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("¡Sincronización completada! Todos los archivos (web y datos) ya están en la nube.")
    except Exception as e:
        print(f"Error al intentar subir los datos a GitHub: {e}")

if __name__ == '__main__':
    if limpiar_datos():
        subir_a_github()
    else:
        print("\n[CANCELADO] No se realizarán cambios en GitHub debido a un problema con el archivo de datos.")
    
    input("\nPresiona ENTER para cerrar esta ventana...")