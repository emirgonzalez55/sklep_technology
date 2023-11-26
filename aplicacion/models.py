from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.auth.models import  AbstractBaseUser,UserManager,PermissionsMixin,Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from decimal import Decimal
import mercadopago
import json
# Create your models here.

class Usuario(AbstractBaseUser,PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=16, unique=True)
    password = models.CharField(max_length=255)
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=45)
    email = models.EmailField(max_length=45, unique=True)

    USERNAME_FIELD = 'usuario'
    objects = UserManager()
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        db_table = "aplicacion_usuarios"

    def crear_usuario(form_registro):
        usuario = form_registro.cleaned_data.get('usuario')
        password = form_registro.cleaned_data.get('password1')
        nombre = form_registro.cleaned_data.get('nombre')
        apellido = form_registro.cleaned_data.get('apellido')
        email = form_registro.cleaned_data.get('email')

        usuario = Usuario(
            usuario = usuario,
            nombre = nombre,
            apellido = apellido,
            email = email
        )
        usuario.set_password(password)
        usuario.save()
        try:
            grupo = Group.objects.get(name="Usuario")
        except ObjectDoesNotExist:
            grupo = Group.objects.create(name="Usuario")
        usuario.groups.add(grupo)
        return usuario


class ProductoCategoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    categoria_nombre = models.CharField(max_length=32,unique=True)
    categoria_descripcion = models.CharField(max_length=255)
    slug = models.SlugField(max_length=32, unique=True, blank=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        db_table = "aplicacion_productos_categorias"

    def __str__(self):
        return self.categoria_nombre


class ProductoMarca(models.Model):
    id_marca = models.AutoField(primary_key=True)
    marca_nombre = models.CharField(max_length=32,unique=True)
    marca_descripcion = models.CharField(max_length=255)
    slug = models.SlugField(max_length=32, unique=True, blank=True)

    class Meta:
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"
        db_table = "aplicacion_productos_marcas"

    def __str__(self):
        return self.marca_nombre

class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(ProductoCategoria, on_delete=models.SET_NULL, null=True)
    marca = models.ForeignKey(ProductoMarca, on_delete=models.SET_NULL, null=True)
    producto_nombre = models.CharField("Nombre de producto",max_length=100, unique=True)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to="productos_imagenes")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidades_stock = models.PositiveBigIntegerField()
    slug = models.SlugField(max_length=100,unique=True, blank=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        db_table = "aplicacion_productos"

    def __str__(self):
        return self.producto_nombre

    def obtener_producto(**kwargs):
        if "slug" in kwargs or "id_producto" in kwargs:
            try:
                producto = Producto.objects.get(**kwargs)
            except ObjectDoesNotExist:
                producto = None
            return producto
        
        if "productos_lista" in kwargs:
            productos_lista = kwargs["productos_lista"]
            productos = []
            for producto_lista in productos_lista:
                try:
                    producto = Producto.objects.get(id_producto = producto_lista["id_producto"])
                    producto.cantidad = producto_lista["cantidad"]
                    productos.append(producto)
                except ObjectDoesNotExist:
                    productos = None
            return productos

    
    def comprobar_stock(**kwargs):
        if "producto" in kwargs:
            producto = kwargs["producto"]
            cantidad = kwargs["cantidad"]
            if producto and cantidad:
                if producto.unidades_stock >= cantidad:
                    comprobar_stock = True
                else:
                    comprobar_stock = False
            else:
                comprobar_stock = False

            return comprobar_stock
        
        if "productos" in kwargs:
            productos = kwargs["productos"]
            if productos:
                for producto in productos:
                    if producto.unidades_stock >= producto.cantidad:
                        comprobar_stock = True
                    else:
                        comprobar_stock = False
                        break
            else:
                comprobar_stock = False

            return comprobar_stock

    def actualizar_stock(**kwargs):
        if "producto" in kwargs:
            producto_id = kwargs["producto"]
            cantidad = kwargs["cantidad"]
            producto = Producto.obtener_producto(id_producto=producto_id)
            if producto:
                comprobar_stock = Producto.comprobar_stock(producto=producto, cantidad=cantidad)
                if comprobar_stock:
                    producto.unidades_stock = producto.unidades_stock - cantidad
                    producto.save()
                    actualizar_stock = True
                else:
                    actualizar_stock = False
            else:
                actualizar_stock = False

        if "productos" in kwargs:
            productos = kwargs["productos"]
            if productos:
                comprobar_stock = Producto.comprobar_stock(productos=productos)
                if comprobar_stock:
                    for producto in productos:
                        producto.unidades_stock = producto.unidades_stock - producto.cantidad
                        producto.save()
                        actualizar_stock = True
                else:
                    actualizar_stock = False
            else:
                actualizar_stock = False
            
        return actualizar_stock
    
    def buscar_productos(**kwargs):
        if kwargs:
            borrar_keys = []
            for key, value in kwargs.items():
                if not value:
                    borrar_keys.append(key)
            for key in borrar_keys:
                del kwargs[key]
            try:
                resultados = Producto.objects.filter(**kwargs)
                resultados.categorias = resultados.values("categoria__categoria_nombre","categoria__slug").annotate(cantidad=Count("categoria")).order_by("-cantidad")
                resultados.marcas = resultados.values("marca__marca_nombre","marca__slug").annotate(cantidad=Count("marca")).order_by("-cantidad")
                resultados.cantidad_resultados = resultados.count()
            except:
                resultados = None

            return resultados

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        db_table = "aplicacion_pedidos"

    def crear_pedido(request,**kwargs):
        if "producto" in kwargs:
            producto = kwargs["producto"]
            cantidad = kwargs["cantidad"]
            comprobar_stock = Producto.comprobar_stock(producto=producto,cantidad=cantidad)
            if comprobar_stock:
                usuario = request.user.id_usuario
                pedido = Pedido(
                    usuario_id  = usuario,
                )
                pedido.save()
                if pedido:
                    pedido_detalle = PedidoDetalle.crear_pedido_detalle(id_pedido=pedido.id_pedido,producto=producto,cantidad=cantidad)
                    if pedido_detalle:
                        pedido = True
                    else:
                        pedido = False
                else:
                    pedido = False
            else:
                pedido = False
            
            return pedido

        if "productos" in kwargs:
            productos = kwargs["productos"]
            comprobar_stock = Producto.comprobar_stock(productos=productos)
            if comprobar_stock:
                usuario = request.user.id_usuario
                pedido = Pedido(
                    usuario_id  = usuario,
                )
                pedido.save()
                if pedido:
                    pedido_detalle = PedidoDetalle.crear_pedido_detalle(id_pedido=pedido.id_pedido,productos=productos)
                    if pedido_detalle:
                        pedido = True
                    else:
                        pedido = False
                else:
                    pedido = False
            else:
                pedido = False
                
            return pedido

    def procesar_parametro(productos):
        productos_procesados = []
        for producto in productos.split(","):
            productos_procesados.append({ "id_producto": int(producto.split("-")[0]), "cantidad": int(producto.split("-")[1])})

        return productos_procesados

    def procesar_lista_productos(carrito_compra):
        lista_productos = []
        for carrito in carrito_compra:
            if carrito.cantidad:
                lista_productos.append(f"{carrito.producto.id_producto}-{carrito.cantidad}")
       
        productos = ",".join(lista_productos)
        return productos
      

class PedidoDetalle(models.Model):
    id_pedido_detalle = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Pedido detalle"
        verbose_name_plural = "Pedidos detalle"
        db_table = "aplicacion_pedidos_detalle"

    def crear_pedido_detalle(**kwargs):
        if "productos" in kwargs:
            productos = kwargs["productos"]
            id_pedido = kwargs["id_pedido"]
            comprobar_stock = Producto.comprobar_stock(productos=productos)
            if comprobar_stock:
                print("Si hay stock de los productos")
                for producto in productos:
                    pedido_detalle = PedidoDetalle(
                        pedido_id  = id_pedido,
                        producto_id = producto.id_producto,
                        precio_unitario = producto.precio_unitario,
                        cantidad = producto.cantidad
                    )
                    pedido_detalle.save()
                if pedido_detalle:
                    print("pedido_detalle creado corretamente",pedido_detalle)
                    actualizar_stock = Producto.actualizar_stock(productos=productos)
                    if actualizar_stock:
                        print("actualizar_stock corretamente")
                        pedido_detalle = True
                    else:
                        pedido_detalle = False
                else:
                    pedido_detalle = False
            else:
                pedido_detalle = False

            return pedido_detalle

        if "producto" in kwargs:
            producto = kwargs["producto"]
            cantidad = kwargs["cantidad"]
            id_pedido = kwargs["id_pedido"]
            
            comprobar_stock = Producto.comprobar_stock(producto=producto,cantidad=cantidad)
            if comprobar_stock:
                pedido_detalle = PedidoDetalle(
                    pedido_id  = id_pedido,
                    producto_id = producto.id_producto,
                    precio_unitario = producto.precio_unitario,
                    cantidad = cantidad
                )
                pedido_detalle.save()
                if pedido_detalle:
                    actualizar_stock = Producto.actualizar_stock(producto=producto.id_producto ,cantidad=cantidad)
                    if actualizar_stock:
                        pedido_detalle = True
                    else:
                        pedido_detalle = False
                else:
                    print("Error al craer pedido individual")
            else:
                pedido_detalle = False

            return pedido_detalle
    

class Tarjeta(models.Model):
    id_tarjeta = models.AutoField(primary_key=True)
    numero = models.PositiveBigIntegerField()
    red = models.CharField(max_length=32)
    tipo = models.CharField(max_length=32)
    codigo_seguridad = models.PositiveSmallIntegerField()
    fecha_caducidad = models.PositiveSmallIntegerField()
    intereses = models.JSONField(null=True)

    class Meta:
        verbose_name = "Tarjeta"
        verbose_name_plural = "Tarjetas"
        db_table = "aplicacion_tarjetas"

    def check_tarjeta(form):
        numero = form.cleaned_data.get('tarjeta_numero')
        codigo_seguridad = form.cleaned_data.get('tarjeta_codigo')
        fecha_caducidad = form.cleaned_data.get('tarjeta_fecha')

        try:
            tarjeta = Tarjeta.objects.get(numero = numero, codigo_seguridad = codigo_seguridad, fecha_caducidad = fecha_caducidad)
        except ObjectDoesNotExist:
            tarjeta = None

        return tarjeta

class CarritoCompra(models.Model):
    id_carrito = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Carrito de compra"
        verbose_name_plural = "Carrito de compras"
        db_table = "aplicacion_carrito_compras"

    def agregar_carrito(request, id_producto, cantidad):
        usuario = request.user.id_usuario
        producto = Producto.obtener_producto(id_producto = id_producto)
        comprobar_stock = Producto.comprobar_stock(producto=producto, cantidad=cantidad)
        if comprobar_stock:
            carrito = CarritoCompra(
                usuario_id = usuario,
                producto_id = producto.id_producto,
                cantidad = cantidad
            )
            carrito.save()


    def obtener_carrito(request):
        usuario = request.user.id_usuario
        total = 0
        carrito_compra = CarritoCompra.objects.filter(usuario=usuario)
        if carrito_compra:
            for carrito in carrito_compra:
                if carrito.producto.unidades_stock:
                    carrito.subtotal = carrito.producto.precio_unitario * carrito.cantidad
                    carrito.cantidad_select = range(1, carrito.producto.unidades_stock + 1)
                    total += carrito.subtotal
                else:
                    carrito.cantidad = 0
                    carrito.save()

        return carrito_compra, total

    def comprobar_carrito_usuario(request, producto):
        usuario = request.user.id_usuario
        try:
            carrito_usuario = CarritoCompra.objects.get(usuario = usuario, producto = producto)
            carrito_usuario = False
        except ObjectDoesNotExist:
            carrito_usuario = True

        return carrito_usuario

    def actualizar_cantidad_producto_carrito(request, carrito, cantidad):
        usuario = request.user.id_usuario
        try:
            cantidad_producto_carrito = CarritoCompra.objects.get(id_carrito = carrito, usuario = usuario)
            comprobar_stock = Producto.comprobar_stock(producto=cantidad_producto_carrito.producto, cantidad=cantidad)
            if comprobar_stock:
                cantidad_producto_carrito.cantidad = cantidad
                cantidad_producto_carrito.save()
            else:
                cantidad_producto_carrito = None
        except ObjectDoesNotExist:
            cantidad_producto_carrito = None

        return cantidad_producto_carrito

    def eliminar_producto_carrito(request, id_carrito):
        usuario = request.user.id_usuario
        try:
            producto_carrito = CarritoCompra.objects.get(id_carrito=id_carrito,usuario=usuario)
            producto_carrito.delete()

        except ObjectDoesNotExist:
            print("Error en eliminar producto de carrito")


class Mercado(models.Model):
    id = models.AutoField(primary_key=True)
    private_access_token = models.CharField(max_length=255)
    public_access_token = models.CharField(max_length=255)

    def generar_preference_mercadopago(request,**kwargs):
        tokens = Mercado.objects.get(id=1)
        public_token = tokens.public_access_token
        sdk = mercadopago.SDK(tokens.private_access_token)
        usuario = request.user.id_usuario

        if "producto" and "cantidad" in kwargs:
            producto = kwargs["producto"]
            cantidad = kwargs["cantidad"]
            preference_data = {
                "items": [
                    {"id": producto.id_producto,
                     "title": producto.producto_nombre,
                     "quantity": cantidad,
                     "unit_price": float(producto.precio_unitario),
                     }
                ],"notification_url" : f"/comprar/mercadopago/{usuario}"
            }

        if "carrito" in kwargs:
            carrito_compra = kwargs["carrito"]
            productos = []
            for carrito in carrito_compra:
                if carrito.producto.unidades_stock:
                    productos.append({ "id": carrito.producto.id_producto, "title": carrito.producto.producto_nombre ,"quantity": carrito.cantidad,"unit_price": float(carrito.producto.precio_unitario)})

            preference_data = {
            "items": productos,
            "notification_url" : f"/comprar/mercadopago/{usuario}"
            }

        # preference_data = {
            # "back_urls": {
            #      "success": "http://127.0.0.1:8000/comprar/producto-test-cantidad=1",
            #      "failure": "http://127.0.0.1:8000/comprar/producto-test-cantidad=1",
            #      "pending": "http://127.0.0.1:8000/comprar/producto-test-cantidad=1"
            # },
        #     "auto_return": "approved",
        #     "notification_url" : ""
        # }
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]

        return preference, public_token
    
    def procesar_respuesta_mp(type,data_id):
        tokens = Mercado.objects.get(id=1)
        sdk = mercadopago.SDK(tokens.private_access_token)

        # if topic == "merchant_order":
        #     merchant_order = sdk.merchant_order().get(id)           
        #     print("Esto es merchant_order",merchant_order)
        #     # for payment in merchant_order["payments"]:
        #     #     print(payment['status'])

        if type == "payment":
            payment = sdk.payment().get(data_id)
            status = payment["response"]["status"]
            print("El estado de la operación es",status)
            if status == "approved":
                productos = payment["response"]["additional_info"]["items"]
                for producto in productos:
                    print(producto["id"])
                    print(producto["title"])


class PedidoPreferencia(models.Model):
    id_preferencia = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    preferencia = models.JSONField()

    class Meta:
        db_table = "aplicacion_pedidos_preferencias"

    def crear_preferencia(request,**kwargs):
        usuario = request.user.id_usuario
        try:
            preferencia_usuario = PedidoPreferencia.objects.get(usuario_id=usuario)
        except ObjectDoesNotExist:
            preferencia_usuario = None
        if preferencia_usuario:
            preferencia_usuario.delete()

        preferencia = {}
        if "carrito" in kwargs:
            carrito_compra = kwargs["carrito"]
            productos_lista = []
            total = 0
            for carrito in carrito_compra:
                if carrito.producto.unidades_stock and carrito.cantidad:
                    productos_lista.append({ "id_producto": carrito.producto.id_producto, "producto_nombre": carrito.producto.producto_nombre ,"cantidad": carrito.cantidad,"precio_unitario": float(carrito.producto.precio_unitario)})
                    total += float(carrito.producto.precio_unitario * carrito.cantidad)

            preferencia["productos"]=productos_lista
            preferencia["total"]=total


        if "producto" in kwargs:
            producto = kwargs["producto"]
            cantidad = kwargs["cantidad"]
            productos = [
                    {"id_producto": producto.id_producto,
                    "producto_nombre": producto.producto_nombre,
                    "cantidad": cantidad,
                    "precio_unitario": float(producto.precio_unitario)
                    }
            ]  
            total = float(producto.precio_unitario * cantidad)
            preferencia["productos"]=productos
            preferencia["total"]=total

        preferencia_datos = json.dumps(preferencia)
        if preferencia_datos:
            preferencia = PedidoPreferencia(
                usuario_id = usuario,
                preferencia = preferencia_datos
            )
            preferencia.save()
            preferencia = PedidoPreferencia.obtener_preferencia(request,preferencia.id_preferencia)
            
        return preferencia
    
    def obtener_preferencia(request,id_preferencia):
        usuario = request.user.id_usuario
        try:
            preferencia = PedidoPreferencia.objects.get(id_preferencia=id_preferencia,usuario_id=usuario)
            preferencia.preferencia = json.loads(preferencia.preferencia) 
        except ObjectDoesNotExist:
            preferencia = None

        return preferencia
    
    def actulizar_preferencia(request,id_preferencia,**kwargs):
        obtener_preferencia = PedidoPreferencia.obtener_preferencia(request,id_preferencia)
        if "tarjeta" in kwargs:
            tarjeta = kwargs["tarjeta"]
            tarjeta_datos = {
                "tarjeta_numero": tarjeta.numero,
                "codigo_seguridad": tarjeta.codigo_seguridad,
                "fecha_caducidad": tarjeta.fecha_caducidad,
                "red": tarjeta.red,
                "tipo": tarjeta.tipo
        }
            obtener_preferencia.preferencia["tarjeta_datos"] = tarjeta_datos

            if tarjeta.tipo == "credito":
                total = obtener_preferencia.preferencia["total"]
                intereses = tarjeta.intereses
                tarjeta_cuotas = []
                for interes in intereses:
                    cuotas = interes["cuotas"]
                    interes = interes["interes"]
                    total_interes = str(round(Decimal(total * interes),2))
                    total_cuota = str(round(Decimal(total * interes/cuotas),2))
                    tarjeta_cuotas.append({ "cuotas": cuotas, "total_cuota": total_cuota ,"total_interes": total_interes})

                obtener_preferencia.preferencia["tarjeta_cuotas"] = tarjeta_cuotas
            
            obtener_preferencia.preferencia = json.dumps(obtener_preferencia.preferencia)
            obtener_preferencia.save()

            return obtener_preferencia
        if "cuotas" in kwargs:
            cuotas = kwargs["cuotas"]
            obtener_preferencia.preferencia["tarjeta_datos"]["cuotas"] = cuotas
            obtener_preferencia.preferencia = json.dumps(obtener_preferencia.preferencia)
            obtener_preferencia.save()
        pass

@receiver(pre_save)
def crear_slug(sender, instance, **kwargs):
    if sender == Producto:
        instance.slug = slugify(instance.producto_nombre)

    if sender == ProductoCategoria:
        instance.slug = slugify(instance.categoria_nombre)

    if sender == ProductoMarca:
        instance.slug = slugify(instance.marca_nombre)