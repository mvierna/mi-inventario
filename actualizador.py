import pandas as pd
import os
import subprocess

def limpiar_y_rescatar_ean(valor):
    """
    Convierte cualquier formato numérico (incluso corruptos por Excel en notación científica
    como 8,4108E+12 o 9,4E+12) en un código EAN de texto puro sin decimales ni exponentes.
    
    Parámetros:
        valor (str): El dato contenido en la celda del EAN.
    Retorna:
        str: Cadena de texto con el código EAN limpio.
    """
    # Cambiamos comas decimales por puntos para permitir la conversión matemática
    v = str(valor).strip().replace(',', '.')
    
    # Si la celda está vacía o es la fila del encabezado ('EAN', 'Code', etc.), la ignoramos
    if not v or v.lower() in ['ean', 'code', 'nan', 'none']:
        return ''
    
    try:
        # Convertimos la notación científica (8.4108E+12) a número flotante real
        numero_real = float(v)
        # Convertimos a int para eliminar decimales (.0) y obtener la cifra completa
        return str(int(numero_real))
    except ValueError:
        # Si el código contiene letras o es alfanumérico, quitamos sufijos decimales si existen
        return v.replace('.0', '')

def quitar_cero_inicial(codigo):
    """
    Elimina el cero a la izquierda en códigos de 13 dígitos para generar soporte dual
    de escaneo (12 y 13 dígitos).
    """
    codigo_str = str(codigo).strip()
    if len(codigo_str) == 13 and codigo_str.startswith('0'):
        return codigo_str[1:]
    return codigo_str

def procesar_inventario():
    """
    Función principal que procesa el CSV, elimina la Columna A, convierte los EANs
    a formato numérico completo y sube el resultado a GitHub.
    """
    nombre_archivo = 'TIENDA.csv'
    
    if not os.path.exists(nombre_archivo):
        print(f"[ERROR] No se encuentra el archivo {nombre_archivo}")
        return

    print("1. Leyendo TIENDA.csv y eliminando la columna A sobrante...")
    # Leemos el archivo CSV sin interpretar la primera fila como encabezado fijo
    df = pd.read_csv(nombre_archivo, sep=';', dtype=str, encoding='latin1', header=None)

    total_columnas = df.shape[1]
    print(f"   -> Columnas detectadas en el archivo: {total_columnas}")

    # REGLA DE DESCARTE: Si el archivo tiene 4 columnas o la columna 0 contiene 'False'
    if total_columnas >= 4:
        print("   -> Detectadas 4 columnas. Eliminando la Columna A sobrante (Columna 0)...")
        df = df.drop(columns=[0])
    elif df[0].astype(str).str.contains('False', case=False, na=False).any():
        print("   -> Detectados valores 'False' en la primera columna. Eliminando Columna A...")
        df = df.drop(columns=[0])

    # Nos quedamos con las 3 columnas de datos principales
    df = df.iloc[:, :3]
    df.columns = ['EAN', 'DESCRIPCION', 'STOCK']

    print("2. Rescatando y formateando códigos EAN (notación científica -> números completos)...")
    # Aplicamos la limpieza matemática a la columna EAN
    df['EAN'] = df['EAN'].apply(limpiar_y_rescatar_ean)
    
    # Descartamos filas vacías o que correspondían a los encabezados
    df = df[df['EAN'] != '']

    print("3. Generando soporte dual para escáner (12 y 13 dígitos)...")
    # Versión formateada a 13 dígitos
    df_13 = df.copy()
    df_13['EAN'] = df_13['EAN'].str.zfill(13)

    # Versión formateada a 12 dígitos
    df_12 = df_13.copy()
    df_12['EAN'] = df_12['EAN'].apply(quitar_cero_inicial)

    # Combinamos ambas tablas y eliminamos códigos duplicados
    df_final = pd.concat([df_13, df_12], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=['EAN'])

    print(f"Total de referencias preparadas y listas para la app: {len(df_final)}")

    print("4. Guardando el archivo TIENDA.csv pulido...")
    # Guardamos en formato CSV limpio, separado por punto y coma, sin índices ni encabezados
    df_final.to_csv(nombre_archivo, index=False, header=False, sep=';', encoding='utf-8')

    print("5. Subiendo datos a GitHub...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Eliminada columna A y corregida notacion cientifica EAN'], check=False)
        subprocess.run(['git', 'pull', 'origin', 'main', '--rebase'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("\n¡[ÉXITO] Base de datos actualizada correctamente en GitHub!")
    except Exception as e:
        print(f"\n[ERROR] Fallo durante la subida a GitHub: {e}")

if __name__ == '__main__':
    procesar_inventario()