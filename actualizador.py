import pandas as pd
import os
import subprocess

def limpiar_y_rescatar_ean(valor):
    """
    Convierte cualquier formato numérico (incluso en notación científica como 8,41E+12)
    en un código EAN de texto puro sin decimales ni exponentes.
    """
    v = str(valor).strip().replace(',', '.')
    if not v or v.lower() in ['ean', 'code', 'nan', 'none']:
        return ''
    
    try:
        numero_real = float(v)
        return str(int(numero_real))
    except ValueError:
        return v.replace('.0', '')

def quitar_cero_inicial(codigo):
    """
    Elimina el cero a la izquierda en códigos de 13 dígitos para generar soporte dual.
    """
    codigo_str = str(codigo).strip()
    if len(codigo_str) == 13 and codigo_str.startswith('0'):
        return codigo_str[1:]
    return codigo_str

def procesar_inventario():
    """
    Lee TIENDA.csv, elimina la Columna A sobrante, procesa 6 columnas de datos
    (EAN, Descrip, Stock, Precio, Fecha Recep, Ventas Recep) y actualiza GitHub.
    """
    nombre_archivo = 'TIENDA.csv'
    
    if not os.path.exists(nombre_archivo):
        print(f"[ERROR] No se encuentra el archivo {nombre_archivo}")
        return

    print("1. Leyendo TIENDA.csv y ajustando estructura ampliada...")
    df = pd.read_csv(nombre_archivo, sep=';', dtype=str, encoding='latin1', header=None)

    total_columnas = df.shape[1]
    print(f"   -> Columnas detectadas en el archivo original: {total_columnas}")

    # REGLA: Si hay 7 o más columnas (Columna A sobrante + 6 de datos), eliminamos la Columna A (índice 0)
    if total_columnas >= 7:
        print("   -> Detectadas 7 o más columnas. Eliminando Columna A sobrante...")
        df = df.drop(columns=[0])
    elif df[0].astype(str).str.contains('False', case=False, na=False).any():
        print("   -> Detectados valores 'False' en la primera columna. Eliminando Columna A...")
        df = df.drop(columns=[0])

    # Tomamos las 6 columnas necesarias
    df = df.iloc[:, :6]
    df.columns = ['EAN', 'DESCRIPCION', 'STOCK', 'PRECIO', 'FECHA_RECEPCION', 'VENTAS_RECEPCION']

    print("2. Rescatando y formateando códigos EAN...")
    df['EAN'] = df['EAN'].apply(limpiar_y_rescatar_ean)
    
    # Rellenamos valores vacíos en los nuevos campos por estética
    df['PRECIO'] = df['PRECIO'].fillna('-')
    df['FECHA_RECEPCION'] = df['FECHA_RECEPCION'].fillna('-')
    df['VENTAS_RECEPCION'] = df['VENTAS_RECEPCION'].fillna('0')

    # Descartamos filas vacías
    df = df[df['EAN'] != '']

    print("3. Generando soporte dual para escáner (12 y 13 dígitos)...")
    df_13 = df.copy()
    df_13['EAN'] = df_13['EAN'].str.zfill(13)

    df_12 = df_13.copy()
    df_12['EAN'] = df_12['EAN'].apply(quitar_cero_inicial)

    # Combinamos ambas tablas y eliminamos códigos duplicados
    df_final = pd.concat([df_13, df_12], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=['EAN'])

    print(f"Total de referencias preparadas para la app: {len(df_final)}")

    print("4. Guardando el archivo TIENDA.csv pulido...")
    df_final.to_csv(nombre_archivo, index=False, header=False, sep=';', encoding='utf-8')

    print("5. Subiendo datos a GitHub...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Soporte para precio, fecha recepcion y ventas'], check=False)
        subprocess.run(['git', 'pull', 'origin', 'main', '--rebase'], check=True)
        subprocess.run(['git', 'push', 'origin', 'main'], check=True)
        print("\n¡[ÉXITO] Base de datos ampliada y subida a GitHub!")
    except Exception as e:
        print(f"\n[ERROR] Fallo durante la subida a GitHub: {e}")

if __name__ == '__main__':
    procesar_inventario()