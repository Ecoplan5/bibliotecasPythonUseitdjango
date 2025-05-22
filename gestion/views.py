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
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'mensaje': 'Libro creado exitosamente',
                'libro': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'mensaje': 'Error al crear el libro',
            'errores': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'mensaje': 'Libro actualizado exitosamente',
                'libro': serializer.data
            })
        return Response({
            'mensaje': 'Error al actualizar el libro',
            'errores': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'mensaje': 'Libro actualizado parcialmente con éxito',
                'libro': serializer.data
            })
        return Response({
            'mensaje': 'Error al actualizar el libro parcialmente',
            'errores': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        titulo = instance.titulo
        self.perform_destroy(instance)
        return Response({
            'mensaje': f'Libro "{titulo}" eliminado exitosamente'
        }, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'mensaje': f'Se encontraron {len(queryset)} libros',
            'libros': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'mensaje': f'Detalles del libro "{instance.titulo}"',
            'libro': serializer.data
        })

# ViewSet para gestionar usuarios y operaciones relacionadas
# Incluye endpoints adicionales para préstamos y devoluciones
class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()  # Consulta base de usuarios
    serializer_class = UsuarioSerializer  # Serializer para transformación
    
    def get_permissions(self):
        # Solo los admins pueden gestionar usuarios, excepto ver detalles propios
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'list']:
            permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                'mensaje': 'Usuario creado exitosamente',
                'usuario': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'mensaje': 'Error al crear el usuario',
            'errores': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'mensaje': f'Usuario "{instance.username}" actualizado exitosamente',
                'usuario': serializer.data
            })
        return Response({
            'mensaje': 'Error al actualizar el usuario',
            'errores': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                'mensaje': f'Usuario "{instance.username}" actualizado parcialmente con éxito',
                'usuario': serializer.data
            })
        return Response({
            'mensaje': 'Error al actualizar el usuario parcialmente',
            'errores': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        username = instance.username
        self.perform_destroy(instance)
        return Response({
            'mensaje': f'Usuario "{username}" eliminado exitosamente'
        }, status=status.HTTP_200_OK)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'mensaje': f'Se encontraron {len(queryset)} usuarios',
            'usuarios': serializer.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'mensaje': f'Detalles del usuario "{instance.username}"',
            'usuario': serializer.data
        })
    
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
                {'mensaje': 'Solo usuarios regulares pueden prestar libros'},
                status=status.HTTP_403_FORBIDDEN
            )
      
        # Validación de parámetros
        # Importante asegurar que recibimos los datos necesarios para procesar
        if not libro_id:
            return Response(
                {'mensaje': 'Se requiere libro_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación de existencia del libro
        # Manejo específico para obtener un error más descriptivo
        try:
            libro = Libro.objects.get(id=libro_id)
        except Libro.DoesNotExist:
            return Response(
                {'mensaje': f'El libro con ID {libro_id} no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validación de disponibilidad
        # Verifico stock antes de procesar para evitar préstamos imposibles
        if libro.cantidad_stock <= 0:
            return Response(
                {'mensaje': f'No hay ejemplares disponibles del libro "{libro.titulo}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación de préstamo duplicado
        # Evito que un usuario intente prestar el mismo libro múltiples veces
        if libro in usuario.libros_prestados.all():
            return Response(
                {'mensaje': f'Ya tienes prestado el libro "{libro.titulo}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesamiento del préstamo
        # Actualizo la relación y disminuyo el stock - operación atómica
        usuario.libros_prestados.add(libro)
        libro.cantidad_stock -= 1
        libro.save()
        
        return Response(
            {
                'mensaje': f'Libro "{libro.titulo}" prestado exitosamente a {usuario.username}',
                'libro': LibroSerializer(libro).data
            },
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
                {'mensaje': 'Se requiere libro_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validación de existencia del libro
        # Manejo consistente con el endpoint de préstamo
        try:
            libro = Libro.objects.get(id=libro_id)
        except Libro.DoesNotExist:
            return Response(
                {'mensaje': f'El libro con ID {libro_id} no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validación de posesión del libro
        # Verifico que el usuario realmente tenga el libro prestado
        if libro not in usuario.libros_prestados.all():
            return Response(
                {'mensaje': f'No tienes prestado el libro "{libro.titulo}"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Procesamiento de la devolución
        # Actualizo la relación y aumento el stock - operación atómica
        usuario.libros_prestados.remove(libro)
        libro.cantidad_stock += 1
        libro.save()
        
        return Response(
            {
                'mensaje': f'Libro "{libro.titulo}" devuelto exitosamente por {usuario.username}',
                'libro': LibroSerializer(libro).data
            },
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
        return Response({
            'mensaje': f'Se encontraron {libros.count()} libros prestados a {usuario.username}',
            'libros': serializer.data
        })