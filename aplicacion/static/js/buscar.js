function filtro_busqueda(event) {
    var url = new URL(window.location);
    var parametro = event.target.getAttribute("name")
    
    if (event.type == "change") {
        var id = event.target.getAttribute("id")
        var filtro = document.getElementById(id).value
        url.searchParams.set(parametro,filtro) 
    }
    if (event.type == "click") {
        url.searchParams.delete(parametro)
    }
    if (event.type == "submit") {
        event.preventDefault();
        var id = event.target.getAttribute("id")
        var inputs = document.querySelectorAll("#"+id+" input");
        inputs.forEach(element => {
            url.searchParams.set(element.name,element.value) 
        });
    }
    window.location.href = url

}