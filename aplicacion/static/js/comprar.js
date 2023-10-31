function link_compra(producto) {
    animacion_boton("comprar-animacion","comprar");
    var cantidad = document.getElementById("cantidad").value

    setTimeout(function() {
        window.location.href = "/comprar/"+producto+"-cantidad="+cantidad+""; 
    }, 1200);
   
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
            }, 1200);
        },
        error: function(error){
            console.log(error);
            animacion_boton("carrito-animacion","carrito");
            setTimeout(function() {
                alert("Ya tienes este producto en el carrito")
            }, 1200);
            
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
    }, 1201);
}

// function animacion_compra(){
//     document.getElementById("barra-compra").classList.toggle("progress-bar");
//     document.getElementById("barra-compra").classList.toggle("progress-bar-animated");

//   }