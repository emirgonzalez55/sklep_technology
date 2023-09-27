from django.urls import path
# from . import views
from aplicacion.views import Inicio, Registro, Loguut, Crear_Producto,Administrar_Productos, Vista_Productos,Buscar_Productos,Actualizar_Producto,EliminarProducto,Login,DetalleProducto
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('', Inicio.as_view(), name= 'inicio'),
    path('login', Login.as_view(), name='login'),
    path('registro', Registro.as_view(), name= 'registro'),
    path('logout', Loguut.as_view(), name= 'logout'),
    path('productos', Vista_Productos.as_view(), name= 'productos'),
    path('producto/<slug:slug>', DetalleProducto.as_view(), name= 'producto_detalle'),
    path('buscar', Buscar_Productos.as_view(), name= 'buscar'),
    path('administrar/productos', Administrar_Productos.as_view(), name='administrar_productos'),
    path('administrar/productos/agregar_producto', Crear_Producto.as_view(), name= 'agregar_producto'),
    path('administrar/productos/editar_producto/<int:pk>', Actualizar_Producto.as_view(), name= 'editar_producto'),
    path('administrar/productos/eliminar_producto/<int:pk>', EliminarProducto.as_view(), name= 'eliminar_producto'),   
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
