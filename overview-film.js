(() => {
  const dialog = document.querySelector('.film-modal--youtube');
  if (!dialog) return;
  const poster = dialog.querySelector('.service-film__play');
  const play = () => {
    dialog.showModal();
    document.body.classList.add('film-open');
    poster.click();
  };
  document.querySelectorAll('.hero-film-button').forEach(button => button.addEventListener('click', play));
  dialog.querySelector('.film-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    dialog.querySelector('iframe')?.remove();
    poster.hidden = false;
    document.body.classList.remove('film-open');
  });
})();
