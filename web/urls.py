from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Redirección de la raíz a la lista de libros
    path('', RedirectView.as_view(pattern_name='libros-lista'), name='home'),
    
    # Rutas para la gestión de libros
    path('libros/', views.LibroListView.as_view(), name='libros-lista'),  # Listado general
    path('libros/<int:pk>/', views.LibroDetailView.as_view(), name='libros-detalles'),  # Detalle de libro
    path('libros/nuevo/', views.LibroCreateView.as_view(), name='libro-create'),  # Creación (admin)
    path('libros/<int:pk>/editar/', views.LibroUpdateView.as_view(), name='libro-update'),  # Edición (admin)
    path('libros/<int:pk>/eliminar/', views.LibroDeleteView.as_view(), name='libro-delete'),  # Eliminación (admin)
    
    # Rutas para gestión de préstamos
    path('mis-prestamos/', views.PrestamoListView.as_view(), name='prestamos-listas'),  # Préstamos del usuario
    path('libros/<int:pk>/prestar/', views.PrestamoCreateView.as_view(), name='prestamo-create'),  # Solicitar préstamo
    path('libros/<int:pk>/devolver/', views.PrestamoDevolucionView.as_view(), name='prestamo-devolucion'),  # Devolución
    path('historial-prestamos/', views.HistorialPrestamosView.as_view(), name='historial-prestamos'),  # Historial (admin)
    path('mi-historial-prestamos/', views.MiHistorialPrestamosView.as_view(), name='mi-historial-prestamos'),  # Historial personal
    path('administrar-usuarios/', views.AdministrarUsuariosView.as_view(), name='administrar-usuarios'),  # Gestión de usuarios (admin)
    path('usuarios/<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='usuario-delete'),  # Eliminación de usuario (admin)
    
    # Rutas de autenticación
    path('login/', views.CustomLoginView.as_view(), name='login'),  # Inicio de sesión
    path('logout/', views.LogoutView.as_view(), name='logout'),  # Cierre de sesión
    path('registro/', views.RegistroView.as_view(), name='registro'),  # Registro de usuario
]