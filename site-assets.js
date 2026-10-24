/* SVG images have no native loading=lazy. Hydrate them near their section. */
(() => {
  const load = image => {
    image.setAttribute('href', image.dataset.deferredHref);
    delete image.dataset.deferredHref;
  };
  const images = document.querySelectorAll('image[data-deferred-href]');
  if (!('IntersectionObserver' in window)) return images.forEach(load);
  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.querySelectorAll('image[data-deferred-href]').forEach(load);
    observer.unobserve(entry.target);
  }), {rootMargin:'350px'});
  new Set([...images].map(image => image.closest('svg'))).forEach(svg => observer.observe(svg));
})();
