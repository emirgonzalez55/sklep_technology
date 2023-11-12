from aplicacion.models import ProductoCategoria, ProductoMarca

def contextos(request):
    categorias = ProductoCategoria.objects.all()
    marcas = ProductoMarca.objects.all()

    return {"categorias": categorias, "marcas": marcas}