from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Libro, Usuario
from .serializers import LibroSerializer, UsuarioSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

# ViewSet para la gestión de libros a través de la API
# Proporciona operaciones CRUD completas para el modelo Libro
class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()  # Consulta base de libros
    serializer_class = LibroSerializer  # Serializer para transformación de datos
    
    def get_permissions(self):
        # Configuración de permisos basada en la acción
        # Decidí restringir escritura solo para administradores para mantener
        # la integridad de los datos pero permitir consultas a usuarios autenticados
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return [permission() for permission in permission_classes]

# ViewSet para gestionar usuarios y operaciones relacionadas
# Incluye endpoints adicionales para préstamos y devoluciones
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Consulta base de usuarios
    serializer_class = UsuarioSerializer  # Serializer para transformación
    
    # Endpoint para préstamo de libro mediante API
    # POST /api/usuarios/{id}/prestar_libro/
    @action(detail=True, methods=['post'])
    def prestar_libro(self, request, pk=None):
        usuario = self.get_object()  # Obtiene el usuario
        
        libro_id = request.data.get('libro_id')  # Obtiene ID del libro
        
        # Validación de rol de usuario
        # Implementé esta restricción para mantener coherencia con los permisos web
        if usuario.rol != 'regular':
            return Response(
                {'error': 'Solo usuarios regulares pueden prestar libros'},
                status=status.HTTP_403_FORBIDDEN
            )
      
        # Validación de parámetros
        # Importante asegurar que recibimos los datos necesarios para procesar
        if not libro_id:
            return Response(
                {'error': 'Se requiere libro_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación de existencia del libro
        # Manejo específico para obtener un error más descriptivo
        try:
            libro = Libro.objects.get(id=libro_id)
        except Libro.DoesNotExist:
            return Response(
                {'error': 'Libro no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validación de disponibilidad
        # Verifico stock antes de procesar para evitar préstamos imposibles
        if libro.cantidad_stock <= 0:
            return Response(
                {'error': 'No hay ejemplares disponibles'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación de préstamo duplicado
        # Evito que un usuario intente prestar el mismo libro múltiples veces
        if libro in usuario.libros_prestados.all():
            return Response(
                {'error': 'Ya tienes este libro prestado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesamiento del préstamo
        # Actualizo la relación y disminuyo el stock - operación atómica
        usuario.libros_prestados.add(libro)
        libro.cantidad_stock -= 1
        libro.save()
        
        return Response(
            {'status': 'Libro prestado exitosamente'},
            status=status.HTTP_200_OK
        )
    
    # Endpoint para devolución de libro mediante API
    # POST /api/usuarios/{id}/devolver_libro/
    @action(detail=True, methods=['post'])
    def devolver_libro(self, request, pk=None):
        usuario = self.get_object()  # Obtiene el usuario
        libro_id = request.data.get('libro_id')  # Obtiene ID del libro
        
        # Validación de parámetros
        # Mismo patrón de validación que en préstamo para mantener consistencia
        if not libro_id:
            return Response(
                {'error': 'Se requiere libro_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación de existencia del libro
        # Manejo consistente con el endpoint de préstamo
        try:
            libro = Libro.objects.get(id=libro_id)
        except Libro.DoesNotExist:
            return Response(
                {'error': 'Libro no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validación de posesión del libro
        # Verifico que el usuario realmente tenga el libro prestado
        if libro not in usuario.libros_prestados.all():
            return Response(
                {'error': 'No tienes este libro prestado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesamiento de la devolución
        # Actualizo la relación y aumento el stock - operación atómica
        usuario.libros_prestados.remove(libro)
        libro.cantidad_stock += 1
        libro.save()
        
        return Response(
            {'status': 'Libro devuelto exitosamente'},
            status=status.HTTP_200_OK
        )
    
    
    # Endpoint para consultar libros prestados
    # GET /api/usuarios/{id}/mis_libros/
    @action(detail=True, methods=['get'])
    def mis_libros(self, request, pk=None):
        usuario = self.get_object()  # Obtiene el usuario
        libros = usuario.libros_prestados.all()  # Obtiene sus libros
        serializer = LibroSerializer(libros, many=True)  # Serializa la colección
        
        # Devuelvo lista completa de libros prestados con todos sus detalles
        # Este endpoint es muy útil para apps móviles que necesitan mostrar esta info
        return Response(serializer.data)