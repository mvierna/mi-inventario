import csv
import subprocess
import os

def formatear_precio_abaco(precio_str):
    """
    Convierte el formato raro de Abaco (ej: '16.900') a euros reales (ej: '1,69')
    """
    if not precio_str or str(precio_str).strip() == "":
        return "-"
    
    precio_limpio = str(precio_str).replace(".", "").strip()
    try:
        precio_num = float(precio_limpio) / 10000
        return f"{precio_num:.2f}".replace(".", ",")
    except ValueError:
        return str(precio_str)

def limpiar_datos():
    archivo = 'TIENDA.csv'
    
    # 1. Comprobar si el archivo existe en la carpeta
    if not os.path.exists(archivo):
        print(f"-> AVISO: No se encuentra el archivo '{archivo}'. Se omite la limpieza de stock.")
        return set()

    print("-> Procesando TIENDA.csv (Stock Diario)...")
    datos_limpios = []
    eans_tienda = set() # Guardará los EANs para usarlos luego como filtro
    
    try:
        # 2. Leer el archivo e inspeccionar su estructura (CÓDIGO ORIGINAL ROBUSTO)
        with open(archivo, 'r', encoding='latin-1') as f:
            primera_linea = f.readline()
            delimitador_entrada = ';' if ';' in primera_linea else '\t'
            f.seek(0)
            lector = list(csv.reader(f, delimiter=delimitador_entrada))

        if not lector:
            print("-> AVISO: El archivo está vacío.")
            return set()

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
                print("   El archivo TIENDA.csv YA está limpio y preparado para la PWA.")
                # Recopilar los EANs aunque ya esté limpio
                for fila in lector:
                    if len(fila) > 0:
                        ean_limpio = fila[0].strip().replace('.0', '')
                        if ean_limpio and ean_limpio.upper() not in ['EAN', 'CODIGO']:
                            eans_tienda.add(ean_limpio)
                return eans_tienda

        print("   Se ha detectado una exportación nueva de Ábaco. Iniciando limpieza profunda...")

        # 3. Procesar la exportación con auto-alineación
        for fila in lector:
            if len(fila) < 3:
                continue
                
            # AUTO-ALINEACIÓN
            shift = 0
            if fila[0].strip().upper() == 'FALSE':
                shift = 1
            elif not (fila[0].strip().isdigit() and len(fila[0].strip()) >= 6):
                if len(fila) > 1 and fila[1].strip().isdigit() and len(fila[1].strip()) >= 6:
                    shift = 1

            ean = fila[0 + shift].strip() if len(fila) > 0 + shift else ""
            ean = ean.replace('.0', '')
            
            if ean.upper() in ['EAN', 'CODIGO', 'CÓDIGO', 'DESIGNACIÓN', 'DESIGNACION'] or not ean:
                continue

            desc = fila[1 + shift].strip() if len(fila) > 1 + shift else ""
            stock = fila[2 + shift].strip() if len(fila) > 2 + shift else "0"
            rayon = fila[3 + shift].strip() if len(fila) > 3 + shift else "-"
            pvc = fila[4 + shift].strip() if len(fila) > 4 + shift else "-"
            
            # BÚSQUEDA INTELIGENTE DE FECHA Y VENTAS
            fecha = "-"
            ventas = "0"
            fechas_encontradas = []
            
            for i in range(5 + shift, len(fila)):
                val = str(fila[i]).strip()
                if '/' in val and any(c.isdigit() for c in val):
                    fechas_encontradas.append((i, val))
                    
            if fechas_encontradas:
                idx_fecha, val_fecha = fechas_encontradas[-1]
                fecha = val_fecha
                if ' ' in fecha and ':' in fecha:
                    fecha = fecha.split(' ')[0]
                if len(fila) > idx_fecha + 1 and str(fila[idx_fecha + 1]).strip() != "":
                    ventas = str(fila[idx_fecha + 1]).strip()
                    
            datos_limpios.append([ean, desc, stock, rayon, pvc, fecha, ventas])
            eans_tienda.add(ean)

    except Exception as e:
        print(f"❌ Error al procesar TIENDA.csv: {e}")
        return set()

    if not datos_limpios:
        print("   Atención: No se generaron datos de Tienda.")
        return set()

    try:
        # 4. Guardar archivo final preparado para la web
        with open(archivo, 'w', encoding='utf-8', newline='') as f:
            escritor = csv.writer(f, delimiter=';')
            escritor.writerows(datos_limpios)
            
        print(f"   ¡Limpieza completada! {len(datos_limpios)} artículos formateados.")
        return eans_tienda
        
    except Exception as e:
        print(f"❌ Error al guardar TIENDA.csv: {e}")
        return set()

def procesar_maestro(eans_en_tienda):
    archivo_maestro = 'stock cero.csv'
    print(f"-> Procesando {archivo_maestro} (Base Maestra)...")
    
    if not os.path.exists(archivo_maestro):
        print(f"   ⚠️ Archivo '{archivo_maestro}' no encontrado. Se saltará este paso.")
        return

    try:
        # Leer usando la misma técnica robusta que en Tienda
        with open(archivo_maestro, 'r', encoding='latin-1') as f:
            primera_linea = f.readline()
            delimitador_entrada = ';' if ';' in primera_linea else '\t'
            f.seek(0)
            lector = list(csv.reader(f, delimiter=delimitador_entrada))

        if not lector or len(lector) < 2:
            print("   ⚠️ El archivo maestro está vacío o no tiene datos.")
            return

        cabeceras = [str(c).strip().upper() for c in lector[0]]
        
        # Encontrar los índices de las columnas dinámicamente
        idx_ean = 0
        idx_desc = 1
        idx_pv = 4
        idx_fecha = 5
        
        for i, col in enumerate(cabeceras):
            if 'EAN' in col: idx_ean = i
            elif 'DESIG' in col: idx_desc = i
            elif col == 'PV': idx_pv = i
            elif 'DATE' in col or 'MOUVEMENT' in col or 'FECHA' in col: idx_fecha = i

        maestro_limpio = []
        maestro_limpio.append(['EAN', 'DESCRIPCION', 'PVP_MAESTRO', 'ULTIMA_VENTA']) 
        eans_procesados = set()

        for fila in lector[1:]:
            if len(fila) > idx_ean:
                ean = str(fila[idx_ean]).strip().replace('.0', '')
                
                # Evitar EANs vacíos, duplicados en el maestro, o que YA ESTÉN en TIENDA.csv
                if not ean or ean in eans_procesados or ean in eans_en_tienda:
                    continue
                    
                desc = fila[idx_desc].strip() if len(fila) > idx_desc else ""
                pv = fila[idx_pv].strip() if len(fila) > idx_pv else ""
                fecha = fila[idx_fecha].strip() if len(fila) > idx_fecha else ""
                
                # APLICAMOS LA CORRECCIÓN MATEMÁTICA DEL PRECIO
                pv_formateado = formatear_precio_abaco(pv)
                
                maestro_limpio.append([ean, desc, pv_formateado, fecha])
                eans_procesados.add(ean)

        # Guardar archivo filtrado y comprimido
        with open('MAESTRO_FILTRADO.csv', 'w', encoding='utf-8-sig', newline='') as f:
            escritor = csv.writer(f, delimiter=';')
            escritor.writerows(maestro_limpio)
            
        print(f"   MAESTRO_FILTRADO.csv generado con éxito ({len(maestro_limpio)-1} referencias sin stock procesadas).")

    except Exception as e:
        print(f"❌ Error procesando el archivo maestro: {e}")

def subir_a_github():
    print("-> Sincronizando TODOS los datos y código con GitHub...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Actualización automática de inventario, maestro y código'], check=False)
        subprocess.run(['git', 'pull', '--rebase'], check=False)
        subprocess.run(['git', 'push'], check=True)
        print("✅ ¡Sincronización completada! Todos los cambios están en la nube.")
    except Exception as e:
        print(f"❌ Error al sincronizar con GitHub: {e}")

if __name__ == '__main__':
    print("="*60)
    print(" INICIANDO SECUENCIA DE ACTUALIZACIÓN COMPLETA")
    print("="*60)
    
    # 1. Limpiamos la tienda y obtenemos los EAN que SÍ tienen stock
    eans_actuales = limpiar_datos()
    
    # 2. Procesamos el maestro filtrando los que ya tenemos
    if eans_actuales is not None:
        procesar_maestro(eans_actuales)
    
    # 3. Subimos todo a la web
    subir_a_github()
    
    print("="*60)
    print(" ACTUALIZACIÓN FINALIZADA")
    print("="*60)
    input("\nPresiona ENTER para cerrar esta ventana...")