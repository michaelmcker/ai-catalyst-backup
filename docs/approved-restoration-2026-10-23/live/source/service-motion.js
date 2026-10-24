/* Diagonal card entrances follow native scroll. Copy and routes work without JS. */
(() => {
  const slots = [...document.querySelectorAll('.service-slot')];
  if (!slots.length) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const compact = matchMedia('(max-width: 800px)');
  let frame = 0;
  function draw() {
    frame = 0;
    const height = innerHeight;
    slots.forEach((slot, index) => {
      const card = slot.firstElementChild;
      const top = slot.getBoundingClientRect().top;
      const progress = Math.max(0, Math.min(1, (height * .94 - top) / (height * .42)));
      const remaining = reduced.matches ? 0 : Math.pow(1 - progress, 2);
      const x = remaining * (compact.matches ? 8 : 42);
      const y = remaining * (compact.matches ? 32 : 80);
      const rotation = remaining * (index % 2 ? -3.8 : 3.2);
      card.style.transform = `translate3d(${x}px,${y}px,0) rotate(${rotation}deg)`;
    });
  }
  function queue() {
    if (!frame && !document.hidden) frame = requestAnimationFrame(draw);
  }
  addEventListener('scroll', queue, {passive:true});
  addEventListener('resize', queue, {passive:true});
  reduced.addEventListener('change', queue);
  document.addEventListener('visibilitychange', queue);
  draw();
})();
