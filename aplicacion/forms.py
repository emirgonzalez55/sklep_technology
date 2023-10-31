from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import Usuario, Producto, ProductoCategoria,ProductoMarca

string_valid = RegexValidator(regex="^(?=.*[A-Z])(?=.*[a-z])(?=.*[\d])[\w]{4,20}$")
tarjeta_valid = RegexValidator(regex="^\d{15,16}$",message="Longitud minima 15/maxima 16",code="")
tarjeta_codigo_valid = RegexValidator(regex="^\d{3,4}$",message="Longitud minima 3/maxima 4",code="")
tarjeta_fecha_valid = RegexValidator(regex="^\d{4,4}$",message="Longitud minima 4/maxima 4",code="")
 
class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['usuario','password1','password2','nombre','apellido','email']
   
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

class PagoForm(forms.Form):
    tarjeta_titular = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre del titular'}))
    tarjeta_numero = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'**** **** **** ****'}),validators=[tarjeta_valid])
    tarjeta_codigo = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'****'}),validators=[tarjeta_codigo_valid])
    tarjeta_fecha = forms.IntegerField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'mm/aa'}),validators=[tarjeta_fecha_valid])
