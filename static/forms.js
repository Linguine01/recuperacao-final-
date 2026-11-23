document.addEventListener('submit', (event) => {
  const mensagem = event.target.dataset.confirm;
  if (mensagem && !window.confirm(mensagem)) {
    event.preventDefault();
  }
});
