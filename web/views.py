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
# Esta vista muestra la lista de todos los libros disponibles en la biblioteca.
class LibroListView(ListView):
    model = Libro  # Modelo que se va a utilizar
    template_name = 'web/libros_lista.html'  # Plantilla HTML
    context_object_name = 'libros'  # Variable en el template
    
    def get_queryset(self):
        # Implementé un buscador que filtra por título o autor, muy útil
        # cuando tenemos muchos libros y el usuario necesita encontrar uno específico
        query = self.request.GET.get('buscar', '')
        if query:
            return Libro.objects.filter(
                Q(titulo__icontains=query) | 
                Q(autor__icontains=query)
            )
        return Libro.objects.all()
    
    def get_context_data(self, **kwargs):
        # Aquí envío el término de búsqueda al template para mantener
        # el valor en la caja de búsqueda después de filtrar
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
        
        # Cuento los préstamos activos para mostrar disponibilidad real
        # Esto es importante para que el usuario sepa si puede pedir el libro
        prestamos_activos = Prestamo.objects.filter(libro=libro, devuelto=False).count()
        context['prestamos_activos'] = prestamos_activos
        
        return context

# En esta vista los administradores pueden crear nuevos libros
# Verifica permisos de administrador antes de permitir el acceso
class LibroCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Libro
    fields = ['titulo', 'autor', 'año_publicacion', 'cantidad_stock']
    template_name = 'web/libro_formularios.html'
    success_url = reverse_lazy('libros-lista')

    def test_func(self):
        # Verifico si el usuario es administrador para evitar accesos no autorizados
        # Esta función la uso en varias vistas para restringir acciones administrativas
        return self.request.user.is_admin
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Mensaje de confirmación para mejorar la experiencia de usuario
        # Me gusta mantener informado al usuario sobre el resultado de sus acciones
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
        # Accedo directamente a los libros prestados del usuario a través de la relación ManyToMany
        # Esto simplifica mucho el código y aprovecha bien las relaciones del modelo
        return self.request.user.libros_prestados.all()

# Vista para gestionar el préstamo de un libro
# Incluye validaciones de disponibilidad y estado
class PrestamoCreateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        libro = get_object_or_404(Libro, pk=pk)
        usuario = request.user
        
        # Verifico la disponibilidad de ejemplares antes de procesar el préstamo
        # Esto evita problemas de inventario negativo
        if libro.cantidad_stock <= 0:
            messages.error(request, "No hay ejemplares disponibles de este libro.")
            return redirect('libros-detalles', pk=pk)
        
        # Evito préstamos duplicados para el mismo usuario
        # Un control importante para mantener la integridad de los datos
        if libro in usuario.libros_prestados.all():
            messages.warning(request, "Ya tienes este libro prestado.")
            return redirect('libros-detalles', pk=pk)
        
        # Realizo el préstamo y actualizo el inventario
        # Esta operación debe ser atómica para mantener la consistencia
        usuario.libros_prestados.add(libro)
        libro.cantidad_stock -= 1
        libro.save()
        
        # Registro en el historial para tener trazabilidad
        # Este registro es crucial para auditorías y estadísticas
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
        
        # Verifico que el usuario tenga efectivamente el libro
        # Esta validación es importante para evitar inconsistencias
        if libro not in usuario.libros_prestados.all():
            messages.error(request, "No tienes este libro prestado.")
            return redirect('prestamos-listas')
        
        # Proceso la devolución actualizando la relación y el inventario
        # Es importante mantener sincronizados estos dos estados
        usuario.libros_prestados.remove(libro)
        libro.cantidad_stock += 1
        libro.save()
        
        # Actualizo el registro histórico para completar el ciclo del préstamo
        # Usamos first() porque solo debería haber un préstamo activo por libro y usuario
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
        # Limito acceso solo a administradores para proteger la información
        # Este tipo de datos es sensible y requiere control de acceso
        return self.request.user.is_admin
    
    def get_context_data(self, **kwargs):
        # Añado contadores para estadísticas que ayudan en la toma de decisiones
        # Me gusta tener métricas a simple vista en el panel de administración
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
        # Filtro préstamos por el usuario actual para mostrar solo su actividad
        # Ordenados por fecha para ver primero los más recientes
        return Prestamo.objects.filter(usuario=self.request.user).order_by('-fecha_prestamo')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añado contadores personales para que el usuario vea su actividad de un vistazo
        # Esto mejora significativamente la experiencia de usuario
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
        # Verifico préstamos activos para evitar eliminaciones que generen inconsistencias
        # Esta verificación es crucial para mantener la integridad referencial
        prestamos_activos = Prestamo.objects.filter(libro=libro, devuelto=False).exists()
        return render(request, 'web/libro_confirmar_eliminar.html', {
            'libro': libro,
            'prestamos_activos': prestamos_activos
        })
    
    def post(self, request, pk):
        libro = get_object_or_404(Libro, pk=pk)
        titulo = libro.titulo
        
        # Verifico nuevamente préstamos activos por seguridad
        # Esta doble verificación evita race conditions en entornos concurrentes
        prestamos_activos = Prestamo.objects.filter(libro=libro, devuelto=False).exists()
        
        if prestamos_activos:
            messages.error(request, f"No se puede eliminar el libro '{titulo}' porque tiene préstamos activos. Espere a que los usuarios devuelvan todos los ejemplares.")
            return redirect('libros-lista')
        
        # Realizo la eliminación solo si es seguro hacerlo
        libro.delete()
        messages.success(request, f"Libro '{titulo}' eliminado exitosamente.")
        return redirect('libros-lista')

# Login personalizado con mejoras para mayor usabilidad
# Facilita el acceso ignorando mayúsculas/minúsculas en el nombre de usuario
class CustomLoginView(LoginView):
    template_name = 'web/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        # Normalizo el nombre de usuario para ser más flexible con los usuarios
        # Esto mejora la experiencia al no rechazar logins por errores de capitalización
        username = form.cleaned_data.get('username')
        try:
            # Busco el usuario sin distinguir mayúsculas/minúsculas
            # Esta pequeña mejora reduce frustración en usuarios
            user = Usuario.objects.filter(username__iexact=username).first()
            if user:
                form.cleaned_data['username'] = user.username
        except:
            # Continúo con el comportamiento normal si hay algún problema
            pass
        return super().form_valid(form)

# Vista de cierre de sesión con confirmación
# Evita cierres de sesión accidentales mejorando la experiencia
class LogoutView(View):
    def get(self, request):
        # Muestro una página de confirmación para evitar cierres accidentales
        # Especialmente útil cuando el botón está cerca de otras opciones
        return render(request, 'web/confirmar_logout.html')
    
    def post(self, request):
        # Proceso el cierre de sesión efectivo solo cuando el usuario confirma
        logout(request)
        messages.success(request, "Has cerrado sesión correctamente.")
        return redirect('home')

# Vista de registro con formulario personalizado
# Permite crear nuevas cuentas de usuario con validaciones específicas
class RegistroView(CreateView):
    form_class = RegistroUsuarioForm
    template_name = 'web/registro.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Mensaje de confirmación para guiar al usuario al siguiente paso
        # Estas indicaciones claras mejoran mucho la experiencia de usuario
        messages.success(self.request, "Registro exitoso. Ahora puedes iniciar sesión.")
        return response

# Vista para administrar usuarios (solo administradores)
# Permite ver todos los usuarios y cambiar sus roles
class AdministrarUsuariosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Usuario
    template_name = 'web/administrar_usuarios.html'
    context_object_name = 'usuarios'
    
    def test_func(self):
        # Limito acceso solo a administradores para proteger datos sensibles
        # Esta es una vista crítica para la seguridad del sistema
        return self.request.user.is_admin
    
    def get_queryset(self):
        # Me aseguro de obtener la lista actualizada después de eliminar un usuario
        # Esto evita mostrar datos obsoletos después de cambios
        return Usuario.objects.all()
    
    def post(self, request):
        # Identifico la acción a realizar según los parámetros del formulario
        # Este método maneja múltiples acciones en una sola vista para simplificar
        accion = request.POST.get('accion')
        usuario_id = request.POST.get('usuario_id')
        
        if not usuario_id:
            messages.error(request, "Usuario no especificado")
            return redirect('administrar-usuarios')
            
        try:
            usuario = Usuario.objects.get(pk=usuario_id)
            
            # Protejo contra acciones en el propio usuario administrador
            # Es una medida de seguridad para evitar que un admin se quite permisos
            if usuario.id == request.user.id:
                messages.error(request, "No puedes realizar esta acción sobre tu propio usuario")
                return redirect('administrar-usuarios')
                
            # Proceso cambio de rol si esa es la acción solicitada
            # Esto permite promover o degradar usuarios según necesidades
            if accion == 'cambiar_rol':
                nuevo_rol = request.POST.get('nuevo_rol')
                if nuevo_rol in dict(Usuario.ROLES).keys():
                    usuario.rol = nuevo_rol
                    usuario.save()
                    messages.success(request, f"Rol de usuario {usuario.username} actualizado a {dict(Usuario.ROLES)[nuevo_rol]}")
                    
            # Proceso eliminación de usuario con verificaciones de seguridad
            # Compruebo que no tenga préstamos activos para evitar inconsistencias
            elif accion == 'eliminar':
                # Verifico si el usuario tiene préstamos activos
                prestamos_activos = usuario.prestamo_set.filter(devuelto=False).exists()
                if prestamos_activos:
                    messages.error(request, f"No se puede eliminar al usuario {usuario.username} porque tiene préstamos activos")
                else:
                    nombre_usuario = usuario.username
                    usuario.delete()
                    messages.success(request, f"Usuario {nombre_usuario} eliminado correctamente")
                    
        except Usuario.DoesNotExist:
            # El usuario podría haber sido eliminado por otra sesión, manejo este caso
            # Esta verificación es importante en entornos multi-usuario
            messages.warning(request, "El usuario ya no existe en el sistema")
        except Exception as e:
            # Capturo otros errores que puedan ocurrir para evitar pantallas de error
            # Prefiero mostrar un mensaje claro que una página de error genérica
            messages.error(request, f"Error al procesar la acción: {str(e)}")
        
        # Redirijo siempre a la lista de usuarios después de cualquier acción
        # Esto mantiene una navegación consistente y predecible
        return redirect('administrar-usuarios')

# Vista para eliminar usuarios con verificación de seguridad
# Previene eliminación de usuarios con préstamos activos
class UsuarioDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_admin
    
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Protejo contra eliminación del propio usuario administrador
        # Esto evita que un admin se elimine a sí mismo por error
        if usuario.id == request.user.id:
            messages.error(request, "No puedes eliminar tu propio usuario")
            return redirect('administrar-usuarios')
            
        # Verifico préstamos activos para evitar problemas de integridad
        # No permito eliminar usuarios con préstamos pendientes
        prestamos_activos = usuario.prestamo_set.filter(devuelto=False).exists()
        return render(request, 'web/usuario_confirmar_eliminar.html', {
            'usuario': usuario,
            'prestamos_activos': prestamos_activos
        })
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        
        # Protejo nuevamente contra eliminación del propio usuario
        # Esta doble verificación es importante para la seguridad
        if usuario.id == request.user.id:
            messages.error(request, "No puedes eliminar tu propio usuario")
            return redirect('administrar-usuarios')
            
        nombre_usuario = usuario.username
        
        # Verifico nuevamente préstamos activos por seguridad
        # Esta doble verificación evita race conditions
        prestamos_activos = usuario.prestamo_set.filter(devuelto=False).exists()
        
        if prestamos_activos:
            messages.error(request, f"No se puede eliminar al usuario '{nombre_usuario}' porque tiene préstamos activos. Espere a que devuelva todos los libros.")
            return redirect('administrar-usuarios')
        
        try:
            # Realizo la eliminación solo si es seguro hacerlo
            usuario.delete()
            messages.success(request, f"Usuario '{nombre_usuario}' eliminado exitosamente. Volviendo a la lista de usuarios.")
        except Exception as e:
            messages.error(request, f"Error al eliminar usuario: {str(e)}")
        
        from django.urls import reverse
        # Redirección explícita a la página de administrar usuarios
        return redirect('administrar-usuarios')