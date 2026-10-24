/* Keep each mobile exclusion and its original illustration in one coordinate
   system. Font/viewport changes may grow the copy, never move the picture. */
(() => {
 'use strict';
 const phone=matchMedia('(max-width:700px)');
 const profiles={
  'company-knight':{right:.15,outline:[[0,1],[.03,.7422],[.06,.6478],[.09,.625],[.12,.5944],[.15,.5859],[.18,.5664],[.21,.5605],[.24,.5553],[.27,.5553],[.30,.5553],[.33,.5462],[.36,.5326],[.39,.5326],[.42,.5352],[.45,.5352],[.48,.5462],[.51,.5579],[.54,.5684],[.57,.5762],[.60,.5859],[.63,.5911],[.66,.5664],[.69,.5449],[.72,.5124],[.75,.4915],[.78,.4688],[.81,.4531],[.84,.4427],[.87,.4427],[.90,.4427],[.93,.502],[.96,1],[.99,1],[1,1]]},
  kneeler:{right:.15,horizon:.58,outline:[[0,1],[.04,.66],[.17,.635],[.26,.61],[.42,.587],[.55,.548],[.58,.54]]},
  portrait:{right:.05,horizon:.69,outline:[[0,.62],[.11,.62],[.22,.62],[.35,.62],[.49,.62],[.60,.62],[.69,.58]]}
 };
 const properties=['--mobile-wrap-width','--mobile-wrap-height','--mobile-wrap-left','--mobile-wrap-top','--mobile-wrap-shape','--mobile-wrap-space-height'];
 for(const hero of document.querySelectorAll('[data-hero-subject]')){
  const profile=profiles[hero.dataset.heroSubject];if(!profile)continue;
  const heading=hero.querySelector('h1'),copy=hero.querySelector('.page-hero__copy');
  const space=hero.querySelector('.hero-mobile-subject-space'),image=hero.querySelector('.page-hero__art img');
  if(!heading||!copy||!space||!image)continue;
  let pending=0;
  const set=(name,value)=>{if(hero.style.getPropertyValue(name)!==value)hero.style.setProperty(name,value);};
  function measure(){
   pending=0;
   if(!phone.matches){properties.forEach(name=>hero.style.removeProperty(name));delete hero.dataset.mobileWrap;return;}
   const bounds=hero.getBoundingClientRect();if(!bounds.width)return;
   const naturalWidth=image.naturalWidth||Number(image.getAttribute('width'));
   const naturalHeight=image.naturalHeight||Number(image.getAttribute('height'));
   if(!naturalWidth||!naturalHeight)return;
   const width=Math.min(bounds.width*1.3,560),height=width*naturalHeight/naturalWidth;
   const left=bounds.width-width+Math.min(bounds.width*profile.right,profile.right===.05?20:84);
   set('--mobile-wrap-width',width.toFixed(3)+'px');
   set('--mobile-wrap-height',height.toFixed(3)+'px');
   const spaceHeight=height+40;
   set('--mobile-wrap-space-height',spaceHeight.toFixed(3)+'px');
   set('--mobile-wrap-left',left.toFixed(3)+'px');
   // The float follows the rendered h1. Its measured top is also the image's
   // top, rather than a percentage of the copy's changing overall height.
   const exclusion=space.getBoundingClientRect();
   set('--mobile-wrap-top',(exclusion.top-bounds.top).toFixed(3)+'px');
   const localLeft=bounds.left+left-exclusion.left;
   const contour=profile.outline.map(([y,x])=>[Math.max(0,Math.min(exclusion.width,localLeft+x*width-18)),y*height]);
   if(profile.horizon){contour.push([0,profile.horizon*height],[0,spaceHeight]);}
   const points=[[exclusion.width,0],[exclusion.width,spaceHeight],...contour.slice().reverse()];
   set('--mobile-wrap-shape','polygon('+points.map(([x,y])=>x.toFixed(3)+'px '+y.toFixed(3)+'px').join(',')+')');
   hero.dataset.mobileWrap='ready';
  }
  function request(){if(!pending)pending=requestAnimationFrame(measure);}
  const observer=new ResizeObserver(request);observer.observe(hero);observer.observe(heading);
  phone.addEventListener('change',request);
  image.addEventListener('load',request);
  window.addEventListener('resize',request,{passive:true});
  document.fonts?.ready.then(request);
  request();
 }
})();
