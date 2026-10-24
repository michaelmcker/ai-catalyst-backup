/* Give the hero first use of the connection; fetch other images near entry. */
(() => {
  'use strict';
  const images=[...document.querySelectorAll('img[data-deferred-src]')];
  if(!images.length)return;
  const hero=document.querySelector('[data-site-art="hero"] img');
  const pending=new Set(images);
  let active=false,observer=null,stallTimer=null;

  function load(image){
    const source=image.dataset.deferredSrc;
    if(!source)return;
    image.src=source;
    delete image.dataset.deferredSrc;
  }
  function activate(){
    if(active)return;
    active=true;
    if(stallTimer!==null){clearTimeout(stallTimer);stallTimer=null;}
    hero?.removeEventListener('load',activate);
    hero?.removeEventListener('error',activate);
    window.removeEventListener('scroll',activate);
    if(typeof IntersectionObserver!=='function'){
      images.forEach(load);pending.clear();return;
    }
    observer=new IntersectionObserver(entries=>{
      for(const entry of entries){
        if(!entry.isIntersecting||!pending.has(entry.target))continue;
        observer.unobserve(entry.target);
        load(entry.target);pending.delete(entry.target);
      }
      if(!pending.size)observer.disconnect();
    },{rootMargin:'300px',threshold:0});
    images.forEach(image=>observer.observe(image));
  }

  // Scrolling past the hero takes priority over waiting for its network load.
  // A stalled/failed hero can never leave the rest of the document unloaded.
  window.addEventListener('scroll',activate,{once:true,passive:true});
  stallTimer=setTimeout(activate,4000);
  if(hero&&!hero.complete){
    hero.addEventListener('load',activate,{once:true});
    hero.addEventListener('error',activate,{once:true});
  }else{
    queueMicrotask(activate);
  }
})();
