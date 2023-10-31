function form_productos(){
    var data = new FormData($('#form-producto')[0])
    $.ajax({
        data: data,
        url: $('#form-producto').attr('action'),
        type: $('#form-producto').attr('method'),
        processData: false, 
        contentType: false,
        success: function(response){
            console.log(response);
            cerrar_modal();
            modal_aviso(response.mensaje,response.producto);
            recargar_tabla();
        },
        error: function(error){
            console.log(error);
            error_form(error); 
        }
    });
}
function error_form(errores){
    $("#producto_nombre").empty();
    $("#categoria").empty();
    $("#marca").empty();
    $("#precio_unitario").empty();
    $("#unidades_stock").empty();
    $("#descripcion").empty();
    $("#imagen").empty();
    let error = "";
    for (let item in errores.responseJSON.error){
        error = '<p>' + errores.responseJSON.error[item] + '</p>';
        $("#"+item).append(error); 

    }
}
function cerrar_modal(){
    $("#modal-producto").modal("hide");
    $("#modal-producto").empty();
  }
function modal_aviso(mensaje,producto){
    $("#titulo-aviso").empty();
    $("#body-aviso").empty();
    $("#modal-aviso").modal("show");	
    $("#titulo-aviso").append(mensaje); 
    $("#body-aviso").append(producto); 
  }
function recargar_tabla(){
    $("#tabla-productos").load(" #tabla-productos > *");
}
function modal_producto(url){
    $('#modal-producto').load(url, function () {
      $(this).modal("show");
  });
}
