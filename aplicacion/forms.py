from collections.abc import Mapping
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import Usuarios, Productos, Categorias

string_valid = RegexValidator(regex="^(?=.*[A-Z])(?=.*[a-z])(?=.*[\d])[\w]{4,20}$")
 
class RegistroForm(UserCreationForm):
    class Meta:
        model = Usuarios
        fields = ['usuario','password1','password2','nombre','apellido','email']
   
class LoginForm(AuthenticationForm):
    class Meta:
        model = Usuarios
        fields = ['usuario', 'password']

class ProductForm(forms.ModelForm):
    categoria = forms.ModelChoiceField( queryset = Categorias.objects.all(),empty_label="Categoria",widget=forms.Select(attrs={"class": "form-select"}))
    imagen = forms.FileField(widget=forms.ClearableFileInput(attrs={"class": "form-control"}))
    producto_nombre = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Nombre producto'}))
    precio_unitario = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Precio unitario'}))
    descripcion = forms.CharField(widget=forms.Textarea(attrs={"class": "form-control","rows":5,"cols":5,'placeholder':'Descripcion'}),label="Descripcion")
    unidades_stock = forms.CharField(widget=forms.TextInput(attrs={"class": "form-control",'placeholder':'Unidades'}))

    class Meta:
        model = Productos
        fields = '__all__'
        exclude = ['slug']

