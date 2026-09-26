import pyautogui
import time
import os

def clic_visual(nombre_imagen, tiempo_espera=2, precision=0.8, clics=1, timeout=10):
    """
    Busca una imagen en pantalla y hace clic en su centro.
    Soporta múltiples clics y tiene un bucle que espera hasta 10 segundos 
    a que la imagen aparezca en pantalla.
    """
    print(f"Buscando en pantalla: {nombre_imagen}...")
    tiempo_inicio = time.time()
    
    while time.time() - tiempo_inicio < timeout:
        try:
            coordenadas = pyautogui.locateCenterOnScreen(nombre_imagen, confidence=precision)
            if coordenadas is not None:
                pyautogui.click(coordenadas, clicks=clics)
                time.sleep(tiempo_espera)
                return True
        except Exception as e:
            if "read" in str(e).lower() or "missing" in str(e).lower():
                print(f"-> Error técnico: Falta el archivo de imagen '{nombre_imagen}'.")
                return False
            pass 
            
        time.sleep(0.5) 
        
    print(f"-> Se agotó el tiempo. No se encontró la imagen '{nombre_imagen}'.")
    return False

def ejecutar_robot():
    pyautogui.FAILSAFE = True

    # 1. Limpieza de archivo antiguo en la carpeta de destino
    if os.path.exists('TIENDA.csv'):
        try:
            os.remove('TIENDA.csv')
            print("Archivo 'TIENDA.csv' antiguo eliminado de la carpeta local.")
        except Exception:
            pass

    print("\n[INICIO] Iniciando automatización completa...")

    try:
        # ---------------------------------------------------------
        # 2. APERTURA DEL PROGRAMA ABACO DESDE EL ESCRITORIO
        # ---------------------------------------------------------
        print("Abriendo aplicación desde la barra de tareas...")
        if not clic_visual('carpeta_inicio.png', tiempo_espera=2): return

        print("Haciendo doble clic en Miguel para abrir Abaco...")
        if not clic_visual('icono_miguel.png', tiempo_espera=15, clics=2): return


        # ---------------------------------------------------------
        # 3. NAVEGACIÓN INICIAL POR LOS MENÚS
        # ---------------------------------------------------------
        if not clic_visual('boton_stocks.png', tiempo_espera=3): return
        if not clic_visual('ANALISIS.png', tiempo_espera=3): return
        if not clic_visual('FILTRO.png', tiempo_espera=2): return
        if not clic_visual('FILTRO 2.png', tiempo_espera=2): return

        # 4. Introducción del modelo
        print("Escribiendo el modelo '101'...")
        pyautogui.write('101', interval=0.2)
        time.sleep(0.5)

        print("Confirmando el modelo (doble Enter)...")
        pyautogui.press('enter', presses=2, interval=0.5)
        time.sleep(1.5) 

        # ---------------------------------------------------------
        # 5. SECUENCIA DE EXPORTACIÓN EN ABACO
        # ---------------------------------------------------------
        print("Navegando por filtros de Abaco...")
        pyautogui.press('tab', presses=7, interval=0.3)
        pyautogui.press('enter')
        time.sleep(8) 
        
        pyautogui.press('enter')
        time.sleep(3)
        
        pyautogui.press('left', presses=2, interval=0.3)
        pyautogui.press('enter')
        time.sleep(14) 
        
        print("Abriendo menú contextual (Shift + F10)...")
        pyautogui.hotkey('shift', 'f10')
        time.sleep(1.5)
        
        print("Seleccionando Exportar (7 flechas abajo y Enter)...")
        pyautogui.press('down', presses=7, interval=0.3)
        pyautogui.press('enter')
        time.sleep(2) 
        
        print("Configurando formato de exportación (3 abajo, 4 tab, Enter)...")
        pyautogui.press('down', presses=3, interval=0.3)
        pyautogui.press('tab', presses=4, interval=0.3)
        pyautogui.press('enter')
        time.sleep(2)
        
        # ---------------------------------------------------------
        # 6. RUTA DE GUARDADO VISUAL EN ABACO
        # ---------------------------------------------------------
        print("Escribiendo nombre del archivo en MAYÚSCULAS...")
        pyautogui.write('TIENDA', interval=0.1)
        time.sleep(1)

        print("Pulsando botón Documentos...")
        clic_visual('DOCUMENTOS.png', tiempo_espera=2)
        
        print("Tabulando 3 veces y pulsando Enter...")
        pyautogui.press('tab', presses=3, interval=0.3)
        pyautogui.press('enter')
        time.sleep(1.5)
        
        print("Confirmando sobreescritura (Izquierda + Enter)...")
        pyautogui.press('left')
        time.sleep(0.5)
        pyautogui.press('enter')
        
        print("Esperando a que el archivo se guarde físicamente...")
        time.sleep(8)
        
        # ---------------------------------------------------------
        # 7. EXTRACCIÓN VISUAL EN WINDOWS
        # ---------------------------------------------------------
        print("Pulsando Démarrer...")
        clic_visual('DEMARRER.png', tiempo_espera=2)
        
        print("Pulsando Ordinateur...")
        clic_visual('ORDENADOR.png', tiempo_espera=2)
        
        print("Pulsando Documentos por segunda vez...")
        clic_visual('DOCUMENTOS.png', tiempo_espera=2)
        
        print("Tocar botón TIENDA para seleccionar...")
        clic_visual('TIENDA.png', tiempo_espera=1)
            
        print("Cortando archivo...")
        pyautogui.hotkey('ctrl', 'x')
        time.sleep(1.5)
        
        print("Pulsando botón Windows...")
        pyautogui.press('win') 
        time.sleep(1.5)
        
        print("Escribiendo ruta de destino...")
        pyautogui.write(r'C:\Users\Usuario\mi-inventario', interval=0.05)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(3) 
        
        print("Pegando archivo...")
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(2)

        # ---------------------------------------------------------
        # 8. SINCRONIZACIÓN FINAL VISUAL
        # ---------------------------------------------------------
        print("\n¡Proceso de Abaco finalizado con éxito!")
        print("Ejecutando actualizador.py visualmente...")
        if not clic_visual('actualizador.png', tiempo_espera=5, clics=2): return
        
        print("¡Sincronización lanzada correctamente!")

    except pyautogui.FailSafeException:
        print("\n[ALERTA] Robot detenido de emergencia por el usuario (ratón en la esquina superior izquierda).")
    except Exception as e:
        print(f"\n[ERROR] Problema inesperado: {e}")

if __name__ == '__main__':
    ejecutar_robot()
    input("\nPresiona ENTER para salir...")