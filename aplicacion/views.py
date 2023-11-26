from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse,Http404
from django.contrib import messages
from aplicacion.forms import RegistroForm, LoginForm, ProductForm,PagoForm
from aplicacion.models import Usuario, Producto,Tarjeta,Pedido,CarritoCompra,Mercado,ProductoCategoria,ProductoMarca,PedidoPreferencia
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


class ComprarMetodoPagoVista(View):
    def get(self, request,producto_slug,cantidad):
        producto = Producto.obtener_producto(slug=producto_slug)
        if producto and cantidad:
            form = PagoForm
            preferencia = PedidoPreferencia.crear_preferencia(request,producto=producto,cantidad=cantidad)
            preference_mercadopago = Mercado.generar_preference_mercadopago(request, producto=producto,cantidad=cantidad)
            total = producto.precio_unitario * cantidad
            return render(request,'comprar_pago.html', {'preferencia': preferencia,'preference': preference_mercadopago[0],'public_token': preference_mercadopago[1], 'producto': producto,'cantidad': cantidad,'total': total,'form': form})
        
        raise Http404("Producto no encontrado")

    def post(self, request,producto_slug,cantidad):
        producto = Producto.obtener_producto(slug=producto_slug)
        form = PagoForm(request.POST or None)
        id_preferencia = request.POST.get("preferencia-id")
        if form.is_valid():
            check_tarjeta = Tarjeta.check_tarjeta(form)
            if check_tarjeta:
                actulizar_preferencia = PedidoPreferencia.actulizar_preferencia(request,id_preferencia,tarjeta=check_tarjeta)
                print("Tarjeta válida")
                if actulizar_preferencia:
                    if check_tarjeta.tipo == "credito":
                        print(check_tarjeta.tipo)
                        url = f"/comprar/pago/cuotas/preferencia-id={id_preferencia}"
                        response = JsonResponse({'url': url})
                        response.status_code = 201
                        return response
                    if check_tarjeta.tipo == "debito":
                        pass
            else:
                print("Tarjeta inválida")  
                # comprobar_stock = Producto.comprobar_stock(producto=producto, cantidad=cantidad)
                # if comprobar_stock:
                #     print("Hay stock disponible")
                #     crear_pedido = Pedido.crear_pedido(request, producto=producto, cantidad=cantidad)
                #     if crear_pedido:
                #         print("Pedido creado correctamente")
                #         response = JsonResponse({'response':"response"})
                #         response.status_code = 201
                #         return response
                #     else:
                #         print("Error al procesar pedido")
                # else: 
                #     print("No hay stock disponible")
                #     response = JsonResponse({'response':"response"})
                #     response.status_code = 404
                #     return response
  

        return render(request,'comprar_pago.html', {'producto': producto,'cantidad': cantidad,'form': form})
    
class ComprarPagoCuotasVista(View):

    def get(self, request,id_preferencia):
        print(id_preferencia)
        preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        if preferencia:
            if "tarjeta_datos" in preferencia.preferencia:
                tarjeta_cuotas = preferencia.preferencia["tarjeta_cuotas"]
                tarjeta_datos = preferencia.preferencia["tarjeta_datos"]
                print(preferencia.preferencia["tarjeta_datos"])
                print(preferencia.preferencia["tarjeta_cuotas"])

                return render(request,'comprar_cuotas.html',{'tarjeta_cuotas':tarjeta_cuotas,'tarjeta_datos':tarjeta_datos})
            else:
                print("No hay datos de tarjeta en la preferecia")
            print(preferencia)

        raise Http404("Página no encontrada")

    def post(self, request, id_preferencia):
        obtener_preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        cuotas = request.POST.get("cuotas")
        if obtener_preferencia:
            preferencia = obtener_preferencia.preferencia
            if "tarjeta_datos" in preferencia and "productos":
                actulizar_preferencia = PedidoPreferencia.actulizar_preferencia(request, id_preferencia, cuotas=cuotas)
                url=f"/comprar/resumen/preferencia-id={id_preferencia}"
                response = JsonResponse({'url': url})
                response.status_code = 201
                return response
            
        raise Http404("Página no encontrada")

        
class ComprarResumen(View):

    def get(self, request,id_preferencia):
        obtener_preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        if obtener_preferencia:
            preferencia = obtener_preferencia.preferencia
            if "tarjeta_datos" in preferencia and "productos":
                print(preferencia["productos"])
                print(preferencia["tarjeta_datos"])

            return render(request,'comprar_confirmacion.html')

        raise Http404("Página no encontrada")

    def post(self, request, id_preferencia):
        print(request.POST)
        return HttpResponse(status=200)
    

class ComprarCarritoVista(View):


    def get(self, request):
        form = PagoForm
        obtener_carrito = CarritoCompra.obtener_carrito(request)
        carrito = obtener_carrito[0]
        productos_lista = Pedido.procesar_lista_productos(carrito)
        total = obtener_carrito[1]
        preferencia = PedidoPreferencia.crear_preferencia(request,carrito=carrito)
        preference_mercadopago = Mercado.generar_preference_mercadopago(request, carrito=carrito)
        return render(request,'comprar_pago.html', {'preference': preference_mercadopago[0],'public_token': preference_mercadopago[1],'carrito_compra': carrito,'total': total,'form': form, 'productos_lista':productos_lista})
    
    def post(self, request):
        parametro_productos = request.POST.get("productos")
        productos_lista = Pedido.procesar_parametro(parametro_productos)
        productos = Producto.obtener_producto(productos_lista=productos_lista)
        Pedido.crear_pedido_carrito(request, productos=productos)
        return render(request,'comprar_pago.html')


class ComprarMercadoPagoVista(View):
    def post(self, request, usuario):
        print("Este es el usuario recivido",usuario)
        if request.GET.get("type") and request.GET.get("data.id"):
            type = request.GET.get("type")
            data_id = request.GET.get("data.id")
            Mercado.procesar_respuesta_mp(type,data_id)

        return HttpResponse(status=200)
    
class AgregarCarritoVista(CreateView):
    def post(self, request, id_producto, cantidad):
        comprobar_carrito_usuario = CarritoCompra.comprobar_carrito_usuario(request, id_producto)
        if comprobar_carrito_usuario:
            agregar_carrito = CarritoCompra.agregar_carrito(request, id_producto, cantidad)
            response = JsonResponse({'response':'response'})
            response.status_code = 201
            return response
        else:
            error = "error"
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response

class ActualizarCarritoVista(UpdateView):
    def post(self, request, id_producto, cantidad):
        actualizar_cantidad = CarritoCompra.actualizar_cantidad_producto_carrito(request, id_producto, cantidad)
        if actualizar_cantidad:
            response = JsonResponse({'response':'response'})
            response.status_code = 201
            return response
        else:
            response = JsonResponse({'error':'error'})
            response.status_code = 400
            return response

class EliminarCarritoVista(DeleteView):
    def post(self, request, id_carrito):
        eliminar_producto_carrito = CarritoCompra.eliminar_producto_carrito(request, id_carrito)
        response = JsonResponse({'response':'response'})
        response.status_code = 201
        return response

class CarritoVista(ListView):
    template_name = "carrito.html"
    context_object_name = "carrito_productos"
    # paginate_by = 10
    def get_queryset(self):
        carrito = CarritoCompra.obtener_carrito(self.request)
        queryset = carrito[0]
        queryset.total = carrito[1]

        return queryset
