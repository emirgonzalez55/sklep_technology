function modal_pedido(url){
    $('#modal-pedido').load(url, function () {
      $(this).modal("show");
  });
}