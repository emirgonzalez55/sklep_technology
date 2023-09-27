from django.db import models
from django.contrib.auth import authenticate, login
from django.db.models.signals import pre_save
from django.utils.text import slugify
from django.contrib.auth.models import  AbstractBaseUser,UserManager,PermissionsMixin,Group
# Create your models here.

class Usuarios(AbstractBaseUser,PermissionsMixin):
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

    def create_user(form_registro):  
        usuario = form_registro.cleaned_data.get('usuario')
        password = form_registro.cleaned_data.get('password1')
        nombre = form_registro.cleaned_data.get('nombre')
        apellido = form_registro.cleaned_data.get('apellido')
        email = form_registro.cleaned_data.get('email')
        
        user = Usuarios(
            usuario = usuario,
            nombre = nombre,
            apellido = apellido,
            email = email
        )
        user.set_password(password)
        user.save()
        grupo = Group.objects.get(name="Usuario")
        user.groups.add(grupo)
        return user
    

class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True)  
    categoria_nombre = models.CharField(max_length=16,unique=True)
    categoria_descripcion = models.CharField(max_length=255)

    def __str__(self):
        return self.categoria_nombre
class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(Categorias, on_delete=models.SET_NULL, null=True)
    producto_nombre = models.CharField("Nombre de producto",max_length=100, unique=True)
    descripcion = models.CharField(max_length=255)
    imagen = models.ImageField(upload_to="productos_imagenes")
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidades_stock = models.PositiveBigIntegerField()
    slug = models.SlugField(max_length=100,unique=True)

    class Meta:
        verbose_name = "Producto" 
        verbose_name_plural = "Productos" 
    
def crear_slug(sender, instance,*args,**kwargs):
    instance.slug = slugify(instance.producto_nombre)

pre_save.connect(crear_slug, sender=Productos)


