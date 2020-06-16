from django import forms

from .models import Busqueda, BusquedaLugar, Clase, Perfil, ClaseItem
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os

class BusquedaForm(forms.ModelForm):

    class Meta:
        model = Busqueda
#        fields = "__all__"
        fields = ('titulo_busqueda', 'descripcion', 'recompensa')

    def __init__(self, *args, **kwargs):
        super(BusquedaForm, self).__init__(*args, **kwargs)
        self.fields['titulo_busqueda'].widget.attrs.update({'class' : 'form-control'})
        self.fields['descripcion'].widget.attrs.update({'class' : 'form-control'})
        self.fields['recompensa'].widget.attrs.update({'class' : 'form-control'})
#        self.fields['inicio'].widget.attrs.update({'class' : 'form-control datepicker'})
#        self.fields['inicio'].widget.attrs.update({'data-value' : '2020-06-01'})
#        self.fields['fin'].widget.attrs.update({'class' : 'form-control datepicker'})
#        self.fields['fin'].widget.attrs.update({'data-value' : '2020-06-01'})
#        self.fields['duracion'].widget.attrs.update({'class' : 'form-control'})
#        self.fields['numero_personas'].widget.attrs.update({'class' : 'form-control','value' : '3'})

class BusquedaImagenForm(forms.ModelForm):

    class Meta:
        model = Busqueda
        fields = ('imagen',)

    def __init__(self, *args, **kwargs):
        super(BusquedaImagenForm, self).__init__(*args, **kwargs)
        self.fields['imagen'].widget.attrs.update({'class' : 'form-control'})

class BusquedaLugarForm(forms.ModelForm):

    class Meta:
        model = BusquedaLugar
#        fields = "__all__"
        fields = ('latitud','longitud')

    def __init__(self, *args, **kwargs):
        super(BusquedaLugarForm, self).__init__(*args, **kwargs)
#        self.fields['avatar'].widget.attrs.update({'class' : 'form-control'})
        self.fields['latitud'].widget.attrs.update({'class' : 'form-control'})
        self.fields['longitud'].widget.attrs.update({'class' : 'form-control'})
#        self.fields['avatar'].widget.attrs.update({'style' : 'display:none;'})
        self.fields['latitud'].widget.attrs.update({'style' : 'display:none;'})
        self.fields['longitud'].widget.attrs.update({'style' : 'display:none;'})

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = ''
        self.fields['first_name'].help_text = ''
        self.fields['last_name'].help_text = ''
        self.fields['email'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.fields['username'].label = 'Usuario'
        self.fields['first_name'].label = 'Nombre'
        self.fields['last_name'].label = 'Apellido'
        self.fields['email'].label = 'Correo'
        self.fields['password1'].label = 'Contraseña'
        self.fields['password2'].label = 'Confirma Contraseña'
        self.fields['username'].widget.attrs.update({'class' : 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class' : 'form-control'})
        self.fields['email'].widget.attrs.update({'class' : 'form-control'})
        self.fields['password1'].widget.attrs.update({'class' : 'form-control'})
        self.fields['password2'].widget.attrs.update({'class' : 'form-control'})

class ClaseForm(forms.ModelForm):

    class Meta:
        model = Clase
        fields = ('titulo', 'avatar','bandera_marcador')

    def __init__(self, *args, **kwargs):
        super(ClaseForm, self).__init__(*args, **kwargs)
        self.fields['titulo'].widget.attrs.update({'class' : 'form-control'})
        self.fields['avatar'].widget.attrs.update({'class' : 'form-control'})
        self.fields['bandera_marcador'].label = '¿Usar marcador?'
        self.fields['bandera_marcador'].widget.attrs.update({'class' : 'form-control'})

class PerfilForm(forms.ModelForm):

    class Meta:
        model = Perfil
        fields = ('imagen_busqueda', 'avatar',)

    def __init__(self, *args, **kwargs):
        super(PerfilForm, self).__init__(*args, **kwargs)
        self.fields['imagen_busqueda'].widget.attrs.update({'class' : 'form-control'})
        self.fields['avatar'].widget.attrs.update({'class' : 'form-control'})

class SonidoForm(forms.ModelForm):

    class Meta:
        model = BusquedaLugar
        fields = ('sonido',)
# Agregar validación
    def clean_audio_file(self):
        file = self.cleaned_data.get('sonido')
        if file:
            if file._size > 4*1024*1024:
                raise ValidationError("El tamaño del archivo es muy grande ( > 1.5Mb )")
            if not file.content-type in ["audio/mpeg","audio/..."]:
                raise ValidationError("Content-Type is not mpeg")
            if not os.path.splitext(file.name)[1] in [".mp3",".wav",".ogg"]:
                raise ValidationError("No tiene la extensión")
            return file
        else:
            raise ValidationError("No fue posible subir el archivo")

class ItemClaseForm(forms.ModelForm):

    class Meta:
        model = ClaseItem
        fields = ('avatar',)

    def __init__(self, *args, **kwargs):
        super(ItemClaseForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].widget.attrs.update({'class' : 'form-control'})

class ClaseImagenForm(forms.ModelForm):

    class Meta:
        model = Busqueda
        fields = ('imagen',)

    def __init__(self, *args, **kwargs):
        super(ClaseImagenForm, self).__init__(*args, **kwargs)
        self.fields['imagen'].widget.attrs.update({'class' : 'form-control'})