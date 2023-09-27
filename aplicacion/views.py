from typing import Any
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib import messages
from .forms import RegistroForm, LoginForm, ProductForm
from .models import Usuarios, Productos
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import ListView,CreateView, UpdateView, DeleteView,TemplateView,DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy

# Create your views here.

class Login(LoginView):
    template_name = "login.html"
    form_class = LoginForm
    redirect_authenticated_user=True

class Inicio(TemplateView):
    template_name = "inicio.html"

class Registro(CreateView):
    template_name = "registro.html"
    form_class = RegistroForm
    def post(self, request):
        form_registro = self.form_class(request.POST or None)
        if form_registro.is_valid():
            create_user = Usuarios.create_user(form_registro)
 
            if create_user:
                messages.success(request,"Usuario creado correctamente")
                return redirect('registro')
            else:
                return redirect('registro')
        else:
            return render(request,'registro.html', {'form': form_registro})

class Loguut(LogoutView):
    next_page ="inicio"
    

class Vista_Productos(ListView):
    template_name = "productos.html"
    model = Productos
    context_object_name = "productos"
    queryset = Productos.objects.all()
    

class DetalleProducto(DetailView):
    template_name = "producto_detalle.html"
    model = Productos
    context_object_name = "producto"
        
class Buscar_Productos(ListView):
    template_name = "resultados.html"
    model = Productos
    context_object_name = "productos"
    def get_queryset(self):
        if self.request.GET.get('buscar'):
            consulta = self.request.GET.get('buscar')
            queryset = Productos.objects.filter(Q(producto_nombre__icontains=consulta) | Q(categoria__categoria_nombre__icontains=consulta))
            return queryset

class Administrar_Productos(PermissionRequiredMixin,ListView):
    permission_required = 'aplicacion.view_productos'
    template_name = "administrar_productos.html"
    model = Productos
    context_object_name = "productos"
    queryset = Productos.objects.all()
    paginate_by = 10

class Crear_Producto(PermissionRequiredMixin,CreateView):
    permission_required = 'aplicacion.add_productos'
    template_name = "add_productos.html"
    model = Productos
    form_class = ProductForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            mensaje = "Producto agregado correctamente"
            producto = f"Producto {form.cleaned_data.get('producto_nombre')}"
            response = JsonResponse({'mensaje':mensaje,'producto':producto})
            response.status_code = 201
            return response
        else:
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response

class Actualizar_Producto(PermissionRequiredMixin,UpdateView):
    permission_required = 'aplicacion.change_productos'
    template_name = "update_productos.html"
    model = Productos
    form_class = ProductForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST,request.FILES, instance = self.get_object())
        if form.is_valid():
            form.save()
            mensaje = "Producto editado correctamente"
            producto = f"Producto {form.cleaned_data.get('producto_nombre')}"
            response = JsonResponse({'mensaje':mensaje,'producto':producto})
            response.status_code = 201
            return response
        else:
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response
class EliminarProducto(PermissionRequiredMixin,DeleteView):
    permission_required = 'aplicacion.delete_productos'
    template_name = "delete_producto.html"
    model = Productos
    success_url = reverse_lazy('administrar_productos')


