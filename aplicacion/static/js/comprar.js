function link_compra(producto) {
    animacion_boton("comprar-animacion","comprar");
    var cantidad = document.getElementById("cantidad").value

    setTimeout(function() {
        window.location.href = "/comprar/pago/"+producto+"-cantidad="+cantidad+"";
    }, 1000);

}

function agregar_carrito(producto){
    var cantidad = document.getElementById("cantidad").value
    var csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value
    $.ajax({
        data: { csrfmiddlewaretoken: csrfmiddlewaretoken },
        url: "/carrito/agregar/"+producto+"-"+cantidad+"",
        type: 'POST',

        success: function(response){
            console.log(response);
            animacion_boton("carrito-animacion","carrito");
            setTimeout(function() {
                window.location.href = "/carrito";
            }, 1000);
        },
        error: function(error){
            console.log(error);
            animacion_boton("carrito-animacion","carrito");
            setTimeout(function() {
                alert("Ya tienes este producto en el carrito")
            }, 1000);

        }
    });
}
function editar_carrito(carrito){
    var cantidad = document.getElementById("cantidad-"+carrito+"").value
    var csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value

    $.ajax({
        data: { csrfmiddlewaretoken: csrfmiddlewaretoken },
        url: "/carrito/actualizar/"+carrito+"-"+cantidad+"",
        type: 'POST',

        success: function(response){
            console.log(response);
            recargar_carrito();
        },
        error: function(error){
            console.log(error);
        }
    });
}
function quitar_carrito(carrito){
    var csrfmiddlewaretoken = document.getElementsByName("csrfmiddlewaretoken")[0].value

    $.ajax({
        data: { csrfmiddlewaretoken: csrfmiddlewaretoken },
        url: "carrito/eliminar/"+carrito+"",
        type: 'POST',

        success: function(response){
            console.log(response);
            recargar_carrito();
        },
        error: function(error){
            console.log(error);
        }
    });
}
function recargar_carrito(){
    $("#carrito").load(" #carrito > *");
}
function animacion_boton(animacion, boton){
    document.getElementById(animacion).classList.toggle("spinner-border");
    document.getElementById(boton).classList.toggle("disabled");
    setTimeout(function() {
        document.getElementById(animacion).classList.toggle("spinner-border");
        document.getElementById(boton).classList.toggle("disabled");
    }, 1000);
}

function validaciones_color_valid(input) {
    input.classList.add("is-valid");
    if (input.classList.contains('is-invalid') ) {
        input.classList.remove("is-invalid");
    }
}
function validaciones_color_invalid(input) {
    input.classList.add("is-invalid");
    if (input.classList.contains('is-valid') ) {
        input.classList.remove("is-valid");
    }
}
function comprobar_form_metodo_pago(){
    nombre_valid = /\w{1,100}\s*/;
    tarjeta_valid = /^\d{15,16}$/;
    dni_valid = /^\d{1,8}$/;
    fecha_valid = /^\d{4,4}$/;
    codigo_valid = /^\d{3,4}$/;
    var inputs = document.querySelectorAll("#form-metodo-pago input");
    var nombre = document.getElementById("id_tarjeta_titular");
    var tarjeta = document.getElementById("id_tarjeta_numero");
    var dni = document.getElementById("id_dni");
    var tarjeta_fecha = document.getElementById("id_tarjeta_fecha");
    var tarjeta_codigo = document.getElementById("id_tarjeta_codigo");
    var boton = document.getElementById("comprar-metodo-pago")

    if (nombre_valid.test(nombre.value) && tarjeta_valid.test(tarjeta.value) && dni_valid.test(dni.value) && fecha_valid.test(tarjeta_fecha.value) && codigo_valid.test(tarjeta_codigo.value)) {
        if (boton.classList.contains("disabled")) {
            boton.classList.toggle("disabled");
        }
    }else{
        if (!boton.classList.contains("disabled")) {
            boton.classList.add("disabled");
        }
    }
  

    inputs.forEach(input => {
        input.addEventListener("blur", function() {
            if (input.name == "tarjeta_numero") {
                if (!tarjeta_valid.test(input.value)) {
                    validaciones_color_invalid(input)
                }else{
                    validaciones_color_valid(input)
                }
            }
            if (input.name == "dni") {
                if (!dni_valid.test(input.value)) {
                    validaciones_color_invalid(input)
                }else{
                    validaciones_color_valid(input)
                }
            }
            if (input.name == "tarjeta_fecha") {
                if (!fecha_valid.test(input.value)) {
                    validaciones_color_invalid(input)
                }else{
                    validaciones_color_valid(input)
                }
            }
            if (input.name == "tarjeta_codigo") {
                if (!codigo_valid.test(input.value)) {
                    validaciones_color_invalid(input)
                }else{
                    validaciones_color_valid(input)
                }
            }
            if (input.name == "tarjeta_titular") {
                if (!nombre_valid.test(input.value)) {
                    validaciones_color_invalid(input)
                }else{
                    validaciones_color_valid(input)
                }
            }
        });

    });
}
function comprar_metodo_pago(){
    mostrar_modal("modal-cargar")
    $.ajax({
        data: $('#form-metodo-pago').serialize(),
        type: $('#form-metodo-pago').attr('method'),
        success: function(response){
            console.log(response);
            setTimeout(() => {
                cerrar_modal("modal-cargar")
                window.location.href = response.url;
            }, 1000);

        },
        error: function(error){
            console.log(error);
            setTimeout(() => {
                cerrar_modal("modal-cargar")
                // error_form(error);
                modal_aviso(error.responseJSON.mensaje,error.responseJSON.error);
            }, 1000);
            
        }
    });
}
function mostrar_modal(modal){
    $("#"+modal+"").modal("show");
}
function cerrar_modal(modal){
    $("#"+modal+"").modal("hide");
}
function error_form(errores){
    $("#tarjeta_titular").empty();
    $("#dni").empty();
    $("#tarjeta_numero").empty();
    $("#tarjeta_fecha").empty();
    $("#tarjeta_codigo").empty();
    let error = "";
    for (let item in errores.responseJSON.error){
        error =  errores.responseJSON.error[item];
        $("#"+item).append(error);

    }
}


function comprar_metodo_pago_cuotas(){
    mostrar_modal("modal-cargar")
    $.ajax({
        data: $('#form-cuotas').serialize(),
        type: $('#form-cuotas').attr('method'),
        success: function(response){
            console.log(response);
            setTimeout(() => {
                cerrar_modal("modal-cargar")
                window.location.href = response.url;
            }, 1000);

        },
        error: function(error){
            console.log(error);
        }
    });
}
function comprar_confirmar(){
    mostrar_modal("modal-comprar")
    $.ajax({
        data: $('#form-comprar-confirmar').serialize(),
        type: $('#form-comprar-confirmar').attr('method'),
        success: function(response){
            console.log(response);
            setTimeout(() => {
                cerrar_modal("modal-comprar")
                window.location.href = response.url;
            }, 1500);

        },
        error: function(error){
            console.log(error);
            setTimeout(() => {
                cerrar_modal("modal-comprar")
                window.location.href = error.responseJSON.url;
            }, 1500);
        }
    });
}
function modal_aviso(mensaje,error){
    $("#titulo-aviso").empty();
    $("#body-aviso").empty();
    $("#modal-aviso-compra").modal("show");	
    $("#titulo-aviso").append(mensaje); 
    $("#body-aviso").append(error); 
}