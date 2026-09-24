from pynput import mouse, keyboard
import time

print("--- MODO GRABADORA TOTAL ---")
print("Registrando clics, teclas y tiempos de espera...")
print("Realiza el proceso en tu programa de forma natural.")
print("Presiona la tecla ESC para detener la grabación y salir.\n")

# Cronómetro para calcular los tiempos de espera
ultimo_tiempo = time.time()
contador_pasos = 1

def registrar_tiempo_espera():
    global ultimo_tiempo
    tiempo_actual = time.time()
    espera = tiempo_actual - ultimo_tiempo
    ultimo_tiempo = tiempo_actual
    return round(espera, 2) # Redondeamos a 2 decimales para que sea fácil de leer

def al_hacer_clic(x, y, boton, presionado):
    global contador_pasos
    if presionado and boton == mouse.Button.left:
        espera = registrar_tiempo_espera()
        print(f"Paso {contador_pasos}: Esperar {espera} seg -> Clic Izquierdo en X: {int(x)}, Y: {int(y)}")
        contador_pasos += 1

def al_presionar_tecla(tecla):
    global contador_pasos
    
    # Si presionamos ESC, detenemos la grabadora inmediatamente
    if tecla == keyboard.Key.esc:
        print("\n[Grabación finalizada por el usuario]")
        # Devolver False detiene los detectores de pynput
        return False 
        
    espera = registrar_tiempo_espera()
    
    try:
        # Detecta teclas normales (letras, números)
        print(f"Paso {contador_pasos}: Esperar {espera} seg -> Presionar tecla: '{tecla.char}'")
    except AttributeError:
        # Detecta teclas especiales (Enter, Shift, Borrar, etc.)
        print(f"Paso {contador_pasos}: Esperar {espera} seg -> Presionar tecla especial: {tecla}")
        
    contador_pasos += 1

# Iniciamos los "escuchadores" de ratón y teclado al mismo tiempo
escuchador_raton = mouse.Listener(on_click=al_hacer_clic)
escuchador_teclado = keyboard.Listener(on_press=al_presionar_tecla)

escuchador_raton.start()
escuchador_teclado.start()

# El script se mantiene en ejecución hasta que pulsemos ESC
escuchador_raton.join()
escuchador_teclado.join()