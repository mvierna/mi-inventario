import pyautogui
import time
import os
import subprocess
import sys

# Rutas principales del proyecto
DIRECTORIO_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_ASSETS = os.path.join(DIRECTORIO_BASE, 'assets')
RUTA_LOCAL_DESTINO = r'C:\Users\Usuario\mi-inventario'

def clic_visual(nombre_imagen, tiempo_espera=2.0, precision=0.8, clics=1, timeout=10):
    """
    Localiza una imagen de referencia dentro de 'assets/' y pulsa en su centro.
    Retorna True si tuvo éxito o False si se agotó el tiempo de búsqueda.
    """
    ruta_imagen = os.path.join(CARPETA_ASSETS, nombre_imagen)
    print(f"Buscando en pantalla: {nombre_imagen}...")
    tiempo_inicio = time.time()
    
    while time.time() - tiempo_inicio < timeout:
        try:
            coordenadas = pyautogui.locateCenterOnScreen(ruta_imagen, confidence=precision)
            if coordenadas is not None:
                pyautogui.click(coordenadas, clicks=clics)
                time.sleep(tiempo_espera)
                return True
        except Exception as e:
            if "read" in str(e).lower() or "missing" in str(e).lower():
                print(f"-> Error: Falta la imagen '{nombre_imagen}' en {CARPETA_ASSETS}")
                return False
            pass
        time.sleep(0.5)
        
    print(f"-> Tiempo agotado: No se localizó '{nombre_imagen}'.")
    return False

def limpiar_archivos_locales():
    """Elimina copias viejas de ambos CSV antes de comenzar para garantizar datos frescos."""
    for archivo in ['TIENDA.csv', 'SIN_STOCK.csv']:
        ruta = os.path.join(DIRECTORIO_BASE, archivo)
        if os.path.exists(ruta):
            try:
                os.remove(ruta)
                print(f"Archivo previo eliminado: {archivo}")
            except Exception as e:
                print(f"Aviso al limpiar {archivo}: {e}")

def exportar_tienda():
    """Ejecuta la primera exportación correspondiente a TIENDA.csv."""
    print("\n--- [PASO 1] Exportando TIENDA.csv ---")
    if not clic_visual('boton_stocks.png', tiempo_espera=2): return False
    if not clic_visual('ANALISIS.png', tiempo_espera=1): return False
    if not clic_visual('FILTRO.png', tiempo_espera=2): return False

    # Navegación por teclado dentro de los filtros rápidos
    pyautogui.press('tab', presses=2, interval=0.3)
    pyautogui.press('enter')
    time.sleep(0.5)
    
    pyautogui.press('tab')
    pyautogui.press('enter')
    time.sleep(0.5)
    
    pyautogui.press('left', presses=2, interval=0.3)
    pyautogui.press('enter')
    
    print("Esperando cálculo del informe de tienda (22 s)...")
    time.sleep(22)
    
    # Menú contextual para exportar
    pyautogui.hotkey('shift', 'f10')
    time.sleep(1.5)
    pyautogui.press('down', presses=7, interval=0.3)
    pyautogui.press('enter')
    time.sleep(2) 
    
    pyautogui.press('down', presses=3, interval=0.3)
    pyautogui.press('tab', presses=4, interval=0.3)
    pyautogui.press('enter')
    time.sleep(2)
    
    # Nombre del archivo y carpeta de guardado en el servidor
    pyautogui.write('TIENDA', interval=0.1)
    time.sleep(1)
    clic_visual('DOCUMENTOS.png', tiempo_espera=2)
    
    pyautogui.press('tab', presses=3, interval=0.3)
    pyautogui.press('enter')
    time.sleep(1.5)
    
    # Confirmar sobreescritura si el archivo ya existía
    pyautogui.press('left')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    print("Guardando TIENDA.csv en el servidor...")
    time.sleep(18)
    return True

def exportar_sin_stock():
    """Ejecuta la segunda exportación correspondiente a SIN_STOCK.csv usando FILTRO 2.png."""
    print("\n--- [PASO 2] Exportando SIN_STOCK.csv ---")
    
    # 1. Abrir la opción del árbol en Ábaco
    if not clic_visual('info_detallada.png', tiempo_espera=2): return False
    
    # 2. Confirmar diálogo inicial: '¿Desea definir los criterios ahora?' -> Sí
    pyautogui.press('enter')
    time.sleep(2)
    
    # 3. Cargar plantilla usando el botón FILTRO 2 proporcionado
    print("Pulsando botón de plantilla con FILTRO 2.png...")
    if not clic_visual('FILTRO 2.png', tiempo_espera=2): return False
    
    # Aceptar la plantilla seleccionada por defecto (001 - STOCK EVENTA 1)
    pyautogui.press('enter')
    time.sleep(2)
    
    # 4. Validar ventana de criterios de filtro (botón OK abajo a la derecha)
    # Pulsamos Tab 3 veces para posicionar el foco sobre el botón OK y pulsamos Enter
    pyautogui.press('tab', presses=3, interval=0.25)
    pyautogui.press('enter')
    time.sleep(1.5)
    
    # 5. Confirmar advertencia: '¿Aplicar el filtro a todos los artículos?' -> Sí (Enter)
    pyautogui.press('enter')
    
    # 6. Extracción de los ~38.000 artículos en Ábaco
    print("Extrayendo datos de sin stock (esperando 60 segundos a que termine el servidor)...")
    time.sleep(60)
    
    # 7. Menú contextual en la tabla resultante (Shift + F10)
    pyautogui.hotkey('shift', 'f10')
    time.sleep(1.5)
    
    # En este informe la opción 'Exporter en CSV' está a 9 pulsaciones hacia abajo
    pyautogui.press('down', presses=9, interval=0.25)
    pyautogui.press('enter')
    time.sleep(2.5)
    
    # 8. Guardar archivo con el nombre SIN_STOCK
    pyautogui.write('SIN_STOCK', interval=0.1)
    time.sleep(1)
    clic_visual('DOCUMENTOS.png', tiempo_espera=2)
    
    pyautogui.press('tab', presses=3, interval=0.3)
    pyautogui.press('enter')
    time.sleep(1.5)
    
    # Confirmar sobreescritura si ya existe
    pyautogui.press('left')
    time.sleep(0.5)
    pyautogui.press('enter')
    
    print("Guardando SIN_STOCK.csv en el servidor...")
    time.sleep(15)
    return True

def transferir_archivos_a_local():
    """Abre la carpeta Documents en el servidor, corta ambos CSV y los pega en el PC local."""
    print("\n--- [PASO 3] Moviendo ambos archivos al equipo local ---")
    
    # Abrir Documents en el servidor remoto
    clic_visual('DEMARRER.png', tiempo_espera=1.5)
    clic_visual('ORDENADOR.png', tiempo_espera=1.5)
    clic_visual('DOCUMENTOS.png', tiempo_espera=2)
    
    # Seleccionar ambos archivos CSV con clics visuales manteniendo la tecla Ctrl
    clic_visual('TIENDA.png', tiempo_espera=1)
    pyautogui.keyDown('ctrl')
    clic_visual('SIN_STOCK.png', tiempo_espera=1)
    pyautogui.keyUp('ctrl')
    time.sleep(0.5)
    
    # Cortar archivos del servidor
    pyautogui.hotkey('ctrl', 'x')
    time.sleep(1.5)
    
    # Abrir explorador de Windows en la máquina local
    pyautogui.hotkey('win', 'e')
    time.sleep(1.5)
    pyautogui.hotkey('alt', 'd')
    time.sleep(0.5)
    pyautogui.write(RUTA_LOCAL_DESTINO, interval=0.05)
    pyautogui.press('enter')
    time.sleep(2.5)
    
    # Pegar archivos transferidos
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.5)
    
    # Si Windows muestra el cuadro de 'Reemplazar los archivos en el destino', pulsar Enter
    pyautogui.press('enter')
    time.sleep(2)
    
    # Cerrar ventana local
    pyautogui.hotkey('alt', 'f4')
    time.sleep(1)

def ejecutar_robot():
    pyautogui.FAILSAFE = True
    limpiar_archivos_locales()
    
    print("\n================ INICIANDO ROBOT DOBLE ================")
    try:
        # Apertura de mRemoteNG y sesión de Ábaco
        if not clic_visual('carpeta_inicio.png', tiempo_espera=2): return
        if not clic_visual('icono_miguel.png', tiempo_espera=2, clics=2): return
        
        # Extracción secuencial de los dos informes
        if not exportar_tienda():
            print("Detención: Falló la exportación de TIENDA.")
            return
            
        if not exportar_sin_stock():
            print("Detención: Falló la exportación de SIN_STOCK.")
            return
            
        # Transferencia conjunta
        transferir_archivos_a_local()
        
        # Ejecución del actualizador y subida a GitHub
        print("\nEjecutando actualizador.py...")
        subprocess.run([sys.executable, "actualizador.py"], cwd=DIRECTORIO_BASE)
        
        # Cierre ordenado de sesión y proceso
        print("\nCerrando sesión en Windows Server...")
        clic_visual('DEMARRER.png', tiempo_espera=1)
        clic_visual('cerrar_sesion.png', tiempo_espera=3)
        subprocess.run(["taskkill", "/f", "/im", "mRemoteNG.exe"], creationflags=subprocess.CREATE_NO_WINDOW)
        
        print("\n¡Automatización completada exitosamente!")
        
    except pyautogui.FailSafeException:
        print("\n[EMERGENCIA] Ejecución abortada por el usuario (ratón en la esquina superior izquierda).")
    except Exception as error:
        print(f"\n[ERROR] Ocurrió una anomalía durante la ejecución: {error}")

if __name__ == '__main__':
    ejecutar_robot()