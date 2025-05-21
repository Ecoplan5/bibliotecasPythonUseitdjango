# Guía de Instalación - Sistema de Biblioteca

Esta guía te llevará paso a paso a través del proceso de configuración e instalación del Sistema de Gestión de Biblioteca desde cero.

## Requisitos Previos

- Python 3.11 o superior
- pip (gestor de paquetes de Python)
- Conocimientos básicos de línea de comandos

## Paso 1: Crear el Entorno Virtual

```bash
# Crear una carpeta para el proyecto
mkdir biblioteca
cd biblioteca

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate
```

## Paso 2: Instalar Django y Dependencias

```bash
# Actualizar pip
pip install --upgrade pip

# Instalar Django y dependencias
pip install django==5.2.1
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install django-widget-tweaks
```

## Paso 3: Crear el Proyecto Django

```bash
# Crear proyecto Django
django-admin startproject biblioteca .

# Crear aplicaciones
python manage.py startapp gestion
python manage.py startapp web
```

## Paso 4: Configurar el Archivo settings.py

Edita el archivo `biblioteca/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'gestion',
    'web',
    'widget_tweaks',
]

# Configuración de usuario personalizado
AUTH_USER_MODEL = 'gestion.Usuario'

# Configuración de REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
}

# Configuración de JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# URLs de redirección
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Configuración de CSRF para desarrollo local
CSRF_TRUSTED_ORIGINS = ['http://localhost:8000', 'http://127.0.0.1:8000']
```

## Paso 5: Crear los Modelos en gestion/models.py

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    año_publicacion = models.IntegerField()
    cantidad_stock = models.IntegerField(default=0)
    
    def __str__(self):
        return self.titulo

class Usuario(AbstractUser):
    ROLES = (
        ('regular', 'Usuario Regular'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=7, choices=ROLES, default='regular')
    libros_prestados = models.ManyToManyField(Libro, blank=True)
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.rol == 'admin'

class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    devuelto = models.BooleanField(default=False)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.libro.titulo} - {self.usuario.username}"
    
    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']
```

## Paso 6: Configurar las URLs del Proyecto

En `biblioteca/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gestion.urls')),
    path('', include('web.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

## Paso 7: Crear la API REST en gestion/serializers.py

```python
from rest_framework import serializers
from .models import Libro, Usuario

class LibroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Libro
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'rol', 'libros_prestados']
```

## Paso 8: Crear las Vistas de API en gestion/views.py

```python
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Libro, Usuario
from .serializers import LibroSerializer, UsuarioSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsuarioSerializer
    
    @action(detail=True, methods=['post'])
    def prestar_libro(self, request, pk=None):
        usuario = self.get_object()
        
        libro_id = request.data.get('libro_id')
        
        if usuario.rol != 'regular':
            return Response({'error': 'Solo usuarios regulares pueden prestar libros'}, status=status.HTTP_403_FORBIDDEN)
      
        if not libro_id:
            return Response({'error': 'Se requiere libro_id'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            libro = Libro.objects.get(id=libro_id)
        except Libro.DoesNotExist:
            return Response({'error': 'Libro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        if libro.cantidad_stock <= 0:
            return Response({'error': 'No hay ejemplares disponibles'}, status=status.HTTP_400_BAD_REQUEST)
        
        if libro in usuario.libros_prestados.all():
            return Response({'error': 'Ya tienes este libro prestado'}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario.libros_prestados.add(libro)
        libro.cantidad_stock -= 1
        libro.save()
        
        return Response({'status': 'Libro prestado'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def devolver_libro(self, request, pk=None):
        usuario = self.get_object()
        libro_id = request.data.get('libro_id')
        
        if not libro_id:
            return Response({'error': 'Se requiere libro_id'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            libro = Libro.objects.get(id=libro_id)
        except Libro.DoesNotExist:
            return Response({'error': 'Libro no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        
        if libro not in usuario.libros_prestados.all():
            return Response({'error': 'No tienes este libro prestado'}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario.libros_prestados.remove(libro)
        libro.cantidad_stock += 1
        libro.save()
        
        return Response({'status': 'Libro devuelto'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def mis_libros(self, request, pk=None):
        usuario = self.get_object()
        libros = usuario.libros_prestados.all()
        serializer = LibroSerializer(libros, many=True)
        return Response(serializer.data)
```

## Paso 9: Configurar URLs de la API en gestion/urls.py

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'libros', views.LibroViewSet)
router.register(r'usuarios', views.UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

## Paso 10: Crear Formulario de Registro en web/forms.py

```python
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')
```

## Paso 11: Crear Vistas Web en web/views.py

Implementar todas las vistas para la interfaz web (la implementación completa es larga para esta guía, pero puedes ver el código actual en el archivo).

## Paso 12: Configurar URLs Web en web/urls.py

```python
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='libros-lista'), name='home'),
    path('libros/', views.LibroListView.as_view(), name='libros-lista'),
    path('libros/<int:pk>/', views.LibroDetailView.as_view(), name='libros-detalles'),
    path('libros/nuevo/', views.LibroCreateView.as_view(), name='libro-create'),
    path('libros/<int:pk>/editar/', views.LibroUpdateView.as_view(), name='libro-update'),
    path('libros/<int:pk>/eliminar/', views.LibroDeleteView.as_view(), name='libro-delete'),
    path('mis-prestamos/', views.PrestamoListView.as_view(), name='prestamos-listas'),
    path('libros/<int:pk>/prestar/', views.PrestamoCreateView.as_view(), name='prestamo-create'),
    path('libros/<int:pk>/devolver/', views.PrestamoDevolucionView.as_view(), name='prestamo-devolucion'),
    path('historial-prestamos/', views.HistorialPrestamosView.as_view(), name='historial-prestamos'),
    
    # Autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
]
```

## Paso 13: Crear las Plantillas HTML

Crear todas las plantillas HTML en las carpetas:
- `web/templates/web/`

## Paso 14: Crear Archivos CSS en Carpeta Static

Crear archivos CSS en:
- `web/static/css/`

## Paso 15: Realizar Migraciones y Crear Superusuario

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

## Paso 16: Ejecutar el Servidor

```bash
python manage.py runserver
```

¡Y listo! Ahora puedes acceder al sitio en http://127.0.0.1:8000/ 