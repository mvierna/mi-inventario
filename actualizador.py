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
            delimitador_entrada = ';' if ';' in primera_linea else '\t'
            f.seek(0)
            lector = list(csv.reader(f, delimiter=delimitador_entrada))

        if not lector:
            print("El archivo está vacío.")
            return False

        # Comprobación de si el archivo ya está limpio
        fila_muestra = None
        for fila in lector:
            if len(fila) > 1 and fila[0].strip().upper() not in ['EAN', 'CODIGO', 'CÓDIGO', 'FALSE'] and fila[1].strip().upper() != 'EAN':
                fila_muestra = fila
                break

        if fila_muestra:
            col0 = fila_muestra[0].strip()
            col1 = fila_muestra[1].strip() if len(fila_muestra) > 1 else ""
            tiene_letras_col1 = any(c.isalpha() for c in col1)
            es_ean_col0 = len(col0) >= 6 and (col0.isdigit() or 'E+' in col0.upper())

            if es_ean_col0 and tiene_letras_col1 and len(fila_muestra) == 7:
                print("--> El archivo TIENDA.csv YA está limpio y preparado para la PWA.")
                print("--> Se conservará el archivo intacto.")
                return True

        print("--> Se ha detectado una exportación nueva de Ábaco. Iniciando limpieza profunda...")

        # 3. Procesar la exportación con auto-alineación
        for fila in lector:
            if len(fila) < 3:
                continue
                
            # AUTO-ALINEACIÓN: Detectar si existe una columna basura inicial
            shift = 0
            if fila[0].strip().upper() == 'FALSE':
                shift = 1
            elif not (fila[0].strip().isdigit() and len(fila[0].strip()) >= 6):
                # Si la col 0 no es EAN pero la col 1 sí lo es, ajustamos el desplazamiento
                if len(fila) > 1 and fila[1].strip().isdigit() and len(fila[1].strip()) >= 6:
                    shift = 1

            ean = fila[0 + shift].strip() if len(fila) > 0 + shift else ""
            
            if ean.upper() in ['EAN', 'CODIGO', 'CÓDIGO', 'DESIGNACIÓN', 'DESIGNACION'] or not ean:
                continue

            # Extracción protegida de datos principales
            desc = fila[1 + shift].strip() if len(fila) > 1 + shift else ""
            stock = fila[2 + shift].strip() if len(fila) > 2 + shift else "0"
            rayon = fila[3 + shift].strip() if len(fila) > 3 + shift else "-"
            pvc = fila[4 + shift].strip() if len(fila) > 4 + shift else "-"
            
            # BÚSQUEDA INTELIGENTE DE FECHA Y VENTAS
            fecha = "-"
            ventas = "0"
            fechas_encontradas = []
            
            # Comenzamos a buscar fechas a partir de la columna siguiente al PVC
            for i in range(5 + shift, len(fila)):
                val = str(fila[i]).strip()
                # Una fecha válida tendrá al menos una barra (/) y números
                if '/' in val and any(c.isdigit() for c in val):
                    fechas_encontradas.append((i, val))
                    
            if fechas_encontradas:
                # Tomar SIEMPRE la última fecha de la fila ignorando fechas temporales de exportación
                idx_fecha, val_fecha = fechas_encontradas[-1]
                fecha = val_fecha
                
                # Limpiamos la hora si está presente
                if ' ' in fecha and ':' in fecha:
                    fecha = fecha.split(' ')[0]
                    
                # Las ventas siempre estarán en la celda inmediatamente posterior a la última fecha
                if len(fila) > idx_fecha + 1 and str(fila[idx_fecha + 1]).strip() != "":
                    ventas = str(fila[idx_fecha + 1]).strip()
                    
            datos_limpios.append([ean, desc, stock, rayon, pvc, fecha, ventas])

    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return False

    if not datos_limpios:
        print("Atención: No se generaron datos. Operación abortada.")
        return False

    try:
        # 4. Guardar archivo final preparado para la web
        with open(archivo, 'w', encoding='utf-8', newline='') as f:
            escritor = csv.writer(f, delimiter=';')
            escritor.writerows(datos_limpios)
            
        print(f"¡Limpieza completada! {len(datos_limpios)} artículos formateados correctamente.")
        return True
        
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        return False

def subir_a_github():
    print("\nIniciando sincronización con GitHub...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Actualización automática de interfaz y stock por RPA'], check=False)
        print("Sincronizando con los datos remotos...")
        subprocess.run(['git', 'pull', '--rebase', 'origin', 'main'], check=False)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("¡Sincronización completada! Todos los datos ya están en la nube.")
    except Exception as e:
        print(f"Error al sincronizar con GitHub: {e}")

if __name__ == '__main__':
    if limpiar_datos():
        subir_a_github()
    else:
        print("\n[CANCELADO] No se realizarán cambios en GitHub.")
    
    input("\nPresiona ENTER para cerrar esta ventana...")