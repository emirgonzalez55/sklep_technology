# Generated by Django 4.2.6 on 2023-12-09 02:48

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('id_usuario', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.CharField(max_length=16, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('nombre', models.CharField(max_length=45)),
                ('apellido', models.CharField(max_length=45)),
                ('email', models.EmailField(max_length=45, unique=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
                'db_table': 'aplicacion_usuarios',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Mercado',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('private_access_token', models.CharField(max_length=255)),
                ('public_access_token', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id_pedido', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_pedido', models.DateTimeField(auto_now_add=True)),
                ('pedido_datos', models.JSONField()),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
                'db_table': 'aplicacion_pedidos',
            },
        ),
        migrations.CreateModel(
            name='ProductoCategoria',
            fields=[
                ('id_categoria', models.AutoField(primary_key=True, serialize=False)),
                ('categoria_nombre', models.CharField(max_length=32, unique=True)),
                ('categoria_descripcion', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=32, unique=True)),
            ],
            options={
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
                'db_table': 'aplicacion_productos_categorias',
            },
        ),
        migrations.CreateModel(
            name='ProductoMarca',
            fields=[
                ('id_marca', models.AutoField(primary_key=True, serialize=False)),
                ('marca_nombre', models.CharField(max_length=32, unique=True)),
                ('marca_descripcion', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=32, unique=True)),
            ],
            options={
                'verbose_name': 'Marca',
                'verbose_name_plural': 'Marcas',
                'db_table': 'aplicacion_productos_marcas',
            },
        ),
        migrations.CreateModel(
            name='Tarjeta',
            fields=[
                ('id_tarjeta', models.AutoField(primary_key=True, serialize=False)),
                ('numero', models.PositiveBigIntegerField()),
                ('red', models.CharField(max_length=32)),
                ('tipo', models.CharField(max_length=32)),
                ('codigo_seguridad', models.PositiveSmallIntegerField()),
                ('fecha_caducidad', models.PositiveSmallIntegerField()),
                ('imagen', models.ImageField(upload_to='tarjetas_imagenes')),
                ('intereses', models.JSONField(null=True)),
            ],
            options={
                'verbose_name': 'Tarjeta',
                'verbose_name_plural': 'Tarjetas',
                'db_table': 'aplicacion_tarjetas',
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id_producto', models.AutoField(primary_key=True, serialize=False)),
                ('producto_nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre de producto')),
                ('descripcion', models.TextField()),
                ('imagen', models.ImageField(upload_to='productos_imagenes')),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('unidades_stock', models.PositiveBigIntegerField()),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aplicacion.productocategoria')),
                ('marca', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aplicacion.productomarca')),
            ],
            options={
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
                'db_table': 'aplicacion_productos',
            },
        ),
        migrations.CreateModel(
            name='PedidoPreferencia',
            fields=[
                ('id_preferencia', models.AutoField(primary_key=True, serialize=False)),
                ('preferencia_datos', models.JSONField()),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'aplicacion_pedidos_preferencias',
            },
        ),
        migrations.CreateModel(
            name='PedidoDetalle',
            fields=[
                ('id_pedido_detalle', models.AutoField(primary_key=True, serialize=False)),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('cantidad', models.PositiveBigIntegerField()),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='aplicacion.pedido')),
                ('producto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aplicacion.producto')),
            ],
            options={
                'verbose_name': 'Pedido detalle',
                'verbose_name_plural': 'Pedidos detalle',
                'db_table': 'aplicacion_pedidos_detalle',
            },
        ),
        migrations.CreateModel(
            name='CarritoCompra',
            fields=[
                ('id_carrito', models.AutoField(primary_key=True, serialize=False)),
                ('cantidad', models.PositiveBigIntegerField()),
                ('producto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='aplicacion.producto')),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Carrito de compra',
                'verbose_name_plural': 'Carrito de compras',
                'db_table': 'aplicacion_carrito_compras',
            },
        ),
    ]
