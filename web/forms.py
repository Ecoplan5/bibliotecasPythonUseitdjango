from django import forms
from django.contrib.auth.forms import UserCreationForm
from gestion.models import Usuario
from django.core.exceptions import ValidationError

class RegistroUsuarioForm(UserCreationForm):
    # Añadí el email como campo obligatorio para asegurar que tenemos
    # forma de contactar con todos los usuarios cuando sea necesario
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalicé los mensajes de ayuda para que sean más amigables
        # y en español, mejorando la experiencia de usuario de la web
        self.fields['password1'].help_text = "La contraseña debe tener entre 4 y 10 caracteres."
        self.fields['username'].help_text = "Puede usar cualquier combinación de letras y números."
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        # Añadí una validación específica de longitud máxima para evitar
        # contraseñas demasiado largas que podrían ser difíciles de recordar
        if len(password) > 10:
            raise ValidationError("La contraseña no puede tener más de 10 caracteres.")
        return password
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Asigno el rol regular por defecto para mantener un nivel de
        # seguridad básico. Los administradores los creo manualmente
        user.rol = 'regular'  # Asignar rol regular automáticamente
        if commit:
            user.save()
        return user 