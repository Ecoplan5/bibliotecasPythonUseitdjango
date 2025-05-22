# Estructura Técnica - Sistema Biblioteca

Este documento explica en detalle cómo está estructurado el proyecto técnicamente, cómo se conectan las diferentes partes y cuál es el propósito de cada configuración. Ideal para comprender el funcionamiento interno del sistema.

## 1. Configuraciones en biblioteca/settings.py

El archivo `settings.py` es el corazón de la configuración de Django. Aquí se especifican todos los parámetros de funcionamiento del sistema:

### Aplicaciones instaladas
```python
INSTALLED_APPS = [
    'django.contrib.admin',  # Panel de administración
    'django.contrib.auth',   # Autenticación de usuarios
    'django.contrib.contenttypes',  # Tipos de contenido para modelos genéricos
    'django.contrib.sessions',  # Manejo de sesiones
    'django.contrib.messages',  # Sistema de mensajes flash
    'django.contrib.staticfiles',  # Servicio de archivos estáticos
    'rest_framework',  # Framework para crear API REST
    'gestion',  # Aplicación para gestión de datos y API
    'web',  # Aplicación para interfaz web
    'widget_tweaks',  # Mejoras para widgets de formularios
]
```
**¿Por qué?** Cada aplicación añade funcionalidades específicas. Las primeras 6 son de Django. Las 4 últimas son específicas del proyecto.

### Modelo de usuario personalizado
```python
AUTH_USER_MODEL = 'gestion.Usuario'
```
**¿Por qué?** Esto reemplaza el modelo de usuario predeterminado de Django por nuestro modelo personalizado `Usuario` en la aplicación `gestion`. Permite añadir campos extra como `rol` y `libros_prestados`.

### Configuración de base de datos
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```
**¿Por qué?** Especifica qué base de datos usar. Aquí usamos SQLite para desarrollo por su simplicidad (es un archivo) pero podría cambiarse a MySQL o PostgreSQL para producción.

### Configuración de REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```
**¿Por qué?** Define los permisos predeterminados (usuarios autenticados pueden escribir, anónimos solo leer) y los métodos de autenticación para la API.

### Configuración de JWT
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```
**¿Por qué?** Especifica la duración de los tokens JWT: 60 minutos para el token de acceso, 1 día para el token de refresco.

### Redirecciones de autenticación
```python
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```
**¿Por qué?** Determina a dónde se redirige al usuario después de iniciar o cerrar sesión.

## 2. Configuración de URLs (biblioteca/urls.py)

```python
urlpatterns = [
    path('admin/', admin.site.urls),  # Panel de administración
    path('api/', include('gestion.urls')),  # API REST
    path('', include('web.urls')),  # Interfaz web
    path('api/token/', TokenObtainPairView.as_view()),  # Obtener token JWT
    path('api/token/refresh/', TokenRefreshView.as_view()),  # Refrescar token JWT
]
```

**¿Por qué y para qué?** Define las rutas principales del proyecto:
- `/admin/`: Panel de administración de Django
- `/api/`: Todas las URLs de la API REST (en gestion/urls.py)
- `/`: Todas las URLs de la interfaz web (en web/urls.py)
- `/api/token/` y `/api/token/refresh/`: Endpoints JWT para autenticación en la API

Cada URL dirige la solicitud al controlador adecuado según el patrón de URL.

## 3. Configuración WSGI (biblioteca/wsgi.py)

```python
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
application = get_wsgi_application()
```

**¿Por qué es importante?** WSGI (Web Server Gateway Interface) es el estándar para servidores web Python:

1. Define cómo se comunican los servidores web (como Apache, Nginx) con aplicaciones Python
2. Crea una variable `application` que el servidor web utiliza para procesar solicitudes HTTP
3. Configura el entorno para cargar los settings de Django
4. **Se usa en producción** cuando desplegamos la aplicación en un servidor real

En desarrollo, no usamos WSGI directamente porque `python manage.py runserver` crea su propio servidor, pero en producción es esencial.

## 4. Relaciones en la aplicación 'gestion'

La aplicación `gestion` maneja los datos y la API:

### Modelos (gestion/models.py)
Define tres modelos principales:
- `Libro`: Almacena información de libros
- `Usuario`: Extiende el usuario de Django (es nuestro AUTH_USER_MODEL)
- `Prestamo`: Registra préstamos entre usuarios y libros

### Serializadores (gestion/serializers.py)
```python
class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = '__all__'
```

**¿Cómo se relaciona?** Convierte objetos de modelo a JSON para la API. Es el "transformador" entre el mundo Python y el mundo API/JSON.

### Vistas de API (gestion/views.py)
```python
class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
```

**¿Cómo se relaciona?** 
1. Recibe solicitudes HTTP
2. Utiliza serializadores para convertir datos
3. Procesa la lógica (verificar permisos, validar datos)
4. Responde con datos serializados

### URLs de API (gestion/urls.py)
```python
router = DefaultRouter()
router.register(r'libros', views.LibroViewSet)
router.register(r'usuarios', views.UsuarioViewSet)
```

**¿Cómo se relaciona?** 
El router automáticamente crea URLs para todas las acciones CRUD:
- GET /api/libros/ → Lista libros
- POST /api/libros/ → Crea libro
- GET /api/libros/{id}/ → Detalle de libro
- PUT /api/libros/{id}/ → Actualiza libro
- DELETE /api/libros/{id}/ → Elimina libro
- Y endpoints custom: /api/usuarios/{id}/prestar_libro/

## 5. Relaciones en la aplicación 'web'

La aplicación `web` maneja la interfaz de usuario:

### Vistas web (web/views.py)
```python
class LibroListView(ListView):
    model = Libro
    template_name = 'web/libros_lista.html'
    context_object_name = 'libros'
```

**¿Cómo se relaciona?** 
1. Obtiene datos del modelo (`model = Libro`)
2. Procesa la lógica para la vista 
3. Envía los datos a una plantilla HTML (`template_name`)
4. Los datos están disponibles en la plantilla con el nombre `libros` (`context_object_name`)

### URLs web (web/urls.py)
```python
path('libros/', views.LibroListView.as_view(), name='libros-lista')
```

**¿Cómo se relaciona?**
1. Define una URL `/libros/`
2. Asocia esa URL con una vista `LibroListView`
3. Asigna un nombre `libros-lista` que se usa en plantillas para referencias

### Plantillas (web/templates/web/*.html)
```html
{% for libro in libros %}
    <h2>{{ libro.titulo }}</h2>
{% endfor %}
```

**¿Cómo se relacionan?** Reciben los datos enviados por la vista y generan HTML dinámico.

## 6. Flujo completo de una solicitud

Cuando un usuario visita una página, el flujo es:

1. **URL**: El usuario escribe `http://localhost:8000/libros/`
2. **urls.py**: Django busca la URL en `biblioteca/urls.py` → `web/urls.py` y encuentra `LibroListView`
3. **views.py**: `LibroListView` consulta la base de datos con `Libro.objects.all()`
4. **models.py**: El modelo `Libro` recupera datos de la tabla `libro` en SQLite
5. **views.py**: La vista envía los datos a la plantilla `libros_lista.html`
6. **template**: La plantilla renderiza los datos como HTML
7. **HTTP**: El HTML se envía al navegador como respuesta

## 7. Flujo de la API REST

Cuando una aplicación cliente hace una solicitud a la API:

1. **URL**: Cliente envía `GET http://localhost:8000/api/libros/`
2. **urls.py**: Django encuentra el `LibroViewSet` en `gestion/views.py` 
3. **views.py**: El viewset consulta `Libro.objects.all()`
4. **serializers.py**: El serializer convierte objetos modelo a JSON
5. **HTTP**: La API devuelve una respuesta JSON

## 8. Autenticación

El sistema usa dos mecanismos:

1. **Sesiones (web)**: Para usuarios en el navegador
   - Usuario introduce credenciales en `/login/`
   - Django crea una sesión y almacena la cookie
   - Las peticiones subsiguientes incluyen la cookie

2. **JWT (API)**: Para aplicaciones cliente
   - Cliente solicita token en `/api/token/`
   - API devuelve tokens de acceso y refresco
   - Cliente incluye token en cabecera (`Authorization: Bearer xxx`)

Ambos mecanismos coexisten para servir diferentes tipos de clientes.

## 9. Seguridad

Varios niveles de protección:

1. **Autenticación**: Verifica identidad (¿quién es?)
2. **Autorización**: Verifica permisos (¿qué puede hacer?)
   ```python
   @login_required  # Solo usuarios autenticados
   def mi_vista(request):
       pass
   ```
   
   ```python
   def test_func(self):  # Solo administradores
       return self.request.user.is_admin
   ```

3. **CSRF**: Protege contra ataques Cross-Site Request Forgery
   ```html
   {% csrf_token %}  <!-- En formularios -->
   ```

## 10. Ciclo de vida de un préstamo

Un buen ejemplo de cómo interactúan todos los componentes:

1. **URL**: Usuario solicita préstamo en `/libros/{id}/prestar/`
2. **View**: `PrestamoCreateView` procesa:
   - Verifica disponibilidad con consulta al modelo `Libro`
   - Crea relación en `usuario.libros_prestados.add(libro)` (relación M2M)
   - Crea registro en `Prestamo.objects.create()` (para historial)
   - Actualiza stock con `libro.save()`
   - Redirige con mensaje flash

Este flujo involucra modelos, vistas, URLs y plantillas trabajando juntos.

## 11. Conexión a la web y servidor HTTP

La conexión entre el servidor Django y los usuarios web se establece así:

### Servidor de desarrollo

En entorno de desarrollo usamos:
```
python manage.py runserver
```

Este comando:
1. Inicia un servidor HTTP ligero en `localhost:8000`
2. Carga la aplicación WSGI definida en `biblioteca/wsgi.py`
3. Procesa solicitudes HTTP y las dirige al sistema de URLs de Django
4. Devuelve respuestas HTTP al navegador

### Servidor de producción

En producción se usa una configuración más robusta:
```
[Servidor Web (Nginx/Apache)] → [WSGI (Gunicorn/uWSGI)] → [Aplicación Django]
```

1. **Servidor Web**: Gestiona conexiones HTTP, archivos estáticos y balanceo de carga
2. **WSGI**: Traduce solicitudes HTTP al formato que Django entiende
3. **Aplicación Django**: Procesa la lógica y genera respuestas

Esto permite manejar múltiples conexiones simultáneas y mejorar el rendimiento.

## 12. Integración entre web y API

Existen dos formas en que la web obtiene datos:

### 1. Acceso directo al modelo (más común)

```python
# En web/views.py
class LibroListView(ListView):
    model = Libro  # Acceso directo a los modelos
    
    def get_queryset(self):
        # Consulta directa a la base de datos
        return Libro.objects.filter(cantidad_stock__gt=0)
```

**Ventaja**: Más eficiente, una sola consulta a la base de datos.

### 2. Consumo de la propia API (menos común)

```python
# Hipotético ejemplo de consumo de API interno
import requests

def obtener_libros(request):
    # Llama a nuestra propia API
    response = requests.get('http://localhost:8000/api/libros/')
    libros = response.json()
    return render(request, 'web/libros_lista.html', {'libros': libros})
```

**Ventaja**: Misma fuente de datos para web y clientes externos.
**Desventaja**: Menos eficiente (doble procesamiento).

En nuestro proyecto usamos principalmente el primer método (acceso directo) para mejor rendimiento.

## 13. Integración de Bootstrap y CSS

### Cómo se integra Bootstrap

Bootstrap se incluye en la plantilla base (`web/templates/web/base.html`):

```html
<!-- En base.html -->
<head>
    <!-- Bootstrap CSS desde CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Iconos de Bootstrap -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    
    <!-- Scripts de Bootstrap -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- CSS personalizado -->
    <link rel="stylesheet" href="{% static 'css/main.css' %}">
    
    <!-- Bloque para CSS adicional por página -->
    {% block extra_css %}{% endblock %}
</head>
```

### Uso de clases CSS de Bootstrap

Como vemos en `libros_lista.html`:

```html
<div class="card mb-4 search-form">  <!-- Componente card con margen inferior -->
    <div class="card-body">  <!-- Parte interna de la card -->
        <form method="get" action="{% url 'libros-lista' %}" class="row g-3">  <!-- Fila con gap -->
            <div class="col-md-8">  <!-- Columna de 8/12 en pantallas medianas -->
                <div class="input-group">  <!-- Grupo de input para combinar elementos -->
                    <input type="text" name="buscar" class="form-control">  <!-- Estilo de input -->
                    <button class="btn btn-primary" type="submit">  <!-- Botón primario azul -->
                        <i class="bi bi-search"></i> Buscar  <!-- Icono de búsqueda -->
                    </button>
                </div>
            </div>
        </form>
    </div>
</div>
```

### CSS personalizado

Complementamos Bootstrap con CSS personalizado:

1. Definimos archivos CSS en `web/static/css/`:
   ```css
   /* En web/static/css/libros.css */
   .libro-card {
       transition: transform 0.2s;
       box-shadow: 0 4px 6px rgba(0,0,0,0.1);
   }
   
   .libro-card:hover {
       transform: translateY(-5px);
   }
   ```

2. Los incluimos en templates específicos:
   ```html
   {% block extra_css %}
   <link rel="stylesheet" href="{% static 'css/libros.css' %}">
   {% endblock %}
   ```

## 14. Integración de JavaScript en Django

Django integra JavaScript de varias formas:

### 1. Scripts en plantillas

```html
<!-- En una plantilla -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Código JavaScript al cargar la página
        const botones = document.querySelectorAll('.btn-prestar');
        botones.forEach(btn => {
            btn.addEventListener('click', confirmarPrestamo);
        });
    });
    
    function confirmarPrestamo(e) {
        if (!confirm('¿Confirmar préstamo?')) {
            e.preventDefault();
        }
    }
</script>
```

### 2. Scripts incluidos desde archivos estáticos

```html
<!-- En base.html o plantilla específica -->
<script src="{% static 'js/prestamos.js' %}"></script>
```

### 3. Django y AJAX

Para interacciones dinámicas con el servidor:

```javascript
// En un archivo .js
function actualizarEstado(prestamoId) {
    fetch(`/api/prestamos/${prestamoId}/devolver/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Actualiza la UI con data
        document.getElementById(`estado-${prestamoId}`).textContent = 'Devuelto';
    });
}

// Función auxiliar para obtener cookie CSRF
function getCookie(name) {
    // ... código para obtener cookie ...
}
```

### 4. Protección CSRF en JavaScript

Django requiere tokens CSRF en solicitudes POST:

```html
<!-- En una plantilla -->
<script>
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Usar en fetch/axios
    fetch('/api/endpoint/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            // Otros headers
        },
        body: JSON.stringify(data)
    });
</script>
```

Este mecanismo de CSRF es por qué verás JavaScript interactuando con elementos generados por Django - es una medida de seguridad esencial. 