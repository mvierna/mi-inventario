import pandas as pd
import os
import subprocess

def limpiar_codigo(val):
    """
    Limpia el código de barras convirtiéndolo a texto plano
    y eliminando decimales de Excel/Pandas (.0).
    """
    if pd.isna(val):
        return ""
    return str(val).split('.')[0].strip()

def procesar_inventario_dual():
    archivo_origen = 'TIENDA.csv'
    archivo_destino = 'TIENDA_LIMPIO.csv' # O 'TIENDA.csv' si la app lee directamente el mismo nombre

    if not os.path.exists(archivo_origen):
        print(f"[ERROR] No se encuentra el archivo {archivo_origen}")
        return

    print("1. Cargando datos de TIENDA.csv...")
    # Leemos el archivo asegurando que todo se trate como texto (dtype=str)
    df = pd.read_csv(archivo_origen, sep=';', dtype=str, encoding='latin1')

    # Identificamos la primera columna (donde está el código EAN)
    col_ean = df.columns[0]
    print(f"Columna de códigos identificada: '{col_ean}'")

    # Limpiamos espacios y decimales
    df[col_ean] = df[col_ean].apply(limpiar_codigo)

    print("2. Generando referencias dobles (12 y 13 dígitos)...")
    
    # Buscamos los códigos de 13 dígitos que empiezan por '0'
    filtro_13_ceros = (df[col_ean].str.len() == 13) & (df[col_ean].str.startswith('0'))
    
    # Creamos un duplicado de esos productos
    duplicados_12 = df[filtro_13_ceros].copy()
    
    # A la copia le quitamos el '0' inicial (convertimos 0606707508872 -> 606707508872)
    duplicados_12[col_ean] = duplicados_12[col_ean].str[1:]

    # Unimos la lista original con los duplicados de 12 dígitos
    df_final = pd.concat([df, duplicados_12], ignore_index=True)

    # Eliminamos posibles registros exactamente idénticos
    df_final = df_final.drop_duplicates(subset=[col_ean])

    print(f"Total de productos en la base de datos optimizada: {len(df_final)}")

    # Guardamos el archivo procesado
    df_final.to_csv(archivo_destino, index=False, sep=';', encoding='utf-8')
    print(f"3. Archivo guardado con éxito como '{archivo_destino}'.")

    # 4. Sincronización automática con GitHub
    try:
        print("4. Subiendo actualización a GitHub Pages...")
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', 'Soporte dual de EAN 12 y 13 digitos'], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("\n¡[ÉXITO] Base de datos actualizada en la nube!")
    except Exception as e:
        print(f"\n[ERROR] Falló la sincronización con Git: {e}")

if __name__ == '__main__':
    procesar_inventario_dual()