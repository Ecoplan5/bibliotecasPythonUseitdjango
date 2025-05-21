#!/usr/bin/env python
"""
Script para facilitar el despliegue en Heroku
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

def check_heroku_cli():
    """Verifica si Heroku CLI está instalado"""
    if not run_command("heroku --version", check=False):
        print("\033[1;31mError: Heroku CLI no está instalado.\033[0m")
        print("Instálalo desde: https://devcenter.heroku.com/articles/heroku-cli")
        return False
    return True

def check_git():
    """Verifica si Git está instalado"""
    if not run_command("git --version", check=False):
        print("\033[1;31mError: Git no está instalado.\033[0m")
        print("Instálalo desde: https://git-scm.com/downloads")
        return False
    return True

def heroku_login():
    """Inicia sesión en Heroku"""
    print("\n\033[1;32m[1/8] Iniciando sesión en Heroku...\033[0m")
    run_command("heroku login")

def create_heroku_app():
    """Crea una nueva aplicación en Heroku"""
    print("\n\033[1;32m[2/8] Creando aplicación en Heroku...\033[0m")
    app_name = input("Nombre para tu aplicación (dejar en blanco para nombre aleatorio): ").strip()
    
    if app_name:
        success = run_command(f"heroku create {app_name}")
    else:
        success = run_command("heroku create")
    
    if not success:
        print("\033[1;33mNota: Si el error es por un nombre ya existente, prueba con otro nombre.\033[0m")
        return create_heroku_app()
    
    # Obtener el nombre de la app creada
    result = subprocess.run("heroku apps:info --json", shell=True, capture_output=True, text=True)
    import json
    try:
        app_info = json.loads(result.stdout)
        return app_info.get('name')
    except:
        # Fallback: extraer del git remote
        result = subprocess.run("git remote get-url heroku", shell=True, capture_output=True, text=True)
        remote_url = result.stdout.strip()
        return remote_url.split('/')[-1].replace('.git', '')

def add_postgres_addon(app_name):
    """Añade el addon de PostgreSQL"""
    print("\n\033[1;32m[3/8] Configurando base de datos PostgreSQL...\033[0m")
    run_command(f"heroku addons:create heroku-postgresql:mini --app {app_name}")

def configure_environment(app_name):
    """Configura variables de entorno en Heroku"""
    print("\n\033[1;32m[4/8] Configurando variables de entorno...\033[0m")
    run_command(f"heroku config:set DEBUG=False --app {app_name}")
    # Generar una clave secreta segura
    import secrets
    secret_key = secrets.token_urlsafe(50)
    run_command(f"heroku config:set SECRET_KEY='{secret_key}' --app {app_name}")

def initialize_git():
    """Inicializa Git si es necesario"""
    print("\n\033[1;32m[5/8] Preparando el repositorio Git...\033[0m")
    
    # Verificar si ya existe un repositorio Git
    if not os.path.exists('.git'):
        print("Inicializando repositorio Git...")
        run_command("git init")
    
    # Añadir heroku como remote si no existe
    result = subprocess.run("git remote -v", shell=True, capture_output=True, text=True)
    if "heroku" not in result.stdout:
        app_name = subprocess.run("heroku apps:info --json | python -c \"import sys, json; print(json.load(sys.stdin).get('name'))\"", 
                                shell=True, capture_output=True, text=True).stdout.strip()
        run_command(f"heroku git:remote -a {app_name}")
    
    # Preparar commit
    run_command("git add .")
    run_command("git commit -m \"Preparación para despliegue en Heroku\"")

def collect_static():
    """Recolecta los archivos estáticos"""
    print("\n\033[1;32m[6/8] Recolectando archivos estáticos...\033[0m")
    run_command("python manage.py collectstatic --noinput")

def push_to_heroku():
    """Envía el código a Heroku"""
    print("\n\033[1;32m[7/8] Desplegando aplicación en Heroku...\033[0m")
    run_command("git push heroku master || git push heroku main")

def apply_migrations(app_name):
    """Aplica las migraciones de la base de datos"""
    print("\n\033[1;32m[8/8] Aplicando migraciones de base de datos...\033[0m")
    run_command(f"heroku run python manage.py migrate --app {app_name}")
    
    print("\n\033[1;32mCreando superusuario para acceder al panel de administración...\033[0m")
    print("Esto te pedirá ingresar un nombre de usuario, correo y contraseña.")
    run_command(f"heroku run python manage.py createsuperuser --app {app_name}")

def main():
    """Función principal del script"""
    print("\033[1;32m===== DESPLIEGUE DE APLICACIÓN DJANGO EN HEROKU =====\033[0m")
    
    if not check_heroku_cli() or not check_git():
        sys.exit(1)
    
    heroku_login()
    app_name = create_heroku_app()
    add_postgres_addon(app_name)
    configure_environment(app_name)
    collect_static()
    initialize_git()
    push_to_heroku()
    apply_migrations(app_name)
    
    print(f"\n\033[1;32m¡DESPLIEGUE COMPLETADO!\033[0m")
    print(f"Tu aplicación está disponible en: https://{app_name}.herokuapp.com")
    print(f"Panel de administración: https://{app_name}.herokuapp.com/admin/")
    print("\nPuede tomar unos minutos para que la aplicación esté completamente disponible.")

if __name__ == "__main__":
    main() 