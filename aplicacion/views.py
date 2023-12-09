from typing import Any
from django.db import models
from django.db.models.query import QuerySet
from django.forms.forms import BaseForm
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse, JsonResponse,Http404
from django.contrib import messages
from aplicacion.forms import RegistroForm, LoginForm, ProductForm,PagoForm,EditarPerfilForm,PasswordChangeForm,CrearUsuarioForm,EditarUsuarioForm,CategoriaForm,MarcaForm
from aplicacion.models import Usuario, Producto,Tarjeta,Pedido,CarritoCompra,Mercado,ProductoCategoria,ProductoMarca,PedidoPreferencia,PedidoDetalle
from django.contrib.auth.views import LoginView,LogoutView
from django.views.generic import ListView,CreateView, UpdateView, DeleteView,TemplateView,DetailView,View,FormView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash 

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

class PerfilVista(LoginRequiredMixin,TemplateView):
    template_name = "perfil.html"

class PerfilEditarVista(LoginRequiredMixin,UpdateView):
    template_name = "perfil_editar.html"
    model = Usuario
    form_class = EditarPerfilForm
    def get_object(self):
        return self.request.user
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance = self.get_object())
        if form.is_valid():
            form.save()
            mensaje = "Perfil editado correctamente"
            response = JsonResponse({'mensaje':mensaje})
            response.status_code = 201
            return response
        else:
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response

class PerfilCambiarPasswordVista(LoginRequiredMixin,FormView):
    template_name = "perfil_cambiar_password.html"
    model = Usuario
    def get_form(self):
        form_class = PasswordChangeForm(user=self.request.user, data=self.request.POST)
        return form_class

    def post(self, request, *args, **kwargs):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            mensaje = "Contraseña cambiada correctamente"
            response = JsonResponse({'mensaje':mensaje})
            response.status_code = 201
            return response
        else:
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response    


class AdministrarUsuariosVista(PermissionRequiredMixin,ListView):
    permission_required = 'aplicacion.view_usuario'
    template_name = "administrar_usuarios.html"
    context_object_name = "usuarios"
    paginate_by = 10
    def get_queryset(self):
        queryset = Usuario.objects.filter().exclude(id_usuario=self.request.user.id_usuario)
        if self.request.GET.get("buscar"):
            buscar = self.request.GET.get("buscar")
            queryset = queryset.filter(usuario__icontains=buscar)

        return queryset

class AdministrarCrearUsuarioVista(PermissionRequiredMixin,CreateView):
    permission_required = 'aplicacion.add_usuario'
    template_name = "administrar_usuarios_crear.html"
    model = Usuario
    form_class = CrearUsuarioForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            form.save()
            mensaje = "Usuario creado correctamente"
            usuario = f"Usuario {form.cleaned_data.get('usuario')}"
            response = JsonResponse({'mensaje':mensaje,'usuario':usuario})
            response.status_code = 201
            return response
        else:
            print(form.errors)
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response
        
class AdministrarEditarUsuarioVista(PermissionRequiredMixin,UpdateView):
    permission_required = 'aplicacion.add_usuario'
    template_name = "administrar_usuarios_editar.html"
    model = Usuario
    form_class = EditarUsuarioForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance = self.get_object())
        if form.is_valid():
            form.save()
            mensaje = "Usuario editado correctamente"
            usuario = f"Usuario {form.cleaned_data.get('usuario')}"
            response = JsonResponse({'mensaje':mensaje,'usuario':usuario})
            response.status_code = 201
            return response
        else:
            print(form.errors)
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response
        
class AdministrarUsuariosEliminarVista(PermissionRequiredMixin,DeleteView):
    permission_required = 'aplicacion.delete_usuario'
    template_name = "administrar_usuarios_eliminar.html"
    model = Usuario
    success_url = reverse_lazy('administrar_usuarios')
    
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
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("buscar"):
            buscar = self.request.GET.get("buscar")
            queryset = queryset.filter(producto_nombre__icontains=buscar)

        return queryset

class AdministrarCategoriasVista(PermissionRequiredMixin,ListView):
    permission_required = 'aplicacion.view_producto'
    template_name = "administrar_categorias.html"
    model = ProductoCategoria
    context_object_name = "categorias"
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("buscar"):
            buscar = self.request.GET.get("buscar")
            queryset = queryset.filter(categoria_nombre__icontains=buscar)

        return queryset

class AdministrarCrearCategoriaVista(PermissionRequiredMixin,CreateView):
    permission_required = 'aplicacion.add_producto'
    template_name = "administrar_categorias_crear.html"
    model = ProductoCategoria
    form_class = CategoriaForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            form.save()
            mensaje = "Categoria agregada correctamente"
            categoria = f"Categoria {form.cleaned_data.get('categoria_nombre')}"
            response = JsonResponse({'mensaje':mensaje,'categoria':categoria})
            response.status_code = 201
            return response
        else:
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response
        
class AdministrarEditarCategoriaVista(PermissionRequiredMixin,UpdateView):
    permission_required = 'aplicacion.change_producto'
    template_name = "administrar_categorias_editar.html"
    model = ProductoCategoria
    form_class = CategoriaForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance = self.get_object())
        if form.is_valid():
            form.save()
            mensaje = "Categoria editada correctamente"
            categoria = f"Categoria {form.cleaned_data.get('categoria_nombre')}"
            response = JsonResponse({'mensaje':mensaje,'categoria':categoria})
            response.status_code = 201
            return response
        else:
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response
        
class AdministrarCategoriaEliminarVista(PermissionRequiredMixin,DeleteView):
    permission_required = 'aplicacion.delete_productos'
    template_name = "administrar_categorias_eliminar.html"
    model = ProductoCategoria
    success_url = reverse_lazy('administrar_categorias')

class AdministrarMarcasVista(PermissionRequiredMixin,ListView):
    permission_required = 'aplicacion.view_producto'
    template_name = "administrar_marcas.html"
    model = ProductoMarca
    context_object_name = "marcas"
    paginate_by = 10
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.GET.get("buscar"):
            buscar = self.request.GET.get("buscar")
            queryset = queryset.filter(marca_nombre__icontains=buscar)

        return queryset

class AdministrarMarcaCrearVista(PermissionRequiredMixin,CreateView):
    permission_required = 'aplicacion.add_producto'
    template_name = "administrar_marca_crear.html"
    model = ProductoMarca
    form_class = MarcaForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None)
        if form.is_valid():
            form.save()
            mensaje = "Marca agregada correctamente"
            marca = f"Marca {form.cleaned_data.get('marca_nombre')}"
            response = JsonResponse({'mensaje':mensaje,'marca':marca})
            response.status_code = 201
            return response
        else:
            print(form.errors)
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response
        
class AdministrarMarcaEditarVista(PermissionRequiredMixin,UpdateView):
    permission_required = 'aplicacion.change_producto'
    template_name = "administrar_marca_editar.html"
    model = ProductoMarca
    form_class = MarcaForm
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance = self.get_object())
        if form.is_valid():
            form.save()
            mensaje = "Marca editada correctamente"
            marca = f"Marca {form.cleaned_data.get('marca_nombre')}"
            response = JsonResponse({'mensaje':mensaje,'marca':marca})
            response.status_code = 201
            return response
        else:
            error = form.errors
            response = JsonResponse({'error':error})
            response.status_code = 400
            return response
        
class AdministrarMarcaEliminarVista(PermissionRequiredMixin,DeleteView):
    permission_required = 'aplicacion.delete_productos'
    template_name = "administrar_marca_eliminar.html"
    model = ProductoMarca
    success_url = reverse_lazy('administrar_marcas')

    
class AdministrarPedidosVista(PermissionRequiredMixin,ListView):
    permission_required = 'aplicacion.view_pedido'
    template_name = "administrar_pedidos.html"
    context_object_name = "pedidos"
    paginate_by = 10
    def get_queryset(self):
        queryset = Pedido.objects.filter().order_by("-fecha_pedido")
        if self.request.GET.get("buscar"):
            buscar = self.request.GET.get("buscar")
            queryset = queryset.filter(id_pedido__icontains=buscar)
        return queryset
    
class AdministrarPedidoDetalleVista(PermissionRequiredMixin,View):
    permission_required = 'aplicacion.view_pedidodetalle'
    def get(self,request,id_pedido):
        obtener_pedido_detalle = PedidoDetalle.obtener_pedido_detalle(id_pedido=id_pedido)
        if obtener_pedido_detalle:
            pedido = obtener_pedido_detalle["pedido"]
            pedido_detalle = obtener_pedido_detalle["pedido_detalle"]
            return render(request,'administrar_pedido_detalle.html', {'pedido': pedido,'pedido_detalle': pedido_detalle})
        raise Http404("Página no encontrada")
    
class EliminarPedidoVista(PermissionRequiredMixin,DeleteView):
    permission_required = 'aplicacion.delete_pedido'
    template_name = "administrar_pedido_delete.html"
    model = Pedido
    success_url = reverse_lazy('administrar_pedidos')


class AdministrarPanelVista(PermissionRequiredMixin,ListView):
    permission_required = 'aplicacion.view_pedido'
    template_name = "administrar_panel.html"
    context_object_name = "panel_datos"
    def get_queryset(self):
        queryset = PedidoDetalle.obtener_pedidos_grafico()
        print(queryset)
        return queryset

class CrearProductoVista(PermissionRequiredMixin,CreateView):
    permission_required = 'aplicacion.add_producto'
    template_name = "administrar_productos_crear.html"
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
    template_name = "administrar_productos_editar.html"
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


class ComprarMetodoPagoVista(LoginRequiredMixin,View):
    def get(self, request,producto_slug,cantidad):
        producto = Producto.obtener_producto(slug=producto_slug)
        if producto and cantidad:
            preferencia = PedidoPreferencia.crear_preferencia(request,producto=producto,cantidad=cantidad)
            if preferencia:
                form = PagoForm
                productos = Producto.obtener_producto(productos_lista=preferencia.preferencia_datos["productos"])
                preference_mercadopago = Mercado.generar_preference_mercadopago(request, producto=producto,cantidad=cantidad)
                return render(request,'comprar_pago.html', {'preferencia': preferencia,'preference': preference_mercadopago[0],'public_token': preference_mercadopago[1], 'productos': productos,'form': form})
        
        raise Http404("Producto no encontrado")

    def post(self, request,producto_slug,cantidad):
        # producto = Producto.obtener_producto(slug=producto_slug)
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
                        url = f"/comprar/confirmar/preferencia-id={id_preferencia}"
                        response = JsonResponse({'url': url})
                        response.status_code = 201
                        return response
            else:
                print("Tarjeta inválida")  
                error = ""
                response = JsonResponse({'error': error})
                response.status_code = 404
                return response
        else:
            error = form.errors
            response = JsonResponse({'error': error})
            response.status_code = 404
            return response

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
  

        # return render(request,'comprar_pago.html', {'producto': producto,'cantidad': cantidad,'form': form})
    
class ComprarPagoCuotasVista(View):

    def get(self, request,id_preferencia):
        print(id_preferencia)
        obtener_preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        if obtener_preferencia:
            preferencia = obtener_preferencia.preferencia_datos
            if "tarjeta_datos" in preferencia:
                if preferencia["tarjeta_datos"].get("tipo") == "credito":
                    tarjeta_cuotas = preferencia["tarjeta_cuotas"]
                    tarjeta_datos = preferencia["tarjeta_datos"]
                    print(preferencia["tarjeta_datos"])
                    print(preferencia["tarjeta_cuotas"])

                    return render(request,'comprar_cuotas.html',{'tarjeta_cuotas':tarjeta_cuotas,'tarjeta_datos':tarjeta_datos,'preferencia':preferencia})

        raise Http404("Página no encontrada")

    def post(self, request, id_preferencia):
        obtener_preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        cuotas = request.POST.get("cuotas")
        if obtener_preferencia:
            preferencia = obtener_preferencia.preferencia_datos
            if "tarjeta_datos" in preferencia and "productos":
                actulizar_preferencia = PedidoPreferencia.actulizar_preferencia(request, id_preferencia, cuotas=cuotas)
                url=f"/comprar/confirmar/preferencia-id={id_preferencia}"
                response = JsonResponse({'url': url})
                response.status_code = 201
                return response
            
        raise Http404("Página no encontrada")

        
class ComprarConfirmar(View):

    def get(self, request,id_preferencia):
        obtener_preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        if obtener_preferencia:
            preferencia = obtener_preferencia.preferencia_datos
            if "tarjeta_datos" in preferencia and "productos" in preferencia:
                if preferencia["tarjeta_datos"].get("cuotas") or preferencia["tarjeta_datos"].get("tipo") == "debito":
                    productos = Producto.obtener_producto(productos_lista=preferencia["productos"])
                    return render(request,'comprar_confirmacion.html', {'productos':productos,'preferencia':preferencia})
                
        raise Http404("Página no encontrada")

    def post(self, request, id_preferencia):
        preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        if preferencia:
            if "tarjeta_datos" in preferencia.preferencia_datos and "productos" in preferencia.preferencia_datos:
                productos = Producto.obtener_producto(productos_lista=preferencia.preferencia_datos["productos"])
                crear_pedido = Pedido.crear_pedido(request=request,productos=productos,preferencia_datos=preferencia.preferencia_datos)
                if crear_pedido:
                    PedidoPreferencia.eliminar_preferencia(id_preferencia)
                    url="/comprar/resultado/correcto"
                    response = JsonResponse({'url': url})
                    response.status_code = 201
                    return response
                else:
                    PedidoPreferencia.eliminar_preferencia(id_preferencia)
                    url="/comprar/resultado/falla"
                    response = JsonResponse({'url': url})
                    response.status_code = 404
                    return response

        raise Http404("Página no encontrada")
    

class ComprarCarritoVista(View):
    def get(self, request):
        form = PagoForm
        obtener_carrito = CarritoCompra.obtener_carrito(request)
        carrito = obtener_carrito[0]
        preferencia = PedidoPreferencia.crear_preferencia(request,carrito=carrito)
        if preferencia:
            productos = Producto.obtener_producto(productos_lista=preferencia.preferencia_datos["productos"])
            preference_mercadopago = Mercado.generar_preference_mercadopago(request, carrito=carrito)
            return render(request,'comprar_pago.html', {'preferencia': preferencia, 'preference': preference_mercadopago[0],'public_token': preference_mercadopago[1],'productos': productos,'form': form})
        
        raise Http404("Producto no encontrado")
    def post(self, request):
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
                        url = f"/comprar/confirmar/preferencia-id={id_preferencia}"
                        response = JsonResponse({'url': url})
                        response.status_code = 201
                        return response
            else:
                print("Tarjeta inválida")  
        # parametro_productos = request.POST.get("productos")
        # productos_lista = Pedido.procesar_parametro(parametro_productos)
        # productos = Producto.obtener_producto(productos_lista=productos_lista)
        # Pedido.crear_pedido_carrito(request, productos=productos)
        # return render(request,'comprar_pago.html')


class ComprarMercadoPagoVista(View):
    def post(self, request, usuario):
        if request.GET.get("type") and request.GET.get("data.id"):
            type = request.GET.get("type")
            data_id = request.GET.get("data.id")
            Mercado.procesar_respuesta_mp(type,data_id,usuario)
        return HttpResponse(status=200)
    
class ComprarResultadoVista(View):
    def get(self,request,resultado):
        return render(request,'comprar_resultado.html', {'resultado': resultado})
    
class ComprasVista(ListView):
    template_name = "compras.html"
    context_object_name = "pedidos"
    # paginate_by = 10    

    def get_queryset(self):
        pedidos = Pedido.obtener_pedidos(self.request)
        queryset = pedidos
        return queryset
    
class CompraDetalleVista(LoginRequiredMixin,View):
    def get(self,request,id_pedido):
        obtener_pedido_detalle = PedidoDetalle.obtener_pedido_detalle(request=request,id_pedido=id_pedido)
        if obtener_pedido_detalle:
            pedido = obtener_pedido_detalle["pedido"]
            pedido_detalle = obtener_pedido_detalle["pedido_detalle"]
            return render(request,'compra_detalle.html', {'pedido': pedido,'pedido_detalle': pedido_detalle})
        
        raise Http404("Página no encontrada")

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

class CarritoVista(LoginRequiredMixin,ListView):
    template_name = "carrito.html"
    context_object_name = "carrito_productos"
    # paginate_by = 10
    def get_queryset(self):
        carrito = CarritoCompra.obtener_carrito(self.request)
        queryset = carrito[0]
        queryset.total = carrito[1]

        return queryset
