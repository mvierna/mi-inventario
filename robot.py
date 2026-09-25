import pyautogui
import time
import subprocess
import os

def clic_visual(nombre_imagen, tiempo_espera=2, precision=0.85, clics=1):
    """
    Busca una imagen en pantalla y hace clic en su centro.
    Soporta múltiples clics mediante el parámetro 'clics'.
    """
    print(f"Buscando en pantalla: {nombre_imagen}...")
    try:
        coordenadas = pyautogui.locateCenterOnScreen(nombre_imagen, confidence=precision)
        if coordenadas is not None:
            pyautogui.click(coordenadas, clicks=clics)
            time.sleep(tiempo_espera)
            return True
        else:
            print(f"-> No se encontró la imagen '{nombre_imagen}'.")
            return False
    except Exception as e:
        print(f"-> Error técnico buscando '{nombre_imagen}': {e}")
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

    print("\n[INICIO] Tienes 5 segundos para maximizar Abaco...")
    time.sleep(5)

    try:
        # 2. Navegación inicial por los menús
        if not clic_visual('boton_stocks.png', tiempo_espera=3): return
        if not clic_visual('ANALISIS.png', tiempo_espera=3): return
        if not clic_visual('FILTRO.png', tiempo_espera=2): return
        if not clic_visual('FILTRO 2.png', tiempo_espera=2): return

        # 3. Introducción del modelo (Cambiado a 101)
        print("Escribiendo el modelo '101'...")
        pyautogui.write('101', interval=0.2)
        time.sleep(0.5)

        print("Confirmando el modelo (doble Enter)...")
        pyautogui.press('enter', presses=2, interval=0.5)
        time.sleep(1.5) 

        # ---------------------------------------------------------
        # 4. SECUENCIA DE EXPORTACIÓN EN ABACO
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
        # 5. RUTA DE GUARDADO VISUAL EN ABACO
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
        # 6. EXTRACCIÓN VISUAL EN WINDOWS
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
        # 7. SINCRONIZACIÓN FINAL
        # ---------------------------------------------------------
        print("\n¡Proceso finalizado con éxito!")
        print("Lanzando actualizador.py para sincronizar con GitHub...")
        subprocess.run(['python', 'actualizador.py'], check=True)

    except pyautogui.FailSafeException:
        print("\n[ALERTA] Robot detenido de emergencia por el usuario (ratón en la esquina superior izquierda).")
    except Exception as e:
        print(f"\n[ERROR] Problema inesperado: {e}")

if __name__ == '__main__':
    ejecutar_robot()
    input("\nPresiona ENTER para salir...")