import pyautogui
import time
import subprocess
import os

def clic_visual(nombre_imagen, tiempo_espera=2, precision=0.85):
    """
    Busca una imagen en pantalla y hace clic en su centro.
    """
    print(f"Buscando en pantalla: {nombre_imagen}...")
    try:
        coordenadas = pyautogui.locateCenterOnScreen(nombre_imagen, confidence=precision)
        if coordenadas is not None:
            pyautogui.click(coordenadas)
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

    if os.path.exists('TIENDA.csv'):
        try:
            os.remove('TIENDA.csv')
            print("Archivo 'TIENDA.csv' antiguo eliminado.")
        except Exception:
            pass

    print("\n[INICIO] Tienes 5 segundos para maximizar Abaco...")
    time.sleep(5)

    try:
        if not clic_visual('boton_stocks.png', tiempo_espera=3): return
        if not clic_visual('ANALISIS.png', tiempo_espera=3): return
        if not clic_visual('FILTRO.png', tiempo_espera=2): return
        if not clic_visual('FILTRO 2.png', tiempo_espera=2): return

        # --- SECCIÓN CRÍTICA: VENTANA DEL MODELO 100 ---
        print("Escribiendo el modelo '100'...")
        pyautogui.write('100', interval=0.2)
        time.sleep(1)
        
        print("Pulsando ENTER para cerrar la ventanita del modelo...")
        pyautogui.press('enter')
        
        # Pausa larga: damos tiempo a que la ventana emergente desaparezca por completo
        time.sleep(3) 

        print("Pulsando ENTER para aplicar el filtro general...")
        pyautogui.press('enter')
        
        # Pausa extra larga para asegurar que carga la nueva vista
        time.sleep(4) 
        # -----------------------------------------------

        # Recuperar el foco: Hacemos un clic inofensivo en el centro superior de la pantalla
        # Esto asegura que las siguientes teclas vayan al programa correcto
        print("Asegurando el foco de la ventana de Abaco...")
        ancho, alto = pyautogui.size()
        pyautogui.click(ancho / 2, alto / 10) 
        time.sleep(1)

        print("Enviando atajo para Buscar (Alt + B)...")
        pyautogui.hotkey('alt', 'b')
        time.sleep(2)
        
        print("Pulsando ENTER para confirmar la búsqueda...")
        pyautogui.press('enter')
        
        # Esperamos 10 segundos para que Abaco cargue la lista masiva de artículos
        time.sleep(10)

        # Si aparece el aviso de los 42.000 artículos, intentamos cerrarlo
        if not clic_visual('boton_oui.png', tiempo_espera=5, precision=0.8):
            print("No se vio el botón OUI visualmente, intentando confirmación por teclado...")
            pyautogui.press('left')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(5)

        # --- EXPORTACIÓN (A la espera de tus pasos exactos) ---
        print("Abriendo menú contextual para exportar...")
        pyautogui.click(ancho / 2, alto / 2, button='right')
        time.sleep(2)

        # Aquí es donde pondremos tus tabulaciones y pulsaciones exactas cuando me las dictes
        print("Navegando por el menú de exportación (bajando 4 posiciones)...")
        pyautogui.press('down', presses=4, interval=0.5)
        pyautogui.press('enter')
        time.sleep(3)

        print("Configurando el guardado (Tabulaciones a ciegas)...")
        pyautogui.press('tab', presses=2, interval=0.5)
        pyautogui.press('enter')
        time.sleep(2)
        pyautogui.press('tab', presses=3, interval=0.5)
        pyautogui.press('enter')
        time.sleep(4)

        pyautogui.write('TIENDA.csv', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(10)

        print("\n¡Proceso de Abaco finalizado!")
        subprocess.run(['python', 'actualizador.py'], check=True)

    except pyautogui.FailSafeException:
        print("\n[ALERTA] Robot detenido de emergencia por el usuario.")
    except Exception as e:
        print(f"\n[ERROR] Problema inesperado: {e}")

if __name__ == '__main__':
    ejecutar_robot()
    input("\nPresiona ENTER para salir...")