import csv
import subprocess
import os
from datetime import datetime

def formatear_precio_abaco(precio_str):
    if not precio_str or str(precio_str).strip() == "" or str(precio_str).strip() == "-":
        return "-"
    
    precio_limpio = str(precio_str).replace(".", "").strip()
    try:
        precio_num = float(precio_limpio) / 10000
        return f"{precio_num:.2f}".replace(".", ",")
    except ValueError:
        return str(precio_str)

def limpiar_cantidad_abaco(val_str):
    if not val_str or str(val_str).strip() == "": 
        return "0"
    val = str(val_str).strip()
    if val.endswith('.0000'): 
        val = val[:-5]
    elif val.endswith('.000'): 
        val = val[:-4]
    val = val.replace('.', '')
    if val == "" or val == "-": 
        return "0"
    return val

def limpiar_ean(ean_raw):
    return str(ean_raw).replace('="', '').replace('"', '').replace('=', '').strip().replace('.0', '')

def leer_csv_robusto(ruta):
    """Lee detectando automáticamente si es UTF-8 o Latin-1 para no romper tildes."""
    encoding_detectado = 'utf-8-sig'
    try:
        with open(ruta, 'r', encoding='utf-8-sig') as f_test:
            f_test.read()
    except UnicodeDecodeError:
        encoding_detectado = 'latin-1'

    with open(ruta, 'r', encoding=encoding_detectado, errors='replace') as f:
        primera_linea = f.readline()
        delimitador = ';' if ';' in primera_linea else (',' if ',' in primera_linea else '\t')
        f.seek(0)
        return list(csv.reader(f, delimiter=delimitador))

def limpiar_datos():
    archivo = 'TIENDA.csv'
    if not os.path.exists(archivo):
        print(f"-> AVISO: No se encuentra '{archivo}'. Se omite la limpieza.")
        return set()

    print("-> Procesando TIENDA.csv (Stock Diario)...")
    datos_limpios = []
    eans_tienda = set()
    
    try:
        lector = leer_csv_robusto(archivo)
        if not lector: 
            return set()

        fila_muestra = None
        for fila in lector:
            if len(fila) > 1 and limpiar_ean(fila[0]).upper() not in ['EAN', 'CODIGO', 'CÓDIGO', 'FALSE'] and fila[1].strip().upper() != 'EAN':
                fila_muestra = fila
                break

        if fila_muestra:
            col0 = limpiar_ean(fila_muestra[0])
            col1 = fila_muestra[1].strip() if len(fila_muestra) > 1 else ""
            if len(col0) >= 6 and (col0.isdigit() or 'E+' in col0.upper()) and any(c.isalpha() for c in col1) and len(fila_muestra) == 7:
                print("   TIENDA.csv YA está limpio.")
                for fila in lector:
                    if len(fila) > 0:
                        ean_limpio = limpiar_ean(fila[0])
                        if ean_limpio and ean_limpio.upper() not in ['EAN', 'CODIGO']: 
                            eans_tienda.add(ean_limpio)
                return eans_tienda

        print("   Iniciando limpieza profunda de TIENDA...")
        for fila in lector:
            if len(fila) < 3: 
                continue
                
            shift = 1 if limpiar_ean(fila[0]).upper() == 'FALSE' else 0
            if shift == 0 and not (limpiar_ean(fila[0]).isdigit() and len(limpiar_ean(fila[0])) >= 6) and len(fila) > 1 and limpiar_ean(fila[1]).isdigit() and len(limpiar_ean(fila[1])) >= 6:
                shift = 1

            ean = limpiar_ean(fila[0 + shift] if len(fila) > 0 + shift else "")
            if ean.upper() in ['EAN', 'CODIGO', 'CÓDIGO', 'DESIGNACIÓN', 'DESIGNACION'] or not ean: 
                continue

            desc = fila[1 + shift].strip() if len(fila) > 1 + shift else ""
            stock = fila[2 + shift].strip() if len(fila) > 2 + shift else "0"
            rayon = fila[3 + shift].strip() if len(fila) > 3 + shift else "-"
            pvc = fila[4 + shift].strip() if len(fila) > 4 + shift else "-"
            
            fecha, ventas = "-", "0"
            fechas_encontradas = [(i, str(fila[i]).strip()) for i in range(5 + shift, len(fila)) if '/' in str(fila[i]) and any(c.isdigit() for c in str(fila[i]))]
            
            if fechas_encontradas:
                idx_fecha, fecha = fechas_encontradas[-1]
                if ' ' in fecha and ':' in fecha: 
                    fecha = fecha.split(' ')[0]
                if len(fila) > idx_fecha + 1 and str(fila[idx_fecha + 1]).strip() != "": 
                    ventas = str(fila[idx_fecha + 1]).strip()
                    
            datos_limpios.append([ean, desc, stock, rayon, pvc, fecha, ventas])
            eans_tienda.add(ean)

        # CAMBIO CLAVE: Guardar con utf-8-sig para que la PWA y Excel lean bien los acentos
        with open(archivo, 'w', encoding='utf-8-sig', newline='') as f:
            csv.writer(f, delimiter=';').writerows(datos_limpios)
        print(f"   ¡Limpieza completada! {len(datos_limpios)} artículos.")
        return eans_tienda
    except Exception as e:
        print(f"❌ Error TIENDA: {e}")
        return set()

def procesar_sin_stock(eans_en_tienda):
    archivos_posibles = ['SIN STOCK_2.csv', 'SIN STOCK.csv']
    archivo_origen = None
    
    for f in archivos_posibles:
        if os.path.exists(f):
            archivo_origen = f
            break
            
    if not archivo_origen:
        print("   ⚠️ Archivos de SIN STOCK no encontrados.")
        return

    print(f"-> Procesando {archivo_origen}...")
    try:
        lector = leer_csv_robusto(archivo_origen)
        if len(lector) < 2: 
            return
        
        cabeceras = [str(c).strip().upper().replace('"', '').replace('\ufeff', '') for c in lector[0]]
        
        idx_ean, idx_desc, idx_pv, idx_fecha = -1, -1, -1, -1
        idx_stock, idx_ventas, idx_rayon_code, idx_rayon_lib = -1, -1, -1, -1
        
        for i, col in enumerate(cabeceras):
            if 'EAN' in col:
                idx_ean = i
            elif ('CÓDIGO' in col or 'CODIGO' in col) and 'ELEMENTO' in col:
                idx_rayon_code = i
            elif idx_ean == -1 and ('CÓDIGO' in col or 'CODIGO' in col):
                idx_ean = i
            elif 'DESIG' in col or 'ARTICULO' in col:
                idx_desc = i
            elif col == 'PV' or 'PVC' in col or 'PRECIO' in col:
                idx_pv = i
            elif 'DATE' in col or 'MOUVEMENT' in col or 'FECHA' in col or 'ÚLTIMA' in col or 'ULTIMA' in col or 'LITMA' in col:
                idx_fecha = i
            elif 'STOCK' in col:
                idx_stock = i
            elif 'UV' in col or 'VENDUES' in col or 'VENTAS' in col:
                idx_ventas = i
            elif 'LIB. RAYON' in col:
                idx_rayon_lib = i
            elif (col == 'RAYON' or col == 'RAYÓN') and idx_rayon_code == -1:
                idx_rayon_code = i

        if idx_ean == -1 or idx_desc == -1:
            print(f"   ❌ Error: No se detectan columnas principales. Cabeceras detectadas: {cabeceras}")
            return

        sin_stock_limpio = [['EAN', 'DESCRIPCION', 'STOCK', 'RAYON', 'PVC', 'FECHA', 'VENTAS']]
        eans_procesados = set()

        for fila in lector[1:]:
            if len(fila) > idx_ean:
                ean = limpiar_ean(fila[idx_ean])
                
                if not ean or ean in eans_procesados or ean in eans_en_tienda: 
                    continue
                    
                desc = fila[idx_desc].strip() if len(fila) > idx_desc else ""
                pv = fila[idx_pv].strip() if idx_pv != -1 and len(fila) > idx_pv else "-"
                
                fecha = fila[idx_fecha].strip() if idx_fecha != -1 and len(fila) > idx_fecha else "-"
                if ' ' in fecha and ':' in fecha:
                    fecha = fecha.split(' ')[0]
                
                stock = limpiar_cantidad_abaco(fila[idx_stock]) if idx_stock != -1 and len(fila) > idx_stock else "0"
                ventas = limpiar_cantidad_abaco(fila[idx_ventas]) if idx_ventas != -1 and len(fila) > idx_ventas else "0"
                
                r_code = fila[idx_rayon_code].strip() if idx_rayon_code != -1 and len(fila) > idx_rayon_code else ""
                r_lib = fila[idx_rayon_lib].strip() if idx_rayon_lib != -1 and len(fila) > idx_rayon_lib else ""
                
                if r_code and r_lib: 
                    rayon = f"{r_code} {r_lib}"
                elif r_lib: 
                    rayon = r_lib
                elif r_code: 
                    rayon = r_code
                else: 
                    rayon = "-"
                
                sin_stock_limpio.append([ean, desc, stock, rayon, formatear_precio_abaco(pv), fecha, ventas])
                eans_procesados.add(ean)

        with open('SIN_STOCK_FILTRADO.csv', 'w', encoding='utf-8-sig', newline='') as f:
            csv.writer(f, delimiter=';').writerows(sin_stock_limpio)
        print(f"   SIN_STOCK_FILTRADO.csv generado con éxito ({len(sin_stock_limpio)-1} referencias).")
    except Exception as e:
        print(f"❌ Error en SIN STOCK: {e}")

def subir_a_github():
    print("-> Sincronizando GitHub...")
    try:
        subprocess.run(['git', 'add', '-A'], check=True)
        resultado_status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=True)
        
        if resultado_status.stdout.strip():
            ahora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            mensaje = f"Sincronización automática: {ahora}"
            subprocess.run(['git', 'commit', '-m', mensaje], check=True)
            print(f"   Commit generado: '{mensaje}'")
        else:
            print("   ℹ️ No hay archivos nuevos ni modificados respecto al repositorio local.")

        subprocess.run(['git', 'pull', '--rebase'], check=False)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("✅ Sincronización completada con éxito en GitHub.")
    except Exception as e:
        print(f"❌ Error durante la sincronización Git: {e}")

if __name__ == '__main__':
    print("="*60)
    eans_actuales = limpiar_datos()
    if eans_actuales is not None:
        procesar_sin_stock(eans_actuales)
    subir_a_github()
    print("="*60)