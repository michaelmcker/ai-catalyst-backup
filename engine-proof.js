/* Play the source demos only when a visitor chooses to watch. */
(() => {
  document.querySelectorAll('.proof-play').forEach(button => {
    button.addEventListener('click', () => {
      const frame = document.createElement('iframe');
      const id = button.dataset.video;
      if (!/^[\w-]{11}$/.test(id)) return;
      frame.src = `https://www.youtube-nocookie.com/embed/${id}?rel=0&autoplay=1&start=${Number(button.dataset.start)||0}`;
      frame.title = button.getAttribute('aria-label');
      frame.allow = 'autoplay; encrypted-media; picture-in-picture';
      frame.allowFullscreen = true;
      button.replaceWith(frame);
    });
  });
})();
