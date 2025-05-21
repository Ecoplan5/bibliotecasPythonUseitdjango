from django.apps import AppConfig
from django.db.models.signals import post_migrate


class GestionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gestion'

    def ready(self):
        # Importar aquí para evitar importación circular
        from django.contrib.auth import get_user_model
        
        # Registrar la señal para crear el superusuario después de las migraciones
        post_migrate.connect(self.crear_superusuario, sender=self)
    
    def crear_superusuario(self, **kwargs):
        """
        Crea un superusuario predeterminado si no existe.
        Este usuario tendrá los privilegios máximos en el sistema.
        """
        Usuario = kwargs.get('apps').get_model('gestion', 'Usuario')
        
        # Verifica si ya existe un superusuario
        if not Usuario.objects.filter(username='SuperAdmin').exists():
            print('Creando superusuario predeterminado (SuperAdmin)...')
            
            # Crear el superusuario
            Usuario.objects.create_superuser(
                username='SuperAdmin',
                password='admin1234',  # Contraseña inicial
                email='admin@biblioteca.com',
                first_name='Super',
                last_name='Admin',
                rol='admin'
            )
            print('¡Superusuario creado exitosamente!')
        else:
            print('El superusuario ya existe, no es necesario crearlo.')
