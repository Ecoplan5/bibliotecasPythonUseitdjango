# Sistema de Gestión de Biblioteca

Sistema web para gestión de biblioteca con préstamos de libros, desarrollado con Django y Django REST Framework.

## Características

-  Gestión de libros (crear, leer, actualizar, eliminar)
-  Sistema de préstamos y devoluciones de libros
-  Búsqueda de libros por título y autor
-  Panel de administración de usuarios
-  Historial de préstamos para administradores
-  API RESTful completa
-  Autenticación con JWT

## Requisitos

- Python 3.11+
- Django 5.2.1
- Django REST Framework
- Otros módulos especificados en requirements.txt

## Instalación Rápida

1. Clonar este repositorio:
   ```bash
   git clone https://github.com/Ecoplan5/bibliotecasPythonUseitdjango.git
   cd bibliotecas
   ```

2. Crear y activar un entorno virtual:
   ```bash
   # En Windows
   python -m venv venv
   venv\Scripts\activate
   
   # En macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Aplicar migraciones:
   ```bash
   python manage.py migrate
   ```

5. Crear usuario administrador:
   ```bash
   python manage.py createsuperuser
   ```

6. Iniciar servidor:
   ```bash
   python manage.py runserver
   ```

## Acceso al Sistema

1. **Interfaz Web**: Visita http://127.0.0.1:8000/ en tu navegador

2. **Panel de Administración**: Accede a http://127.0.0.1:8000/admin/ con las credenciales de tu superusuario

3. **Acceso SuperAdmin**: 
   - Usuario: `SuperAdmin`
   - Contraseña: `admin1234`
   - Email: `admin@biblioteca.com`
   - Este usuario tiene todos los permisos para administrar el sistema completo
   - Se crea automáticamente durante la migración
   - Accede desde la página de login normal en http://127.0.0.1:8000/login/

4. **API REST**:
   - Endpoint principal: http://127.0.0.1:8000/api/
   - Documentación completa de la API en `postman_endpoints.md`
   - Autenticación: http://127.0.0.1:8000/api/token/

## Despliegue en Railway

La aplicación está desplegada en Railway debido a las limitaciones de la capa gratuita de Heroku.

- **URL de la aplicación**: [https://bibliotecaspythonuseitdjango-production.up.railway.app/libros/](https://bibliotecaspythonuseitdjango-production.up.railway.app/libros/)
- **Base de datos**: PostgreSQL proporcionada por Railway
- **Configuración**: La aplicación se configuró para despliegue automático desde GitHub

## Registro de Usuarios

Para registrar un nuevo usuario regular en el sistema:

1. Accede a la página principal: [https://bibliotecaspythonuseitdjango-production.up.railway.app/libros/](https://bibliotecaspythonuseitdjango-production.up.railway.app/libros/)
2. Haz clic en el enlace "Registrarse" en la barra de navegación
3. Completa el formulario con:
   - Nombre de usuario (único)
   - Contraseña (mínimo 8 caracteres)
   - Confirmar contraseña
   - Correo electrónico (opcional)
   - Nombre y apellido
4. Haz clic en "Registrarse"
5. Después del registro exitoso, podrás iniciar sesión con tus credenciales
6. Por defecto, todos los usuarios nuevos tienen rol de "usuario regular"
7. Los usuarios regulares pueden:
   - Ver libros disponibles
   - Solicitar préstamos de libros
   - Devolver libros prestados
   - Ver su historial de préstamos

## Tipos de Usuario

1. **Administrador**
   - Tiene acceso a todas las funcionalidades
   - Puede crear, editar y eliminar libros
   - Puede ver el historial completo de préstamos
   - Puede consultar los préstamos activos

2. **Usuario Regular**
   - Puede ver la lista de libros disponibles
   - Puede solicitar préstamos de libros
   - Puede devolver libros prestados
   - Puede ver su historial de préstamos

## Guía de Uso Rápido

### Para Usuarios Regulares:

1. Regístrate o inicia sesión en el sistema
2. Navega por la lista de libros disponibles
3. Usa el buscador para encontrar libros específicos
4. Solicita un préstamo haciendo clic en el botón "Solicitar préstamo" en la página de detalles del libro
5. Consulta tus libros prestados en la sección "Mis Préstamos"
6. Devuelve un libro desde la sección "Mis Préstamos"

### Para Administradores:

1. Inicia sesión con credenciales de administrador
2. Añade nuevos libros desde la sección "Libros" o el botón "Nuevo Libro"
3. Edita o elimina libros existentes
4. Consulta el historial completo de préstamos
5. Supervisa los préstamos activos y las devoluciones

## Documentación Adicional

- **Guía de Instalación Completa**: Ver archivo `guia_instalacion.md`
- **Documentación de API**: Ver archivo `docs/postman/postman_endpoints.md`
- **Colección Postman**: Disponible en `docs/postman/biblioteca_api_collection.json`
- **Para importar la colección Postman**:
  1. Abre Postman
  2. Haz clic en "Import"
  3. Arrastra el archivo JSON o búscalo en tu sistema
  4. Configura la variable de entorno `base_url` con la URL de la API (`https://bibliotecaspythonuseitdjango-production.up.railway.app`)
  5. Ejecuta la solicitud "Obtener Token JWT" con las credenciales para obtener el token de acceso

## Notas para Desarrolladores

Si deseas contribuir al proyecto:

1. Sigue las pautas de instalación en `guia_instalacion.md`
2. Las consultas a la API se pueden probar con Postman siguiendo la documentación en `postman_endpoints.md`
3. Para ejecutar pruebas unitarias:
   ```bash
   python manage.py test
   ```

[Autor Feliciano Mosquera]