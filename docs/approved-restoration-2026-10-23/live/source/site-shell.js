(() => {
  'use strict';
  const header = document.querySelector('.masthead');
  if (!header) return;
  const toggle = header.querySelector('.masthead-toggle');
  const panel = header.querySelector('.masthead-panel');
  const scrim = header.querySelector('.masthead-scrim');
  const links = header.querySelector('.masthead-links');
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  header.querySelectorAll('.masthead-panel a').forEach(link => {
    if (link.getAttribute('href') === currentPage) link.setAttribute('aria-current', 'page');
  });
  const compact = matchMedia('(max-width: 1000px)');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let isOpen = false, pending = false, returnFocus, closeTimer;
  const background = [...document.querySelectorAll('main, .site-footer, .skip')];
  function updateHeader() {
    const collapsed = true; // One navigation presentation at every scroll position and breakpoint.
    header.classList.toggle('is-compact', collapsed);
    links.inert = collapsed;
    toggle.tabIndex = collapsed ? 0 : -1;
    pending = false;
  }
  function setOpen(open, restore = true) {
    clearTimeout(closeTimer);
    isOpen = open;
    toggle.setAttribute('aria-expanded', String(open));
    toggle.firstElementChild.textContent = open ? 'Close' : 'Menu';
    if (open) {
      returnFocus = document.activeElement;
      panel.hidden = false; scrim.hidden = false;
      panel.inert = false;
      // Allow the hidden panel to acquire its closed state before entry.
      requestAnimationFrame(() => header.classList.add('is-open'));
      document.documentElement.style.setProperty('--menu-scrollbar', `${window.innerWidth-document.documentElement.clientWidth}px`);
      document.body.classList.add('menu-is-open');
      background.forEach(el => { el.inert = true; });
      panel.querySelector('a').focus({preventScroll: true});
    } else {
      header.classList.remove('is-open');
      panel.inert = true;
      document.body.classList.remove('menu-is-open');
      document.documentElement.style.removeProperty('--menu-scrollbar');
      background.forEach(el => { el.inert = false; });
      if (restore) (returnFocus || toggle).focus({preventScroll:true});
      closeTimer = setTimeout(() => { panel.hidden = true; scrim.hidden = true; }, reduced.matches ? 0 : 340);
    }
    updateHeader();
  }
  toggle.addEventListener('click', () => setOpen(!isOpen));
  scrim.addEventListener('click', () => setOpen(false));
  panel.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setOpen(false, false)));
  document.addEventListener('keydown', event => {
    if (!isOpen) return;
    if (event.key === 'Escape') { event.preventDefault(); setOpen(false); }
    if (event.key === 'Tab') {
      const focusable = [...header.querySelectorAll('.masthead-logo, .masthead-toggle, .masthead-contact, .masthead-panel a')];
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  window.addEventListener('scroll', () => { if (!pending) { requestAnimationFrame(updateHeader); pending = true; } }, {passive:true});
  compact.addEventListener('change', updateHeader);
  updateHeader();
  document.querySelectorAll('.page-hero, .sub-hero').forEach(hero => {
    hero.addEventListener('pointermove', event => {
      if (event.pointerType === 'touch') return;
      const rect = hero.getBoundingClientRect();
      hero.style.setProperty('--pointer-x', `${((event.clientX-rect.left)/rect.width*100).toFixed(1)}%`);
      hero.style.setProperty('--pointer-y', `${((event.clientY-rect.top)/rect.height*100).toFixed(1)}%`);
    }, {passive:true});
  });
  const steps = document.querySelectorAll('.process-step, .approach-card');
  if (!reduced.matches && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('has-arrived'); observer.unobserve(entry.target); } });
    }, {threshold:.22, rootMargin:'0px 0px -4% 0px'});
    steps.forEach(step => { step.classList.add('will-arrive'); observer.observe(step); });
  }
})();
