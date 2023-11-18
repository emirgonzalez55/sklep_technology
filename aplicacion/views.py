from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse,Http404
from django.contrib import messages
from aplicacion.forms import RegistroForm, LoginForm, ProductForm,PagoForm
from aplicacion.models import Usuario, Producto,Tarjeta,Pedido,CarritoCompra,Mercado,ProductoCategoria,ProductoMarca
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import ListView,CreateView, UpdateView, DeleteView,TemplateView,DetailView,View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy

# Create your views here.

class LoginVista(LoginView):
    template_name = "login.html"
    form_class = LoginForm
    redirect_authenticated_user=True

class InicioVista(TemplateView):
    template_name = "inicio.html"

class RegistroVista(CreateView):
    template_name = "registro.html"
    form_class = RegistroForm
    def post(self, request):
        form_registro = self.form_class(request.POST or None)
        if form_registro.is_valid():
            crear_usuario = Usuario.crear_usuario(form_registro)
 
            if crear_usuario:
                messages.success(request,"Usuario creado correctamente")
                return redirect('registro')
            else:
                return redirect('registro')
        else:
            return render(request,'registro.html', {'form': form_registro})

class LoguutVista(LogoutView):
    next_page ="inicio"

class ProductosVista(ListView):
    template_name = "productos.html"
    model = Producto
    context_object_name = "productos"
    queryset = Producto.objects.all()
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.kwargs:
            filtro = self.kwargs["filtro"]
            valor = self.kwargs["valor"]

            if filtro == "categoria":
                queryset = queryset.filter(categoria__slug=valor)
            if filtro == "marca":
                queryset = queryset.filter(marca__slug=valor)

        return queryset
    
class DetalleProductoVista(DetailView):
    template_name = "producto_detalle.html"
    model = Producto
    context_object_name = "producto"
    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs) 
        if context["producto"].unidades_stock:
            context["cantidad_select"] = range(1, context["producto"].unidades_stock + 1)
            
        return context
  
class BuscarProductosVista(ListView):
    template_name = "resultados.html"
    context_object_name = "productos"
    def get_queryset(self):
        if self.request.GET.get('buscar'):
            consulta = self.request.GET.get('buscar')
            categoria = self.request.GET.get('categoria')
            marca = self.request.GET.get('marca')
            precio_min = self.request.GET.get('precio_min')
            precio_max = self.request.GET.get('precio_max')
            precio_rango = None
            # if precio_min and precio_max:
            #     precio_rango = tuple(sorted((precio_min, precio_max)))
            #     print(tuple(sorted((precio_min, precio_max))))
            #     precio_min = None
            #     precio_max = None

            queryset = Producto.buscar_productos(producto_nombre__icontains=consulta,categoria__categoria_nombre=categoria,marca__marca_nombre=marca,precio_unitario__range=precio_rango,precio_unitario__gte=precio_min,precio_unitario__lte=precio_max)
            queryset.consulta = consulta
            queryset.categoria = categoria
            queryset.marca = marca
            queryset.precio_min = precio_min
            queryset.precio_max = precio_max
            # queryset.precio_rango = precio_rango
            return queryset

class AdministrarProductosVista(PermissionRequiredMixin,ListView):
    permission_required = 'aplicacion.view_producto'
    template_name = "administrar_productos.html"
    model = Producto
    context_object_name = "productos"
    queryset = Producto.objects.all()
    paginate_by = 10

class CrearProductoVista(PermissionRequiredMixin,CreateView):
    permission_required = 'aplicacion.add_producto'
    template_name = "add_productos.html"
    model = Producto
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

class ActualizarProductoVista(PermissionRequiredMixin,UpdateView):
    permission_required = 'aplicacion.change_producto'
    template_name = "update_productos.html"
    model = Producto
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
class EliminarProductoVista(PermissionRequiredMixin,DeleteView):
    permission_required = 'aplicacion.delete_productos'
    template_name = "delete_producto.html"
    model = Producto
    success_url = reverse_lazy('administrar_productos')


class ComprarVista(View):
    def get(self, request,producto_slug,cantidad):
        form = PagoForm
        producto = Producto.obtener_producto(slug=producto_slug)
        if producto and cantidad:
            # comprobar_stock = Producto.comprobar_stock(producto.id_producto, cantidad)
            usuario = request.user.id_usuario
            preference_mercadopago = Mercado.generar_preference_mercadopago(usuario, producto=producto,cantidad=cantidad)
            total = producto.precio_unitario * cantidad
        
            return render(request,'comprar.html', {'preference': preference_mercadopago[0],'public_token': preference_mercadopago[1], 'producto': producto,'cantidad': cantidad,'total': total,'form': form})
        

        raise Http404("Producto no encontrado")

    def post(self, request,producto_slug,cantidad):
        producto = Producto.obtener_producto(slug=producto_slug)
        form = PagoForm(request.POST or None)
        if form.is_valid():
            check_tarjeta = Tarjeta.check_tarjeta(form)
            if check_tarjeta:
                print("Tarjeta válida")
                comprobar_stock = Producto.comprobar_stock(producto.id_producto, cantidad)
                if comprobar_stock:
                    print("Hay stock disponible")
                    crear_pedido = Pedido.crear_pedido(request, producto, cantidad)
                    if crear_pedido:
                            print("Pedido creado correctamente")
                    else:
                        print("Error al procesar pedido")
                else: 
                    print("No hay stock disponible")
            else:
                print("Tarjeta inválida")    

        return render(request,'comprar.html', {'producto': producto,'cantidad': cantidad,'form': form})

class ComprarCarritoVista(View):


    def get(self, request):
        usuario = request.user.id_usuario
        form = PagoForm
        obtener_carrito = CarritoCompra.obtener_carrito(usuario)
        carrito = obtener_carrito[0]
        productos_lista = Pedido.procesar_lista_productos(carrito)
        total = obtener_carrito[1]
        preference_mercadopago = Mercado.generar_preference_mercadopago(usuario, carrito=carrito)
        return render(request,'comprar.html', {'preference': preference_mercadopago[0],'public_token': preference_mercadopago[1],'carrito_compra': carrito,'total': total,'form': form, 'productos_lista':productos_lista})
    
    def post(self, request):
        parametro_productos = request.POST.get("productos")
        productos_lista = Pedido.procesar_parametro(parametro_productos)
        productos = Producto.obtener_producto(productos_lista=productos_lista)
        productos1 = Producto.obtener_producto(slug="amd-ryzen-5-5950x")
        # productos2 = Producto.obtener_producto(id_producto=1)
        print("obtener_producto", productos)
        print("obtener_producto", productos1)
        # print("obtener_producto", productos2)
        # comprobar_stock = Producto.comprobar_stock(productos=productos)
        # comprobar_stock1 = Producto.comprobar_stock(producto=1, cantidad=1)
        # actualizar_stock = Producto.actualizar_stock(producto=1, cantidad=1)
        # print("actualizar_stock",actualizar_stock)
        # actualizar_stock_v2 = Producto.actualizar_stock(productos=productos)
        # print("actualizar_stockv2",actualizar_stock_v2)


        # # print("parametro_productos",parametro_productos)
        # # print("productos_lista",productos_lista)
        # # print("productos",productos)
        # return redirect('/comprar/carrito')
        return render(request,'comprar.html')


class ComprarMercadoPagoVista(View):
    def post(self, request, usuario):
        print("Este es el usuario recivido",usuario)
        if request.GET.get("type") and request.GET.get("data.id"):
            type = request.GET.get("type")
            data_id = request.GET.get("data.id")
            Mercado.procesar_respuesta_mp(type,data_id)

        return HttpResponse(status=200)
    
class AgregarCarritoVista(CreateView):
    def post(self, request, producto, cantidad):
        comprobar_carrito_usuario = CarritoCompra.comprobar_carrito_usuario(request, producto)
        if comprobar_carrito_usuario:
            agregar_carrito = CarritoCompra.agregar_carrito(request, producto, cantidad)
            response = JsonResponse({'response':'response'})
            response.status_code = 201
            return response
        else:
            error = "error"
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response

class ActualizarCarritoVista(UpdateView):

    def post(self, request, producto, cantidad):
        actualizar_cantidad = CarritoCompra.actualizar_cantidad_producto_carrito(request, producto, cantidad)
        if actualizar_cantidad:
            response = JsonResponse({'response':'response'})
            response.status_code = 201
            return response
        else:
            response = JsonResponse({'error':'error'})
            response.status_code = 400
            return response

class EliminarCarritoVista(DeleteView):
    def post(self, request, producto):
        eliminar_producto_carrito = CarritoCompra.eliminar_producto_carrito(request, producto)
        response = JsonResponse({'response':'response'})
        response.status_code = 201
        return response

class CarritoVista(ListView):
    template_name = "carrito.html"
    context_object_name = "carrito_productos"
    # paginate_by = 10
    def get_queryset(self):
        usuario = self.request.user.id_usuario
        carrito = CarritoCompra.obtener_carrito(usuario=usuario)
        queryset = carrito[0]
        queryset.total = carrito[1]

        return queryset
