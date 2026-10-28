(() => {
  document.querySelectorAll('.service-film__play[data-youtube-id]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      const id = link.dataset.youtubeId;
      if (!/^[\w-]{11}$/.test(id)) return;
      event.preventDefault();
      if (link.hidden) return;
      const frame = document.createElement('iframe');
      frame.title = link.dataset.videoTitle;
      frame.src = `https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0&playsinline=1`;
      frame.allow = 'autoplay; encrypted-media; fullscreen; picture-in-picture';
      frame.allowFullscreen = true;
      frame.referrerPolicy = 'strict-origin-when-cross-origin';
      link.hidden = true;
      link.closest('.service-film').append(frame);
      frame.focus();
    });
  });
})();
