function form_editar_perfil(){
    $.ajax({
        data: $('#form-editar-perfil').serialize(),
        type: $('#form-editar-perfil').attr('method'),
        url: $('#form-editar-perfil').attr('action'),
        success: function(response){
            console.log(response);

        },
        error: function(error){
            console.log(error);
            form_error(error,"form-editar-perfil");
        }
    });
}
function form_cambiar_password(){
    $.ajax({
        data: $('#form-cambiar-password').serialize(),
        type: $('#form-cambiar-password').attr('method'),
        url: $('#form-cambiar-password').attr('action'),
        success: function(response){
            console.log(response);
            alert(response.mensaje)
        },
        error: function(error){
            console.log(error);
            form_error(error,"form-cambiar-password");
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
// function error_form_cambiar_password(errores){
//     $("#old_password").empty();
//     $("#new_password1").empty();
//     $("#new_password2").empty();
//     let error = "";
//     for (let item in errores.responseJSON.error){
//         error = '<p>' + errores.responseJSON.error[item] + '</p>';
//         $("#"+item).append(error); 

//     }
// }
// function error_form(errores){
//     $("#usuario").empty();
//     $("#email").empty();
//     $("#nombre").empty();
//     $("#apellido").empty();
//     let error = "";
//     for (let item in errores.responseJSON.error){
//         error = '<p>' + errores.responseJSON.error[item] + '</p>';
//         $("#"+item).append(error); 

//     }
// }

function modal_usuario(url){
    $('#modal-usuario').load(url, function () {
      $(this).modal("show");
  });
}
function form_usuario(){
    $.ajax({
        data: $('#form-usuario').serialize(),
        type: $('#form-usuario').attr('method'),
        url: $('#form-usuario').attr('action'),
        success: function(response){
            console.log(response);
            modal_aviso(response.mensaje,response.usuario);
            modal_cerrar("modal-usuario");
            recargar_tabla("tabla-usuarios");
        },
        error: function(error){
            console.log(error);
            form_error(error,"form-usuario");
        }
    });
}
function modal_perfil(url){
    $('#modal-perfil').load(url, function () {
      $(this).modal("show");
  });
}
function modal_aviso(mensaje,usuario){
    $("#titulo-aviso").empty();
    $("#body-aviso").empty();
    $("#modal-aviso").modal("show");	
    $("#titulo-aviso").append(mensaje); 
    $("#body-aviso").append(usuario); 
}
function modal_cerrar(modal){
    $("#"+modal+"").modal("hide");
    $("#"+modal+"").empty();
}
function recargar_tabla(tabla){
    $("#"+tabla+"").load(" #"+tabla+" > *");
}