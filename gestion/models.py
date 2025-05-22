from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Modelo de Libro para almacenar la información básica de cada libro
# Este es el modelo central del sistema ya que toda la aplicación gira 
# en torno a la gestión de estos elementos
class Libro(models.Model):
    titulo = models.CharField(max_length=200)  # Título completo del libro
    autor = models.CharField(max_length=100)  # Nombre del autor o autores
    año_publicacion = models.IntegerField()  # Año de publicación para catalogado
    cantidad_stock = models.IntegerField(default=0)  # Cantidad de ejemplares disponibles
    
    def __str__(self):
        # Decidí usar solo el título para facilitar la identificación rápida
        # en la interfaz de administración y en las listas desplegables
        return self.titulo

# Modelo de usuario personalizado que extiende el usuario estándar de Django
# Lo configuré con roles y campos adicionales específicos para la biblioteca
class Usuario(AbstractUser):
    # Definí solo dos roles para simplificar la gestión de permisos
    # En el futuro podría añadir más como 'bibliotecario', 'supervisor', etc.
    ROLES = (
        ('regular', 'Usuario Regular'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=7, choices=ROLES, default='regular')
    
    # Esta relación ManyToMany me pareció la forma más eficiente de registrar
    # qué libros tiene actualmente cada usuario, facilitando las consultas
    libros_prestados = models.ManyToManyField(Libro, blank=True)
    
    # Hice el email único para evitar registros duplicados y poder
    # usarlo como método alternativo de login en el futuro
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        # Creé esta property para simplificar las verificaciones de permisos
        # en las vistas y evitar repetir la comparación de rol en todo el código
        return self.rol == 'admin'

# Modelo para el registro histórico de préstamos
# Este modelo es crucial para mantener un historial completo 
# incluso después de que los libros sean devueltos
class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)  # Referencia al libro
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que realizó el préstamo
    fecha_prestamo = models.DateTimeField(default=timezone.now)  # Cuándo se prestó el libro
    devuelto = models.BooleanField(default=False)  # Indica si ya fue devuelto
    fecha_devolucion = models.DateTimeField(null=True, blank=True)  # Cuándo se devolvió
    
    def __str__(self):
        # Combiné libro y usuario para identificar claramente cada préstamo
        # en los listados y en el panel de administración
        return f"{self.libro.titulo} - {self.usuario.username}"
    
    class Meta:
        # Configuración adicional para mejorar la presentación y ordenación
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']  # Los más recientes primero