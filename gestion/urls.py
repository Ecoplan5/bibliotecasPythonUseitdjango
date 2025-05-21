from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuración del enrutador automático de REST Framework
# Genera las rutas de API basadas en los viewsets registrados
router = DefaultRouter()

# Registro de viewsets para libros y usuarios
# Genera automáticamente las rutas estándar y personalizadas:
# - /api/libros/ y /api/libros/{id}/
# - /api/usuarios/ y /api/usuarios/{id}/
# - Acciones personalizadas:
#   - /api/usuarios/{id}/prestar_libro/
#   - /api/usuarios/{id}/devolver_libro/
#   - /api/usuarios/{id}/mis_libros/
router.register(r'libros', views.LibroViewSet)
router.register(r'usuarios', views.UsuarioViewSet)

# Definición de rutas de la API
urlpatterns = [
    path('', include(router.urls)),  # Inclusión de rutas generadas
]