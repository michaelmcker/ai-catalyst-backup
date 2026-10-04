/* Purposeful, one-pass explanations. All text is readable without motion. */
(() => {
 const reduced=matchMedia('(prefers-reduced-motion: reduce)');
 const overview=[...document.querySelectorAll('.quality-diagram')];
 overview.forEach(diagram=>{
  const svgs=[...diagram.querySelectorAll('svg')];let visible=false,seen=false,finished=false,timers=[];
  const stop=()=>{timers.forEach(clearTimeout);timers=[];};
  const sync=()=>{const paused=reduced.matches||document.body.classList.contains('motion-paused')||!visible||finished;svgs.forEach(svg=>{if(paused)svg.pauseAnimations?.();else svg.unpauseAnimations?.();});};
  const settle=()=>{stop();finished=true;diagram.dataset.flow='complete';sync();};
  new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(visible&&!seen){seen=true;if(reduced.matches||document.body.classList.contains('motion-paused'))settle();else{diagram.dataset.flow='inputs';timers.push(setTimeout(()=>diagram.dataset.flow='centre',1400),setTimeout(()=>diagram.dataset.flow='outputs',2900),setTimeout(settle,4800));}}else if(!visible&&seen)settle();sync();},{threshold:.3}).observe(diagram);
  reduced.addEventListener('change',settle);document.getElementById('motion-toggle')?.addEventListener('click',settle);document.addEventListener('visibilitychange',()=>{if(document.hidden)settle();});sync();
 });
 const reveals=[...document.querySelectorAll('.quality-section-head,.quality-command-intro,.solution-card,.quality-detail-row,.quality-delivery article')];
 if(!reduced.matches){const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('has-arrived');observer.unobserve(e.target);}}),{threshold:.12});reveals.forEach(el=>{el.classList.add('quality-enter');observer.observe(el);});}
 document.querySelectorAll('.decision-demo').forEach(demo=>{
  const buttons=[...demo.querySelectorAll('[data-decision-step]')],captions=[...demo.querySelectorAll('[data-decision-caption]')];
  let timer=0,step=0,seen=false;
  function stop(){clearTimeout(timer);timer=0;}
  function show(i){step=i;demo.dataset.decision=String(i);buttons.forEach((b,j)=>b.setAttribute('aria-pressed',String(i===j)));captions.forEach((p,j)=>p.hidden=i!==j);}
  function play(){stop();show(0);if(reduced.matches||document.body.classList.contains('motion-paused'))return;const next=()=>{if(document.hidden)return;if(step<2){show(step+1);timer=setTimeout(next,4800);}};timer=setTimeout(next,4800);}
  buttons.forEach((b,i)=>b.addEventListener('click',()=>{stop();show(i);}));
  new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting&&!seen){seen=true;play();}else if(!e.isIntersecting)stop();}),{threshold:.4}).observe(demo);
  reduced.addEventListener('change',stop);document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});document.getElementById('motion-toggle')?.addEventListener('click',stop);
 });
})();
