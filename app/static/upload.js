document.getElementById('file').addEventListener('change', function(e) {
  var form = document.querySelector('form');
  var request = new XMLHttpRequest();

  // Adicionar um ouvinte de evento para acompanhar o progresso do upload
  request.upload.addEventListener('progress', function(e) {
    var percentComplete = (e.loaded / e.total) * 100;
    document.querySelector('.progress-bar').style.width = percentComplete + '%';
  });

  // Configurar a requisição
  request.open('POST', form.action);
  request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

  // Enviar o formulário
  var formData = new FormData(form);
  request.send(formData);
});
