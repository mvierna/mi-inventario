import pandas as pd
import subprocess
import os

def formatear_precio_abaco(precio_str):
    """
    Convierte el formato raro de Abaco (ej: '16.900') a euros reales (ej: '1,69')
    """
    if pd.isna(precio_str) or str(precio_str).strip() == "":
        return "-"
    
    # 1. Eliminamos los puntos que Abaco usa como separador
    precio_limpio = str(precio_str).replace(".", "").strip()
    
    try:
        # 2. Dividimos entre 10.000 (Ej: "16900" -> 1.69)
        precio_num = float(precio_limpio) / 10000
        # 3. Lo devolvemos formateado con 2 decimales y coma española
        return f"{precio_num:.2f}".replace(".", ",")
    except ValueError:
        return str(precio_str)

def procesar_tienda():
    print("-> Procesando TIENDA.csv (Stock Diario)...")
    try:
        df_tienda = pd.read_csv('TIENDA.csv', sep=';', dtype=str, header=None)
        df_tienda = df_tienda.fillna("")
        
        # Limpieza básica del EAN (columna 0)
        df_tienda[0] = df_tienda[0].str.strip().str.replace(r'\.0$', '', regex=True)
        
        df_tienda.to_csv('TIENDA.csv', sep=';', index=False, header=False, encoding='utf-8-sig')
        print(f"   TIENDA.csv procesado con {len(df_tienda)} líneas.")
        
        return df_tienda[0].unique()
    
    except Exception as e:
        print(f"❌ Error procesando TIENDA.csv: {e}")
        return []

def procesar_maestro(eans_en_tienda):
    print("-> Procesando stock cero.csv (Base Maestra)...")
    archivo_maestro = 'stock cero.csv'
    
    if not os.path.exists(archivo_maestro):
        print(f"   ⚠️ Archivo '{archivo_maestro}' no encontrado. Se saltará este paso.")
        return

    try:
        df_maestro = pd.read_csv(archivo_maestro, sep=';', dtype=str, encoding='utf-8')
        
        # Limpiar EANs y eliminar duplicados
        df_maestro['Code EAN'] = df_maestro['Code EAN'].str.strip().str.replace(r'\.0$', '', regex=True)
        df_maestro = df_maestro.drop_duplicates(subset=['Code EAN'], keep='first')
        
        # Filtrar los que no están en tienda
        df_faltantes = df_maestro[~df_maestro['Code EAN'].isin(eans_en_tienda)]
        
        columnas_clave = ['Code EAN', 'Designación', 'PV', 'Date dernier mouvement']
        columnas_presentes = [col for col in columnas_clave if col in df_maestro.columns]
        df_final = df_faltantes[columnas_presentes].copy()
        
        # APLICAR LA CORRECCIÓN DE PRECIO AL MAESTRO
        if 'PV' in df_final.columns:
            df_final['PV'] = df_final['PV'].apply(formatear_precio_abaco)
        
        df_final.columns = ['EAN', 'DESCRIPCION', 'PVP_MAESTRO', 'ULTIMA_VENTA'][:len(columnas_presentes)]
        df_final = df_final.fillna("")
        
        df_final.to_csv('MAESTRO_FILTRADO.csv', sep=';', index=False, encoding='utf-8-sig')
        print(f"   MAESTRO_FILTRADO.csv generado con éxito ({len(df_final)} referencias).")

    except Exception as e:
        print(f"❌ Error procesando el archivo maestro: {e}")

def sincronizar_github():
    print("-> Sincronizando TODOS los datos y código con GitHub...")
    comandos = [
        ["git", "add", "."], 
        ["git", "commit", "-m", "Actualización automática de inventario, maestro y código"],
        ["git", "pull", "--rebase"],
        ["git", "push"]
    ]
    
    for cmd in comandos:
        try:
            print(f"   Ejecutando: {' '.join(cmd)}")
            resultado = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if resultado.stdout:
                print(f"   {resultado.stdout.strip()}")
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in e.stdout or "no changes added" in e.stdout:
                print("   No hay cambios nuevos para subir. El repositorio está actualizado.")
                break
            else:
                print(f"   ⚠️ Error ejecutando '{' '.join(cmd)}':\n{e.stderr.strip()}")

if __name__ == "__main__":
    print("="*50)
    print(" INICIANDO SECUENCIA DE ACTUALIZACIÓN COMPLETA")
    print("="*50)
    
    eans_actuales = procesar_tienda()
    
    if len(eans_actuales) > 0:
        procesar_maestro(eans_actuales)
    
    sincronizar_github()
    
    print("="*50)
    print(" ACTUALIZACIÓN FINALIZADA")
    print("="*50)