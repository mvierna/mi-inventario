import pandas as pd
import subprocess
import os

def procesar_tienda():
    print("-> Procesando TIENDA.csv (Stock Diario)...")
    try:
        # Leer forzando string para proteger EAN de la notación científica
        df_tienda = pd.read_csv('TIENDA.csv', sep=';', dtype=str, header=None)
        df_tienda = df_tienda.fillna("")
        
        # Limpieza básica del EAN (columna 0)
        df_tienda[0] = df_tienda[0].str.strip().str.replace(r'\.0$', '', regex=True)
        
        # Guardar archivo limpio
        df_tienda.to_csv('TIENDA.csv', sep=';', index=False, header=False, encoding='utf-8-sig')
        print(f"   TIENDA.csv procesado con {len(df_tienda)} líneas.")
        
        # Retornar los EANs únicos para usarlos como filtro en el archivo maestro
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
        # Leer maestro forzando texto puro
        df_maestro = pd.read_csv(archivo_maestro, sep=';', dtype=str, encoding='utf-8')
        
        # Limpiar EANs y eliminar duplicados manteniendo el primero
        df_maestro['Code EAN'] = df_maestro['Code EAN'].str.strip().str.replace(r'\.0$', '', regex=True)
        df_maestro = df_maestro.drop_duplicates(subset=['Code EAN'], keep='first')
        
        # Filtrar: Quedarse con los que NO están en TIENDA.csv
        df_faltantes = df_maestro[~df_maestro['Code EAN'].isin(eans_en_tienda)]
        
        # Extraer solo las 4 columnas críticas para aligerar la PWA
        columnas_clave = ['Code EAN', 'Designación', 'PV', 'Date dernier mouvement']
        
        # Verificar que las columnas existan en el CSV de Abaco antes de extraerlas
        columnas_presentes = [col for col in columnas_clave if col in df_maestro.columns]
        df_final = df_faltantes[columnas_presentes].copy()
        
        # Renombrar para que el index.html lo lea fácilmente
        df_final.columns = ['EAN', 'DESCRIPCION', 'PVP_MAESTRO', 'ULTIMA_VENTA'][:len(columnas_presentes)]
        df_final = df_final.fillna("")
        
        # Exportar maestro filtrado
        df_final.to_csv('MAESTRO_FILTRADO.csv', sep=';', index=False, encoding='utf-8-sig')
        print(f"   MAESTRO_FILTRADO.csv generado con éxito ({len(df_final)} referencias).")

    except Exception as e:
        print(f"❌ Error procesando el archivo maestro: {e}")

def sincronizar_github():
    print("-> Sincronizando TODOS los datos y código con GitHub...")
    comandos = [
        # El punto indica que suba absolutamente todo lo que haya cambiado en la carpeta
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
            # Ignorar error si no hay cambios para hacer commit
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