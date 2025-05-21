# Sistema de Gestión de Biblioteca

Sistema web para gestión de biblioteca con préstamos de libros, desarrollado con Django y Django REST Framework.

## Características

- ✅ Gestión de libros (crear, leer, actualizar, eliminar)
- ✅ Sistema de préstamos y devoluciones de libros
- ✅ Búsqueda de libros por título y autor
- ✅ Panel de administración de usuarios
- ✅ Historial de préstamos para administradores
- ✅ API RESTful completa
- ✅ Autenticación con JWT

## Requisitos

- Python 3.11+
- Django 5.2.1
- Django REST Framework
- Otros módulos especificados en requirements.txt

## Instalación Rápida

1. Clonar este repositorio:
   ```bash
   git clone <url-del-repositorio>
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

3. **API REST**:
   - Endpoint principal: http://127.0.0.1:8000/api/
   - Documentación completa de la API en `postman_endpoints.md`
   - Autenticación: http://127.0.0.1:8000/api/token/

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
- **Documentación de API**: Ver archivo `postman_endpoints.md`

## Notas para Desarrolladores

Si deseas contribuir al proyecto:

1. Sigue las pautas de instalación en `guia_instalacion.md`
2. Las consultas a la API se pueden probar con Postman siguiendo la documentación en `postman_endpoints.md`
3. Para ejecutar pruebas unitarias:
   ```bash
   python manage.py test
   ```

## Licencia

[MIT](LICENSE) 