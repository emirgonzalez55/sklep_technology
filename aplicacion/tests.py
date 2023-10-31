from django.test import TestCase

from aplicacion.models import Usuario, Producto, ProductoCategoria, ProductoMarca
from aplicacion.forms import RegistroForm

# Create your tests here.

class UsuarioTestCase(TestCase):

    def setUp(self):
        form = RegistroForm(data={"usuario": "usuario_test", "password1": "password_test", 
                                  "password2": "password_test", "nombre": "nombre_test", 
                                  "apellido": "apellido_test", "email": "test@test.com"})
        form.is_valid()

        self.usuario = Usuario.crear_usuario(form)

    def test_user_creation(self):
        usuario_grupo = self.usuario.groups.get()
        self.assertEqual(self.usuario.usuario, "usuario_test")
        self.assertEqual(self.usuario.nombre, "nombre_test")
        self.assertEqual(self.usuario.apellido, "apellido_test")
        self.assertEqual(self.usuario.email, "test@test.com")
        self.assertEqual(self.usuario.check_password("password_test"), True)
        self.assertEqual(self.usuario.is_superuser, False)       
        self.assertEqual(usuario_grupo.name, "Usuario")


class ProductoTestCase(TestCase):

    def setUp(self):
        self.categoria = ProductoCategoria.objects.create(id_categoria=1, categoria_nombre="categoria_nombre",
                                               categoria_descripcion="categoria_descripcion")
        self.marca = ProductoMarca.objects.create(id_marca=1, marca_nombre="marca_nombre")

        self.producto = Producto.objects.create(
            producto_nombre = "producto nombre",
            descripcion = "descripcion",
            precio_unitario = 99,
            unidades_stock = 10,
            categoria_id = self.categoria.id_categoria,
            marca_id = self.marca.id_marca
        )

    def test_producto_creation(self):
        self.assertEqual(self.producto.producto_nombre, "producto nombre")
        self.assertEqual(self.producto.descripcion, "descripcion")
        self.assertEqual(self.producto.precio_unitario, 99)
        self.assertEqual(self.producto.unidades_stock, 10)
        self.assertEqual(self.producto.categoria.categoria_nombre, "categoria_nombre")
        self.assertEqual(self.producto.marca.marca_nombre, "marca_nombre")
        self.assertEqual(self.producto.slug, "producto-nombre")

    def test_producto_comprobar_stock(self):
        cantidad = 11
        comprobar_stock = Producto.comprobar_stock(self.producto.id_producto,cantidad)
        self.assertEqual(comprobar_stock, False)

    def test_producto_actualizar_stock(self):
        cantidad = 1
        actualizar_stock = Producto.actualizar_stock(self.producto.id_producto, cantidad)
        producto = Producto.obtener_producto(id_producto=self.producto.id_producto)
        self.assertEqual(actualizar_stock, True)
        self.assertEqual(producto.unidades_stock, self.producto.unidades_stock - cantidad)


        
        
