import pandas as pd
import os
import subprocess

def procesar_fichero_tienda():
    archivo_origen = 'TIENDA.csv'
    
    if not os.path.exists(archivo_origen):
        print(f"[ERROR] No se encuentra el archivo {archivo_origen}")
        return

    print("1. Leyendo datos de TIENDA.csv...")
    # Leemos el CSV asignando nombres de columnas temporales o respetando los existentes
    # header=None asegura que no interprete la primera fila como encabezado si no lo tiene
    df = pd.read_csv(archivo_origen, sep=';', dtype=str, encoding='latin1', header=None)

    # Si por error hay más de 3 columnas, nos quedamos solo con las 3 primeras (EAN, Nombre, Stock)
    df = df.iloc[:, :3]
    df.columns = ['EAN', 'DESCRIPCION', 'STOCK']

    print("2. Limpiando códigos de barras y eliminando decimales...")
    # Convertimos a texto y quitamos espacios
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()

    print("3. Generando ceros a la izquierda (13 dígitos)...")
    # Creamos una copia de los registros que tienen menos de 13 dígitos
    df_13 = df.copy()
    # zfill(13) convierte '606707508872' -> '0606707508872'
    df_13['EAN'] = df_13['EAN'].str.zfill(13)

    # Creamos también la versión de 12 dígitos (sin el cero inicial)
    df_12 = df_13.copy()
    df_12['EAN'] = df_12['EAN'].apply(lambda x: x[1:] if len(x) == 13 and x.startswith('0') else x)

    # Combinamos ambas listas para que funcionen tanto con 12 como con 13 dígitos
    df_final = pd.concat([df_13, df_12], ignore_index=True)
    
    # Eliminamos duplicados exactos
    df_final = df_final.drop_duplicates(subset=['EAN'])

    print(f"Total de referencias listas: {len(df_final)}")

    print("4. Guardando 'TIENDA.csv' formateado de forma limpia...")
    # Guardamos sin índice (index=False) y sin encabezados (header=False) para mantener la compatibilidad original
    df_final.to_csv('TIENDA.csv', index=False, header=False, sep=';', encoding='utf-8')

    print("5. Sincronizando con GitHub...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Formato de archivo TIENDA reestructurado'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("\n¡[ÉXITO] Base de datos corregida y subida a la nube!")
    except Exception as e:
        print(f"\n[ERROR] Error durante la subida Git: {e}")

if __name__ == '__main__':
    procesar_fichero_tienda()