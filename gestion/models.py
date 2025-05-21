from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Modelo de Libro para almacenar la información básica de cada libro
# en la biblioteca.
class Libro(models.Model):
    titulo = models.CharField(max_length=200)  # Título del libro
    autor = models.CharField(max_length=100)  # Nombre del autor
    año_publicacion = models.IntegerField()  # Año de publicación
    cantidad_stock = models.IntegerField(default=0)  # Inventario disponible
    
    def __str__(self):
        # Representación legible en el admin y otras partes
        return self.titulo

# Modelo de usuario personalizado que extiende el usuario estándar
# para añadir funcionalidades específicas de la biblioteca
class Usuario(AbstractUser):
    # Opciones de roles disponibles en el sistema
    ROLES = (
        ('regular', 'Usuario Regular'),
        ('admin', 'Administrador'),
    )
    rol = models.CharField(max_length=7, choices=ROLES, default='regular')
    
    # Relación muchos a muchos con los libros prestados
    # Permite saber qué libros tiene cada usuario
    libros_prestados = models.ManyToManyField(Libro, blank=True)
    
    # Campo email con validación adicional
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        # Método auxiliar para verificar el rol de administrador
        return self.rol == 'admin'

# Modelo para el registro histórico de préstamos
# Guarda información detallada de cada transacción
class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)  # Libro prestado
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)  # Usuario que lo pidió
    fecha_prestamo = models.DateTimeField(default=timezone.now)  # Fecha de inicio
    devuelto = models.BooleanField(default=False)  # Estado del préstamo
    fecha_devolucion = models.DateTimeField(null=True, blank=True)  # Fecha de devolución
    
    def __str__(self):
        # Formato para facilitar identificación
        return f"{self.libro.titulo} - {self.usuario.username}"
    
    class Meta:
        # Configuración adicional del modelo
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ['-fecha_prestamo']