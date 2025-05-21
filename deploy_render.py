#!/usr/bin/env python
"""
Script para preparar el despliegue en Render.com
"""
import os
import sys
import subprocess
import time

def run_command(command, check=True):
    """Ejecuta un comando y muestra el output en tiempo real"""
    print(f"\n\033[1;34m$ {command}\033[0m")
    process = subprocess.run(command, shell=True, check=check)
    return process.returncode == 0

def check_git():
    """Verifica si Git está instalado"""
    if not run_command("git --version", check=False):
        print("\033[1;31mError: Git no está instalado.\033[0m")
        print("Instálalo desde: https://git-scm.com/downloads")
        return False
    return True

def initialize_git():
    """Inicializa Git si es necesario"""
    print("\n\033[1;32m[1/3] Preparando el repositorio Git...\033[0m")
    
    # Verificar si ya existe un repositorio Git
    if not os.path.exists('.git'):
        print("Inicializando repositorio Git...")
        run_command("git init")
    
    # Preparar commit
    run_command("git add .")
    run_command("git commit -m \"Preparación para despliegue en Render\"")

def create_render_yaml():
    """Crea el archivo render.yaml para despliegue"""
    print("\n\033[1;32m[2/3] Creando archivo de configuración para Render...\033[0m")
    
    with open("render.yaml", "w") as f:
        f.write("""
services:
  - type: web
    name: biblioteca-django
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn biblioteca.wsgi:application
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: biblioteca-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: PYTHON_VERSION
        value: 3.11.8
    autoDeploy: true

databases:
  - name: biblioteca-db
    databaseName: biblioteca
    ipAllowList: []
""")
    
    print("\033[1;32mArchivo render.yaml creado correctamente.\033[0m")

def collect_static():
    """Recolecta los archivos estáticos"""
    print("\n\033[1;32m[3/3] Recolectando archivos estáticos...\033[0m")
    run_command("python manage.py collectstatic --noinput")

def main():
    """Función principal del script"""
    print("\033[1;32m===== PREPARACIÓN PARA DESPLIEGUE EN RENDER.COM =====\033[0m")
    
    if not check_git():
        sys.exit(1)
    
    initialize_git()
    create_render_yaml()
    collect_static()
    
    print(f"\n\033[1;32m¡PREPARACIÓN COMPLETADA!\033[0m")
    print(f"Para desplegar tu aplicación en Render.com:")
    print(f"1. Crea una cuenta en https://render.com/")
    print(f"2. Sube tu código a GitHub o GitLab")
    print(f"3. En el dashboard de Render, selecciona 'New' y luego 'Blueprint'")
    print(f"4. Conecta tu repositorio y Render detectará automáticamente el archivo render.yaml")
    print(f"5. Haz clic en 'Apply Blueprint'")
    print(f"\nRender desplegará tu aplicación automáticamente.")

if __name__ == "__main__":
    main() 