from django.urls import path
# from . import views
from aplicacion.views import InicioVista, RegistroVista, LoguutVista, CrearProductoVista,AdministrarProductosVista, ProductosVista,BuscarProductosVista,ActualizarProductoVista,EliminarProductoVista,LoginVista,DetalleProductoVista,ComprarVista,AgregarCarritoVista,CarritoVista,ActualizarCarritoVista, EliminarCarritoVista,ComprarCarritoVista,ComprarMercadoPagoVista
from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    path('', InicioVista.as_view(), name= 'inicio'),
    path('login', LoginVista.as_view(), name='login'),
    path('registro', RegistroVista.as_view(), name= 'registro'),
    path('logout', LoguutVista.as_view(), name= 'logout'),
    path('productos', ProductosVista.as_view(), name= 'productos'),
    path('productos/<str:filtro>/<str:valor>', ProductosVista.as_view(), name= 'productos_filtro'),
    path('producto/<slug:slug>', DetalleProductoVista.as_view(), name= 'producto_detalle'),
    path('buscar', BuscarProductosVista.as_view(), name= 'buscar'),
    path('comprar/<slug:producto_slug>-cantidad=<int:cantidad>', ComprarVista.as_view(), name='comprar'),
    path('comprar/carrito', ComprarCarritoVista.as_view(), name='comprar_carrito'),
    path('comprar/mercadopago/<int:usuario>', csrf_exempt(ComprarMercadoPagoVista.as_view()), name='comprar_mp'),
    path('carrito', CarritoVista.as_view(), name='carrito'),
    path('carrito/agregar/<int:producto>-<int:cantidad>', AgregarCarritoVista.as_view(), name='agregar_carrito'),
    path('carrito/actualizar/<int:producto>-<int:cantidad>', ActualizarCarritoVista.as_view(), name='actualizar_carrito'),
    path('carrito/eliminar/<int:producto>', EliminarCarritoVista.as_view(), name='quitar_carrito'),
    path('administrar/productos', AdministrarProductosVista.as_view(), name='administrar_productos'),
    path('administrar/productos/agregar_producto', CrearProductoVista.as_view(), name= 'agregar_producto'),
    path('administrar/productos/editar_producto/<int:pk>', ActualizarProductoVista.as_view(), name='editar_producto'),
    path('administrar/productos/eliminar_producto/<int:pk>', EliminarProductoVista.as_view(), name='eliminar_producto'),   
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
