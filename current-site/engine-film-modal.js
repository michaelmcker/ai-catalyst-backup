(() => {
  const dialog = document.querySelector('.film-modal--engine');
  if (!dialog) return;
  const player = dialog.querySelector('.engine-film-player');
  document.querySelectorAll('.engine-film-link').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || typeof dialog.showModal !== 'function') return;
      const id = link.dataset.youtubeId;
      if (!/^[\w-]{11}$/.test(id)) return;
      event.preventDefault();
      const frame = document.createElement('iframe');
      frame.title = link.dataset.videoTitle;
      frame.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&playsinline=1`;
      frame.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      player.replaceChildren(frame);
      dialog.setAttribute('aria-label', link.dataset.videoTitle);
      dialog.showModal();
      document.body.classList.add('film-open');
      dialog.querySelector('.film-close').focus();
    });
  });
  dialog.querySelector('.film-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener('close', () => {
    player.replaceChildren();
    document.body.classList.remove('film-open');
  });
})();
