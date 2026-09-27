import csv
import subprocess
import os

def limpiar_datos():
    print("Analizando el archivo TIENDA.csv...")
    archivo = 'TIENDA.csv'
    
    # 1. Comprobar si el archivo existe en la carpeta
    if not os.path.exists(archivo):
        print(f"Error: No se encuentra el archivo '{archivo}'.")
        return False

    datos_limpios = []
    
    try:
        # 2. Leer el archivo e inspeccionar su estructura
        with open(archivo, 'r', encoding='latin-1') as f:
            primera_linea = f.readline()
            # Detectar si el delimitador es punto y coma o tabulación
            delimitador_entrada = ';' if ';' in primera_linea else '\t'
            f.seek(0)
            
            lector = list(csv.reader(f, delimiter=delimitador_entrada))

        if not lector:
            print("El archivo está vacío.")
            return False

        # Buscar la primera fila de datos real (omitir cabeceras)
        fila_muestra = None
        for fila in lector:
            if len(fila) > 1 and fila[0].strip().upper() not in ['EAN', 'CODIGO', 'CÓDIGO'] and fila[1].strip().upper() != 'EAN':
                fila_muestra = fila
                break

        if not fila_muestra:
            print("No se encontraron filas con datos válidos de productos.")
            return False

        # COMPROBACIÓN INTELIGENTE MEJORADA:
        # En un archivo YA limpio: Columna 0 = EAN (dígitos) y Columna 1 = Descripción (texto con letras).
        # En la exportación de Ábaco: Columna 0 = Código interno, Columna 1 = EAN, Columna 2 = Descripción.
        col0 = fila_muestra[0].strip()
        col1 = fila_muestra[1].strip() if len(fila_muestra) > 1 else ""
        
        tiene_letras_col1 = any(c.isalpha() for c in col1)
        es_ean_col0 = len(col0) >= 8 and col0.isdigit()

        # Solo si Columna 0 es un EAN y Columna 1 es la descripción de texto, consideramos que ya está limpio
        if es_ean_col0 and tiene_letras_col1 and len(fila_muestra) == 6:
            print("--> El archivo TIENDA.csv YA está limpio y preparado para la PWA.")
            print("--> Se conservará el archivo intacto.")
            return True

        print("--> Se ha detectado una exportación nueva de Ábaco. Iniciando limpieza...")

        # 3. Procesar la exportación de Ábaco
        for fila in lector:
            if len(fila) > 2:
                ean = fila[1].strip() if len(fila) > 1 else ""
                
                # Saltar filas de cabecera
                if ean.upper() in ['EAN', 'CODIGO', 'CÓDIGO'] or fila[0].strip().upper() in ['EAN', 'CODIGO', 'CÓDIGO']:
                    continue
                
                # Si el EAN estaba en la primera columna por algún formato especial
                if not ean and len(fila[0].strip()) >= 8 and fila[0].strip().isdigit():
                    ean = fila[0].strip()
                    
                if not ean:
                    continue

                desc = fila[2].strip() if len(fila) > 2 else ""
                stock = fila[3].strip() if len(fila) > 3 else "0"
                pvc = fila[4].strip() if len(fila) > 4 else ""
                
                fecha = fila[6].strip() if len(fila) > 6 else ""
                ventas = fila[7].strip() if len(fila) > 7 else ""
                
                # Limpiar hora si está presente en la fecha
                if '/' in fecha and ':' in fecha and ' ' in fecha:
                    fecha = fecha.split(' ')[0]
                    
                datos_limpios.append([ean, desc, stock, pvc, fecha, ventas])

    except Exception as e:
        print(f"Error al leer el archivo de Ábaco: {e}")
        return False

    if not datos_limpios:
        print("Atención: No se generaron datos. Operación abortada para proteger la base de datos.")
        return False

    try:
        # 4. Guardar el archivo formateado en UTF-8 con delimitador ';'
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
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Actualización automática de interfaz y stock por RPA'], check=False)
        print("Sincronizando con los datos remotos de GitHub...")
        subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=False)
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