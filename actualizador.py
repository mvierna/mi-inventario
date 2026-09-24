import pandas as pd
import os
import subprocess

def limpiar_y_rescatar_ean(valor):
    """
    Convierte cualquier formato numérico (incluso corruptos por Excel como 8,41E+12)
    en un código EAN de texto puro.
    """
    v = str(valor).strip().replace(',', '.') # Cambia comas por puntos por si Excel lo corrompió
    if not v or v.lower() in ['ean', 'code', 'nan']:
        return ''
    
    try:
        # Si el valor es matemático (8.4108E+12 o 8410800000000.0), lo transforma al número real
        numero_real = float(v)
        return str(int(numero_real))
    except ValueError:
        # Si tiene letras (ej. un código interno alfanumérico), lo deja como texto
        return v.replace('.0', '')

def quitar_cero_inicial(codigo):
    codigo_str = str(codigo).strip()
    if len(codigo_str) == 13 and codigo_str.startswith('0'):
        return codigo_str[1:]
    return codigo_str

def procesar_inventario():
    nombre_archivo = 'TIENDA.csv'
    
    if not os.path.exists(nombre_archivo):
        print(f"[ERROR] No se encuentra el archivo {nombre_archivo}")
        return

    print("1. Leyendo TIENDA.csv y limpiando estructura...")
    df = pd.read_csv(nombre_archivo, sep=';', dtype=str, encoding='latin1', header=None)

    # Eliminamos la columna A (False) si existe
    if str(df.iloc[0, 0]).lower() == 'false' or df[0].astype(str).str.contains('False', case=False, na=False).any():
        df = df.drop(columns=[0])
    
    # Aseguramos el mapeo de las 3 columnas principales
    df = df.iloc[:, :3]
    df.columns = ['EAN', 'DESCRIPCION', 'STOCK']

    print("2. Rescatando y formateando códigos de barras...")
    df['EAN'] = df['EAN'].apply(limpiar_y_rescatar_ean)
    
    # Filtramos las filas vacías
    df = df[df['EAN'] != '']

    print("3. Generando soporte dual para escáner (12 y 13 dígitos)...")
    df_13 = df.copy()
    df_13['EAN'] = df_13['EAN'].str.zfill(13)

    df_12 = df_13.copy()
    df_12['EAN'] = df_12['EAN'].apply(quitar_cero_inicial)

    # Unimos y eliminamos los duplicados
    df_final = pd.concat([df_13, df_12], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=['EAN'])

    print(f"Total de referencias listas para la app: {len(df_final)}")

    print("4. Guardando base de datos pulida...")
    df_final.to_csv(nombre_archivo, index=False, header=False, sep=';', encoding='utf-8')

    print("5. Subiendo datos a GitHub...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Blindaje matematico de EAN y soporte dual'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("\n¡[ÉXITO] Todo correcto y en la nube!")
    except Exception as e:
        print(f"\n[ERROR] Fallo en la subida: {e}")

if __name__ == '__main__':
    procesar_inventario()