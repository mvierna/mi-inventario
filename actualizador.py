import pandas as pd
import os
import subprocess

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

    print("1. Leyendo TIENDA.csv y eliminando la columna basura...")
    # Leemos TODO como texto estricto para evitar la maldita notación científica (E+12)
    df = pd.read_csv(nombre_archivo, sep=';', dtype=str, encoding='latin1', header=None)

    # Nos "cargamos" la primera columna (la que tiene los False)
    df = df.drop(columns=[0])
    
    # Reasignamos las 3 columnas restantes a los nombres que usamos internamente
    df = df.iloc[:, :3]
    df.columns = ['EAN', 'DESCRIPCION', 'STOCK']

    print("2. Limpiando códigos de barras...")
    df['EAN'] = df['EAN'].fillna('')
    df['EAN'] = df['EAN'].astype(str).str.replace('.0', '', regex=False).str.strip()
    df = df[~df['EAN'].str.lower().isin(['ean', 'code', ''])]

    print("3. Generando soporte dual para escáner (12 y 13 dígitos)...")
    # Versión 13 dígitos
    df_13 = df.copy()
    df_13['EAN'] = df_13['EAN'].str.zfill(13)

    # Versión 12 dígitos
    df_12 = df_13.copy()
    df_12['EAN'] = df_12['EAN'].apply(quitar_cero_inicial)

    # Unimos y limpiamos duplicados
    df_final = pd.concat([df_13, df_12], ignore_index=True)
    df_final = df_final.drop_duplicates(subset=['EAN'])

    print(f"Total de referencias listas para la app: {len(df_final)}")

    print("4. Guardando archivo final con formato original...")
    # Guardamos sin cabeceras y sin índices, exactamente como tu app lo espera
    df_final.to_csv(nombre_archivo, index=False, header=False, sep=';', encoding='utf-8')

    print("5. Subiendo a la nube...")
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Formato original restaurado con soporte 12/13 EAN'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("\n¡[ÉXITO] Base de datos limpia y sincronizada!")
    except Exception as e:
        print(f"\n[ERROR] Fallo en la subida: {e}")

if __name__ == '__main__':
    procesar_inventario()