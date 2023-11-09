from django.db import models
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.contrib.auth.models import  AbstractBaseUser,UserManager,PermissionsMixin,Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
import mercadopago
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
    categoria_nombre = models.CharField(max_length=16,unique=True)
    categoria_descripcion = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        db_table = "aplicacion_productos_categorias"

    def __str__(self):
        return self.categoria_nombre


class ProductoMarca(models.Model):
    id_marca = models.AutoField(primary_key=True)
    marca_nombre = models.CharField(max_length=16,unique=True)

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

    def crear_slug(sender, instance,*args,**kwargs):
        instance.slug = slugify(instance.producto_nombre)

    def obtener_producto(**kwargs):
        try:
            producto = Producto.objects.get(**kwargs)
        except ObjectDoesNotExist:
            producto = None

        return producto
    
    def comprobar_stock(producto, cantidad):
        producto = Producto.obtener_producto(id_producto=producto)
        if producto:
            if producto.unidades_stock >= cantidad:
                comprobar_stock = True
            else:
                comprobar_stock = False
        else:
            comprobar_stock = False

        return comprobar_stock

    def actualizar_stock(producto_id, cantidad):
        producto = Producto.obtener_producto(id_producto=producto_id)
        if producto:
            comprobar_stock = Producto.comprobar_stock(producto.id_producto, cantidad)
            if comprobar_stock:
                producto.unidades_stock = producto.unidades_stock - cantidad
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
                resultados.categorias = resultados.values("categoria__categoria_nombre").annotate(cantidad=Count("categoria")).order_by("-cantidad")
                resultados.marcas = resultados.values("marca__marca_nombre").annotate(cantidad=Count("marca")).order_by("-cantidad")
                resultados.cantidad_resultados = resultados.count()
            except:
                resultados = None

            return resultados

pre_save.connect(Producto.crear_slug, sender=Producto)

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        db_table = "aplicacion_pedidos"

    def crear_pedido(request, producto, cantidad):
        usuario = request.user.id_usuario
        pedido = Pedido(
            usuario_id  = usuario,
        )
        pedido.save()
        if pedido:
            pedido_detalle = PedidoDetalle(
                pedido_id  = pedido.id_pedido,
                producto_id = producto.id_producto,
                cantidad = cantidad
            )
            pedido_detalle.save()
            if pedido_detalle:
                actualizar_stock = Producto.actualizar_stock(producto.id_producto ,cantidad)
                if actualizar_stock:
                    pedido = True
        return pedido

class PedidoDetalle(models.Model):
    id_pedido_detalle = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveBigIntegerField()

    class Meta:
        verbose_name = "Pedido detalle"
        verbose_name_plural = "Pedidos detalle"
        db_table = "aplicacion_pedidos_detalle"

class Tarjeta(models.Model):
    id_tarjeta = models.AutoField(primary_key=True)
    numero = models.PositiveBigIntegerField()
    codigo_seguridad = models.PositiveSmallIntegerField()
    fecha_caducidad = models.PositiveSmallIntegerField()

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

    def agregar_carrito(request, producto, cantidad):
        usuario = request.user.id_usuario
        comprobar_stock = Producto.comprobar_stock(producto, cantidad)
        if comprobar_stock:
            carrito = CarritoCompra(
                usuario_id = usuario,
                producto_id = producto,
                cantidad = cantidad
            )
            carrito.save()


    def obtener_carrito(usuario):
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
        else:
            carrito_compra = None

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
            comprobar_stock = Producto.comprobar_stock(cantidad_producto_carrito.producto_id, cantidad)
            if comprobar_stock:
                cantidad_producto_carrito.cantidad = cantidad
                cantidad_producto_carrito.save()
            else:
                cantidad_producto_carrito = None
        except ObjectDoesNotExist:
            cantidad_producto_carrito = None

        return cantidad_producto_carrito

    def eliminar_producto_carrito(request, pk):
        usuario = request.user.id_usuario
        try:
            producto_carrito = CarritoCompra.objects.get(id_carrito=pk,usuario=usuario)
            producto_carrito.delete()

        except ObjectDoesNotExist:
            print("Error en eliminar producto de carrito")


class Mercado(models.Model):
    id = models.AutoField(primary_key=True)
    private_access_token = models.CharField(max_length=255)
    public_access_token = models.CharField(max_length=255)

    def generar_preference_mercadopago(**kwargs):
        tokens = Mercado.objects.get(id=1)
        public_token = tokens.public_access_token
        sdk = mercadopago.SDK(tokens.private_access_token)

        if "producto" and "cantidad" in kwargs:
            producto = kwargs["producto"]
            cantidad = kwargs["cantidad"]
            preference_data = {
                "items": [
                    { "title": producto.producto_nombre,
                     "quantity": cantidad,
                     "unit_price": float(producto.precio_unitario),
                     }
                ]
            }

        if "carrito" in kwargs:
            carrito_compra = kwargs["carrito"][0]
            productos = []
            for carrito in carrito_compra:
                productos.append({ "title": carrito.producto.producto_nombre ,"quantity": carrito.cantidad,"unit_price": float(carrito.producto.precio_unitario)})

            preference_data = {
            "items": productos
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
