from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm,PasswordChangeForm
from django.core.validators import RegexValidator
from .models import Usuario, Producto, ProductoCategoria,ProductoMarca
from django.contrib.auth.models import Group

string_valid = RegexValidator(regex="^(?=.*[A-Z])(?=.*[a-z])(?=.*[\d])[\w]{4,20}$")
tarjeta_valid = RegexValidator(regex="^\d{15,16}$",message="Longitud minima 15/maxima 16",code="")
tarjeta_codigo_valid = RegexValidator(regex="^\d{3,4}$",message="Longitud minima 3/maxima 4",code="")
tarjeta_fecha_valid = RegexValidator(regex="^\d{4,4}$",message="Longitud minima 4/maxima 4",code="")
dni_valid = RegexValidator(regex="^\d{1,8}$",message="Longitud minima 1/maxima 8",code="")
 
class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['usuario','password1','password2','nombre','apellido','email']

class CrearUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['usuario','password1','password2','nombre','apellido','email','groups']
        widgets = {
            'groups': forms.SelectMultiple(attrs={"class": "form-select"})
        }

class EditarUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['usuario','nombre','apellido','email','groups']
        widgets = {
            'groups': forms.SelectMultiple(attrs={"class": "form-select"})
        }

class EditarPerfilForm(forms.ModelForm):
    usuario = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre de usuario'}))
    nombre = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre de usuario'}))
    apellido = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre de usuario'}))
    email = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre de usuario'}))
    class Meta:
        model = Usuario
        fields = ['usuario','nombre','apellido','email']
        exclude = ['password1','password2']
        
class LoginForm(AuthenticationForm):
    class Meta:
        model = Usuario
        fields = ['usuario', 'password']

class ProductForm(forms.ModelForm):
    categoria = forms.ModelChoiceField(queryset = ProductoCategoria.objects.all(),empty_label="Categoria",widget=forms.Select(attrs={"class": "form-select"}))
    marca = forms.ModelChoiceField(queryset = ProductoMarca.objects.all(),empty_label="Marca",widget=forms.Select(attrs={"class": "form-select"}))
    imagen = forms.FileField(widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    producto_nombre = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre producto'}))
    precio_unitario = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Precio unitario'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control","rows":5,"cols":5,'placeholder':'Descripcion'}),label="Descripcion")
    unidades_stock = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Unidades'}))

    class Meta:
        model = Producto
        fields = '__all__'
        
class CategoriaForm(forms.ModelForm):
    categoria_nombre  = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre de categoria'}))
    categoria_descripcion = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control","rows":2,"cols":2,'placeholder':'Descripcion de categoria'}))

    class Meta:
        model = ProductoCategoria
        fields = '__all__'

class MarcaForm(forms.ModelForm): 
    marca_nombre  = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre de marca'}))
    marca_descripcion = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control","rows":2,"cols":2,'placeholder':'Descripcion de marca'}))

    class Meta:
        model = ProductoMarca
        fields = '__all__'

class PagoForm(forms.Form):
    tarjeta_titular = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre del titular'}))
    dni = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'12345678',"maxlength": 8}),validators=[dni_valid])
    tarjeta_numero = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'1234 1234 1234 1234',"maxlength": 19}),validators=[tarjeta_valid])
    tarjeta_codigo = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'123',"maxlength": 4}),validators=[tarjeta_codigo_valid])
    tarjeta_fecha = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'MM/AA',"maxlength": 5}),validators=[tarjeta_fecha_valid])
