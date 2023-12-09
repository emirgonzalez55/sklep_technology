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
            modal_cerrar("modal-producto")
            modal_aviso(response.mensaje,response.producto);
            recargar_tabla("tabla-productos");
        },
        error: function(error){
            console.log(error);
            form_error(error,"form-producto")
        }
    });
}
function form_categorias(){
    $.ajax({
        data: $('#form-categoria').serialize(),
        url: $('#form-categoria').attr('action'),
        type: $('#form-categoria').attr('method'),
        
        success: function(response){
            console.log(response);
            modal_aviso(response.mensaje,response.categoria);
            modal_cerrar("modal-categoria");
            recargar_tabla("tabla-categorias");
        },
        error: function(error){
            console.log(error);
            form_error(error,"form-categoria")
        }
    });
}
function form_marcas(){
    $.ajax({
        data: $('#form-marca').serialize(),
        url: $('#form-marca').attr('action'),
        type: $('#form-marca').attr('method'),
        
        success: function(response){
            console.log(response);
            modal_aviso(response.mensaje,response.marca);
            modal_cerrar("modal-marca");
            recargar_tabla("tabla-marcas");
        },
        error: function(error){
            console.log(error);
            form_error(error,"form-marca")
        }
    });
}
function form_error(errores,form){
    var campos = document.querySelectorAll("#"+form+" input,select,textarea");
    campos.forEach(campo => {
        $("#"+campo.name+"").empty();
    });
    let error = "";
    for (let item in errores.responseJSON.error){
        error = errores.responseJSON.error[item];
        $("#"+item).append(error); 
    }
}
// function error_form(errores){
//     $("#producto_nombre").empty();
//     $("#categoria").empty();
//     $("#marca").empty();
//     $("#precio_unitario").empty();
//     $("#unidades_stock").empty();
//     $("#descripcion").empty();
//     $("#imagen").empty();
//     let error = "";
//     for (let item in errores.responseJSON.error){
//         error = '<p>' + errores.responseJSON.error[item] + '</p>';
//         $("#"+item).append(error); 

//     }
// }
function modal_cerrar(modal){
    $("#"+modal+"").modal("hide");
    $("#"+modal+"").empty();
}
// function cerrar_modal(){
//     $("#modal-producto").modal("hide");
//     $("#modal-producto").empty();
// }
function modal_aviso(mensaje,item){
    $("#titulo-aviso").empty();
    $("#body-aviso").empty();
    $("#modal-aviso").modal("show");	
    $("#titulo-aviso").append(mensaje); 
    $("#body-aviso").append(item); 
}
function recargar_tabla(tabla){
    $("#"+tabla+"").load(" #"+tabla+" > *");
}
function modal_producto(url){
    $('#modal-producto').load(url, function () {
      $(this).modal("show");
  });
}
function modal_categoria(url){
    $('#modal-categoria').load(url, function () {
      $(this).modal("show");
  });
}
function modal_marca(url){
    $('#modal-marca').load(url, function () {
      $(this).modal("show");
  });
}

