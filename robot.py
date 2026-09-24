import pyautogui
import time
import subprocess
import os

# --- MÓDULO DE RECONOCIMIENTO VISUAL ---
def clic_visual(nombre_imagen, tiempo_espera=2, precision=0.85):
    """
    Busca una imagen en pantalla y hace clic en su centro si la encuentra.
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

# --- MÓDULO PRINCIPAL ---
def ejecutar_robot():
    # Seguro de pánico: Mueve el ratón a una esquina para detener el código
    pyautogui.FAILSAFE = True

    # Limpieza previa del archivo antiguo para evitar conflictos
    if os.path.exists('TIENDA.csv'):
        try:
            os.remove('TIENDA.csv')
            print("Archivo 'TIENDA.csv' antiguo eliminado.")
        except Exception as e:
            print(f"No se pudo eliminar el archivo anterior: {e}")

    print("\n[INICIO] Tienes 5 segundos para hacer clic en Abaco y dejar la ventana activa.")
    time.sleep(5)

    try:
        # PASO 1: Entrar a Gestión de Stocks
        if not clic_visual('boton_stocks.png', tiempo_espera=3):
            print("Detenido en Paso 1: 'boton_stocks.png'")
            return

        # PASO 2: Entrar a Análisis de artículos
        if not clic_visual('ANALISIS.png', tiempo_espera=3):
            print("Detenido en Paso 2: 'ANALISIS.png'")
            return

        # PASO 3: Abrir menú Filtro de
        if not clic_visual('FILTRO.png', tiempo_espera=2):
            print("Detenido en Paso 3: 'FILTRO.png'")
            return

        # PASO 4: Abrir la lista de modelos
        if not clic_visual('FILTRO 2.png', tiempo_espera=2):
            print("Detenido en Paso 4: 'FILTRO 2.png'")
            return

        # PASO 5: Inyección por teclado del modelo '100' y doble Enter
        print("Escribiendo el modelo '100' y confirmando con teclado...")
        pyautogui.write('100', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')  # Cierra la ventana emergente del modelo
        time.sleep(1.5)
        pyautogui.press('enter')  # Cierra la ventana general de filtros y aplica
        time.sleep(3)

        # PASO 6: Lanzar la búsqueda (Combinación directa para evitar error en boton_buscar.png)
        print("Ejecutando la búsqueda mediante combinación de teclas...")
        pyautogui.hotkey('alt', 'b') # Intenta el atajo clásico de 'Buscar'
        time.sleep(0.5)
        pyautogui.press('enter')    # Refuerzo con Enter
        time.sleep(10)              # Tiempo de carga de la lista

        # PASO 7: Aceptar aviso de volumen de artículos si aparece
        print("Confirmando la ventana de artículos (Oui / Sí)...")
        if not clic_visual('boton_oui.png', tiempo_espera=15, precision=0.8):
            # Si no lo encuentra por imagen, envía flecha izquierda + Enter por teclado
            pyautogui.press('left')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(12)

        # PASO 8: Clic derecho en el centro de la tabla para exportar
        print("Abriendo menú contextual de la lista...")
        ancho, alto = pyautogui.size()
        pyautogui.click(ancho / 2, alto / 2, button='right')
        time.sleep(1.5)

        # Navegar hasta la opción 'Exporter'
        pyautogui.press('down', presses=4, interval=0.3)
        pyautogui.press('enter')
        time.sleep(3)

        # PASO 9: Guardar archivo CSV
        print("Configurando el guardado del archivo 'TIENDA.csv'...")
        pyautogui.press('tab', presses=2, interval=0.5)
        pyautogui.press('enter')
        time.sleep(1.5)
        pyautogui.press('tab', presses=3, interval=0.5)
        pyautogui.press('enter')
        time.sleep(3)

        pyautogui.write('TIENDA.csv', interval=0.1)
        time.sleep(1)
        pyautogui.press('enter')

        print("Esperando 10 segundos a que se genere el archivo en disco...")
        time.sleep(10)

        # PASO 10: Subida automática a la nube
        print("\n¡Extracción finalizada con éxito!")
        print("Iniciando la sincronización con GitHub mediante actualizador.py...")
        subprocess.run(['python', 'actualizador.py'], check=True)

    except pyautogui.FailSafeException:
        print("\n[ALERTA] El robot se detuvo porque el ratón tocó una esquina de la pantalla.")
    except Exception as e:
        print(f"\n[ERROR] Ocurrió un problema inesperado: {e}")

if __name__ == '__main__':
    ejecutar_robot()
    input("\nPresiona ENTER para salir...")