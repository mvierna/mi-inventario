import pandas as pd
import os
import subprocess

def quitar_cero_inicial(codigo):
    """
    Si un EAN tiene 13 dígitos y empieza por '0',
    devuelve la versión de 12 dígitos para la pistola de escaneo.
    """
    codigo_str = str(codigo).strip()
    if len(codigo_str) == 13 and codigo_str.startswith('0'):
        return codigo_str[1:]
    return codigo_str

def procesar_inventario():
    nombre_archivo = 'TIENDA.csv'
    
    if not os.path.exists(nombre_archivo):
        print(f"[ERROR] No se encuentra el archivo {nombre_archivo}")
        return

    print("1. Cargando datos de TIENDA.csv manteniendo todas las columnas...")
    # Leemos las 4 columnas originales forzando tipo texto (dtype=str)
    # para evitar conversión a notación científica (8,41E+12)
    df = pd.read_csv(nombre_archivo, sep=';', dtype=str, encoding='latin1', header=None)

    # Nos quedamos con las 4 columnas estructurales (Columna A, EAN, Descripción, Stock)
    df = df.iloc[:, :4]
    df.columns = ['COL_A', 'EAN', 'DESCRIPCION', 'STOCK']

    print("2. Normalizando códigos de barras (EAN)...")
    # Limpiamos nulos y posibles sufijos .0 de Excel
    df['EAN'] = df['EAN'].fillna('')
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    
    # Eliminamos filas donde la cabecera sea el texto 'EAN' o esté vacía
    df = df[~df['EAN'].str.lower().isin(['ean', 'code', ''])]

    # 3. Creación del conjunto de 13 dígitos (con cero a la izquierda)
    df_13 = df.copy()
    df_13['EAN'] = df_13['EAN'].str.zfill(13)

    # 4. Creación del conjunto de 12 dígitos (para escáner)
    df_12 = df_13.copy()
    df_12['EAN'] = df_12['EAN'].apply(quitar_cero_inicial)

    # Combinamos conservando la columna A original en ambos bloques
    df_final = pd.concat([df_13, df_12], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=['EAN'])

    print(f"Total de referencias reales procesadas: {len(df_final)}")

    print(f"3. Sobrescribiendo '{nombre_archivo}' con la columna A intacta...")
    # Guardamos en TIENDA.csv manteniendo el orden de las 4 columnas
    df_final.to_csv(nombre_archivo, index=False, header=False, sep=';', encoding='utf-8')

    print("4. Sincronizando datos con la nube mediante Git...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Conservando columna A y aplicando soporte dual EAN'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("\n¡[ÉXITO] TIENDA.csv actualizado correctamente!")
    except Exception as e:
        print(f"\n[ERROR] Fallo en la sincronización con Git: {e}")

if __name__ == '__main__':
    procesar_inventario()