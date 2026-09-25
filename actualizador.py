import subprocess

def subir_a_github():
    """
    Función para automatizar la sincronización y subida de la base de datos a GitHub.
    Usa 'git pull --rebase' antes del push para evitar conflictos de ramas remotas.
    """
    try:
        print("5. Subiendo datos a GitHub...")
        
        # Paso A: Preparar todos los archivos modificados (como TIENDA.csv)
        subprocess.run(["git", "add", "."], check=True)
        
        # Paso B: Crear el commit local con el mensaje descriptivo
        # 'check=False' evita que el programa falle si no hay cambios nuevos que guardar
        subprocess.run(
            ["git", "commit", "-m", "Blindaje matematico de EAN y soporte dual"], 
            check=False
        )
        
        # Paso C: Traer cambios remotos y reordenar el historial (SOLUCIÓN AL ERROR)
        # Sincroniza lo que hay en GitHub con tu equipo antes de enviar nada
        subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True)
        
        # Paso D: Enviar los datos actualizados a GitHub
        subprocess.run(["git", "push", "origin", "main"], check=True)
        
        print("¡Base de datos actualizada y subida correctamente a GitHub!")
        
    except subprocess.CalledProcessError as error:
        print(f"[ERROR] Fallo en la subida a GitHub: {error}")

# Llamada a la función dentro del flujo principal de tu script
subir_a_github()