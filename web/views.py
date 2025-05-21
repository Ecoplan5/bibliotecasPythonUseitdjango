from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.utils import timezone
from django.db.models import Q
from gestion.models import Libro, Usuario, Prestamo
from .forms import RegistroUsuarioForm

# Vista principal para mostrar libros.
#  Esta vista Muestra la lista de todos los libros disponibles en la biblioteca.
class LibroListView(ListView):
    model = Libro  # Modelo que se va a utilizar
    template_name = 'web/libros_lista.html'  # Plantilla HTML
    context_object_name = 'libros'  # Variable en el template
    
    def get_queryset(self):
        # Implementación del buscador, filtra por título o autor
        query = self.request.GET.get('buscar', '')
        if query:
            return Libro.objects.filter(
                Q(titulo__icontains=query) | 
                Q(autor__icontains=query)
            )
        return Libro.objects.all()
    
    def get_context_data(self, **kwargs):
        #  aqui Envío el término de búsqueda al template
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('buscar', '')
        return context

# Vista para mostrar los detalles de un libro específico
# Incluye información sobre disponibilidad actual
class LibroDetailView(DetailView):
    model = Libro
    template_name = 'web/libros_detalles.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        libro = self.get_object()
        
        # Contamos los préstamos activos para mostrar disponibilidad
        prestamos_activos = Prestamo.objects.filter(libro=libro, devuelto=False).count()
        context['prestamos_activos'] = prestamos_activos
        
        return context

#  en esta vista  los administradores pueden  crear nuevos libros
# Verifica permisos de administrador antes de permitir el acceso
class LibroCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Libro
    fields = ['titulo', 'autor', 'año_publicacion', 'cantidad_stock']
    template_name = 'web/libro_formularios.html'
    success_url = reverse_lazy('libros-lista')

    def test_func(self):
        # Verifica si el usuario es administrador
        return self.request.user.is_admin
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Mensaje de confirmación
        messages.success(self.request, f"Libro '{self.object.titulo}' creado exitosamente.")
        return response

# Vista para editar libros existentes
# También limitada a administradores
class LibroUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Libro
    fields = ['titulo', 'autor', 'año_publicacion', 'cantidad_stock']
    template_name = 'web/libro_formularios.html'
    success_url = reverse_lazy('libros-lista')

    def test_func(self):
        return self.request.user.is_admin
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Libro '{self.object.titulo}' actualizado exitosamente.")
        return response

# Vista para que los usuarios vean sus libros prestados
# Muestra la colección personal de préstamos activos
class PrestamoListView(LoginRequiredMixin, ListView):
    template_name = 'web/prestamos_listas.html'
    context_object_name = 'libros'

    def get_queryset(self):
        # Accede directamente a los libros prestados del usuario
        return self.request.user.libros_prestados.all()

# Vista para gestionar el préstamo de un libro
# Incluye validaciones de disponibilidad y estado
class PrestamoCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        libro = get_object_or_404(Libro, pk=pk)
        usuario = request.user
        
        # Verifica la disponibilidad de ejemplares
        if libro.cantidad_stock <= 0:
            messages.error(request, "No hay ejemplares disponibles de este libro.")
            return redirect('libros-detalles', pk=pk)
        
        # Evita préstamos duplicados
        if libro in usuario.libros_prestados.all():
            messages.warning(request, "Ya tienes este libro prestado.")
            return redirect('libros-detalles', pk=pk)
        
        # Realiza el préstamo y actualiza inventario
        usuario.libros_prestados.add(libro)
        libro.cantidad_stock -= 1
        libro.save()
        
        # Registra en el historial
        Prestamo.objects.create(
            libro=libro,
            usuario=usuario
        )
        
        messages.success(request, f"Libro '{libro.titulo}' prestado exitosamente.")
        return redirect('prestamos-listas')

# Vista para procesar la devolución de un libro
# Actualiza el estado del préstamo y el inventario
class PrestamoDevolucionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        libro = get_object_or_404(Libro, pk=pk)
        usuario = request.user
        
        # Verifica que el usuario tenga el libro
        if libro not in usuario.libros_prestados.all():
            messages.error(request, "No tienes este libro prestado.")
            return redirect('prestamos-listas')
        
        # Procesa la devolución
        usuario.libros_prestados.remove(libro)
        libro.cantidad_stock += 1
        libro.save()
        
        # Actualiza el registro histórico
        prestamo = Prestamo.objects.filter(
            libro=libro,
            usuario=usuario,
            devuelto=False
        ).first()
        
        if prestamo:
            prestamo.devuelto = True
            prestamo.fecha_devolucion = timezone.now()
            prestamo.save()
        
        messages.success(request, f"Libro '{libro.titulo}' devuelto exitosamente.")
        return redirect('prestamos-listas')

# Vista administrativa para ver el historial de préstamos
# Muestra estadísticas y todos los registros de préstamos
class HistorialPrestamosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Prestamo
    template_name = 'web/historial_prestamos.html'
    context_object_name = 'prestamos'
    
    def test_func(self):
        # Limita acceso solo a administradores
        return self.request.user.is_admin
    
    def get_context_data(self, **kwargs):
        # Añade contadores para estadísticas
        context = super().get_context_data(**kwargs)
        context['prestamos_activos'] = Prestamo.objects.filter(devuelto=False).count()
        context['prestamos_devueltos'] = Prestamo.objects.filter(devuelto=True).count()
        return context

# Vista para que un usuario vea su historial personal de préstamos
# Muestra tanto préstamos activos como devueltos
class MiHistorialPrestamosView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'web/mi_historial_prestamos.html'
    context_object_name = 'prestamos'
    
    def get_queryset(self):
        # Filtrar préstamos por el usuario actual
        return Prestamo.objects.filter(usuario=self.request.user).order_by('-fecha_prestamo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir contadores personales
        context['prestamos_activos'] = Prestamo.objects.filter(
            usuario=self.request.user, 
            devuelto=False
        ).count()
        context['prestamos_devueltos'] = Prestamo.objects.filter(
            usuario=self.request.user,
            devuelto=True
        ).count()
        return context

# Vista para eliminar libros con verificaciones de seguridad
# Previene eliminación de libros con préstamos activos
class LibroDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_admin
    
    def get(self, request, pk):
        libro = get_object_or_404(Libro, pk=pk)
        # Verifica préstamos activos
        prestamos_activos = Prestamo.objects.filter(libro=libro, devuelto=False).exists()
        return render(request, 'web/libro_confirmar_eliminar.html', {
            'libro': libro,
            'prestamos_activos': prestamos_activos
        })
    
    def post(self, request, pk):
        libro = get_object_or_404(Libro, pk=pk)
        titulo = libro.titulo
        
        # Verifica nuevamente préstamos activos
        prestamos_activos = Prestamo.objects.filter(libro=libro, devuelto=False).exists()
        
        if prestamos_activos:
            messages.error(request, f"No se puede eliminar el libro '{titulo}' porque tiene préstamos activos. Espere a que los usuarios devuelvan todos los ejemplares.")
            return redirect('libros-lista')
        
        # Realiza la eliminación
        libro.delete()
        messages.success(request, f"Libro '{titulo}' eliminado exitosamente.")
        return redirect('libros-lista')

# Login personalizado con mejoras
# Facilita el acceso ignorando mayúsculas/minúsculas
class CustomLoginView(LoginView):
    template_name = 'web/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        # Normaliza el nombre de usuario
        username = form.cleaned_data.get('username')
        try:
            # Busca sin distinguir mayúsculas/minúsculas
            user = Usuario.objects.filter(username__iexact=username).first()
            if user:
                form.cleaned_data['username'] = user.username
        except:
            # Continúa con el comportamiento normal
            pass
        return super().form_valid(form)

# Vista de cierre de sesión con confirmación
# Evita cierres de sesión accidentales
class LogoutView(View):
    def get(self, request):
        return render(request, 'web/confirmar_logout.html')
    
    def post(self, request):
        logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect('home')

# Vista de registro con formulario personalizado
# Permite crear nuevas cuentas de usuario
class RegistroView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'web/registro.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Mensaje de confirmación
        messages.success(self.request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return response

# Vista para administrar usuarios (solo administradores)
# Permite ver todos los usuarios y cambiar sus roles
class AdministrarUsuariosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Usuario
    template_name = 'web/administrar_usuarios.html'
    context_object_name = 'usuarios'
    
    def test_func(self):
        # Limita acceso solo a administradores
        return self.request.user.is_admin
    
    def get_queryset(self):
        # Asegurarse de obtener la lista actualizada después de eliminar un usuario
        return Usuario.objects.all()
    
    def post(self, request):
        # Identificar la acción a realizar
        accion = request.POST.get('accion')
        usuario_id = request.POST.get('usuario_id')
        
        if not usuario_id:
            messages.error(request, "Usuario no especificado")
            return redirect('administrar-usuarios')
            
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            
            # Proteger contra acciones en el propio usuario
            if usuario.id == request.user.id:
                messages.error(request, "No puedes realizar esta acción sobre tu propio usuario")
                return redirect('administrar-usuarios')
                
            # Procesar cambio de rol
            if accion == 'cambiar_rol':
                nuevo_rol = request.POST.get('nuevo_rol')
                if nuevo_rol in dict(Usuario.ROLES).keys():
                    usuario.rol = nuevo_rol
                    usuario.save()
                    messages.success(request, f"Rol de usuario {usuario.username} actualizado a {dict(Usuario.ROLES)[nuevo_rol]}")
                    
            # Procesar eliminación de usuario
            elif accion == 'eliminar':
                # Verificar si el usuario tiene préstamos activos
                prestamos_activos = usuario.prestamo_set.filter(devuelto=False).exists()
                if prestamos_activos:
                    messages.error(request, f"No se puede eliminar al usuario {usuario.username} porque tiene préstamos activos")
                else:
                    nombre_usuario = usuario.username
                    usuario.delete()
                    messages.success(request, f"Usuario {nombre_usuario} eliminado correctamente")
                    
        except Usuario.DoesNotExist:
            # El usuario podría haber sido eliminado por otra sesión
            messages.warning(request, "El usuario ya no existe en el sistema")
        except Exception as e:
            # Capturar otros errores que puedan ocurrir
            messages.error(request, f"Error al procesar la acción: {str(e)}")
        
        # Redirigir siempre a la lista de usuarios después de cualquier acción
        return redirect('administrar-usuarios')

# Vista para eliminar usuarios con verificación de seguridad
# Previene eliminación de usuarios con préstamos activos
class UsuarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_admin
    
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Proteger contra eliminación del propio usuario
        if usuario.id == request.user.id:
            messages.error(request, "No puedes eliminar tu propio usuario")
            return redirect('administrar-usuarios')
            
        # Verificar préstamos activos
        prestamos_activos = usuario.prestamo_set.filter(devuelto=False).exists()
        return render(request, 'web/usuario_confirmar_eliminar.html', {
            'usuario': usuario,
            'prestamos_activos': prestamos_activos
        })
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Proteger contra eliminación del propio usuario
        if usuario.id == request.user.id:
            messages.error(request, "No puedes eliminar tu propio usuario")
            return redirect('administrar-usuarios')
            
        nombre_usuario = usuario.username
        
        # Verificar nuevamente préstamos activos
        prestamos_activos = usuario.prestamo_set.filter(devuelto=False).exists()
        
        if prestamos_activos:
            messages.error(request, f"No se puede eliminar al usuario '{nombre_usuario}' porque tiene préstamos activos. Espere a que devuelva todos los libros.")
            return redirect('administrar-usuarios')
        
        try:
            # Realizar la eliminación
            usuario.delete()
            messages.success(request, f"Usuario '{nombre_usuario}' eliminado exitosamente. Volviendo a la lista de usuarios.")
        except Exception as e:
            messages.error(request, f"Error al eliminar usuario: {str(e)}")
        
        from django.urls import reverse
        # Redirección explícita a la página de administrar usuarios
        return redirect('administrar-usuarios')