/* One explanation per visual. Readable without scripting; no scroll capture. */
(() => {
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 document.querySelectorAll('.engine-story').forEach(story=>{
  const buttons=[...story.querySelectorAll('[data-story-step]')];
  if(!buttons.length)return; // Native visual playback does not need step controls.
  const captions=[...story.querySelectorAll('[data-story-caption]')];
  const visual=story.querySelector('#signals,#allocation,#chat-scene');
  let timer=0,index=0,seen=false;
  function stop(){clearTimeout(timer);timer=0;}
  function show(next,instant=false){
   index=next;story.classList.toggle('instant-change',instant);
   buttons.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===next)));
   captions.forEach((p,i)=>p.hidden=i!==next);
   if(visual){if(visual.id!=="signals")visual.dataset.storyTime=buttons[next].dataset.visualTime;visual.dataset.activeStory=String(next);visual.dispatchEvent(new Event("storychange"));}
  }
  function play(){stop();show(0);if(reduced.matches)return;
   const advance=()=>{if(document.hidden){stop();return;}if(index<2){show(index+1);timer=setTimeout(advance,3400);}};
   timer=setTimeout(advance,3400);
  }
  buttons.forEach((b,i)=>b.addEventListener('click',e=>{stop();show(i,e.detail===0||reduced.matches);}));
  story.querySelector('.story-replay')?.addEventListener('click',play);
  new IntersectionObserver(entries=>{entries.forEach(e=>{
   if(e.isIntersecting&&!seen){seen=true;play();}else if(!e.isIntersecting)stop();
  });},{threshold:.35}).observe(story);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  reduced.addEventListener('change',()=>{stop();show(index,true);});
 });
 const process=document.querySelector('.process-story');
 if(process){
  const points=[...process.querySelectorAll('.quick-engagement-steps li')];
  const dot=process.querySelector('.process-dot'),line=process.querySelector('.process-line'),track=process.querySelector('.process-track');
  let seen=false,timer=0,current=0;
  function show(i){current=i;points.forEach((p,j)=>p.classList.toggle('process-current',i===j));
   if(dot)dot.style.transform='translateX('+((track.clientWidth-10)*i/2)+'px)';
   if(line)line.style.transform='scaleX('+i/2+')';
  }
  new ResizeObserver(()=>show(current)).observe(process);
  new IntersectionObserver(entries=>entries.forEach(e=>{
   if(e.isIntersecting&&!seen){seen=true;show(0);if(!reduced.matches)timer=setTimeout(()=>{show(1);timer=setTimeout(()=>show(2),2300);},2300);else show(2);}
   else if(!e.isIntersecting&&seen){clearTimeout(timer);show(2);}
  }),{threshold:.35}).observe(process);
  reduced.addEventListener('change',()=>{clearTimeout(timer);show(2);});
 }
})();
