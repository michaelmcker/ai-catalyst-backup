(() => {
'use strict';
// Local design preview. No tracking, form transport or persistent client data.
const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const reduced = matchMedia('(prefers-reduced-motion: reduce)');
let paused = reduced.matches;
const toggle = $('#motion-toggle');
function setMotion(value) {
  paused = value;
  document.body.classList.toggle('motion-paused', paused);
  document.body.classList.toggle('js-motion', !paused);
  if(toggle) toggle.innerHTML = paused ? 'Enable motion <span aria-hidden="true">▷</span>' : 'Pause motion <span aria-hidden="true">Ⅱ</span>';
  toggle?.setAttribute('aria-pressed', String(paused));
  if (paused) $$('.reveal').forEach(el => el.classList.add('seen'));
  wake();
}
toggle?.addEventListener('click', () => setMotion(!paused));
reduced.addEventListener('change', e => setMotion(e.matches));
// Stage repeated proof and footer elements before the shared observer starts.
const stagedRevealSelectors=['.experience h2','.experience-context','.footer-title','.footer-directory>p','.footer-directory nav','.footer-art','.footer-bottom'];
stagedRevealSelectors.forEach(selector=>$$(selector).forEach((el,index)=>{el.classList.add('reveal');el.style.transitionDelay=`${index*.09}s`}));
$$('.logo').forEach((el,index)=>{el.classList.add('reveal');el.style.transitionDelay=`${Math.min(index*.065,.52)}s`});


// Mask each visual line without imposing fixed line breaks on responsive copy.
$$('.intro .reveal:not(.approach-card)').forEach(el=>{
 const text=el.textContent.trim();el.setAttribute('aria-label',text);el.textContent='';el.classList.add('line-reveal');
 text.split(/\s+/).forEach((word,i)=>{if(i)el.append(' ');const mask=document.createElement('span');mask.className='word-mask';mask.setAttribute('aria-hidden','true');const inner=document.createElement('span');inner.textContent=word;mask.append(inner);el.append(mask)});
 const measure=()=>{let previous=-1,line=-1;[...el.children].forEach(mask=>{if(mask.offsetTop!==previous){previous=mask.offsetTop;line++}mask.style.setProperty('--line-delay',`${line*.14}s`)})};
 new ResizeObserver(measure).observe(el);measure();
});
const revealObserver = new IntersectionObserver(entries => entries.forEach(e => {if(e.isIntersecting&&e.intersectionRatio>=.03){e.target.classList.add('seen');revealObserver.unobserve(e.target)}}),{rootMargin:'0px 0px 12% 0px',threshold:.03});
$$('.reveal:not(.approach-card)').forEach(el=>revealObserver.observe(el));
// Process entrances share the same timing and viewport trigger in site-shell.js.
$$('details').forEach(el=>el.addEventListener('toggle',()=>{if(el.open&&!paused)el.querySelector('.detail-copy').animate([{opacity:0,transform:'translateY(8px)'},{opacity:1,transform:'none'}],{duration:300,easing:'ease-out'})}));
$$('.topic-link').forEach(link=>link.addEventListener('click',()=>{const field=$('[name="priority"]');if(field&&!field.value)field.value=`I’d like to discuss ${link.dataset.topic.toLowerCase()}. `}));
function openDialog(id){const d=$(id);d.showModal();document.body.classList.add('modal-open');}
if ($('#people-open')) $('#people-open').onclick=()=>openDialog('#people-dialog');
if($('#notes-open'))$('#notes-open').onclick=()=>openDialog('#notes-dialog');
$$('dialog').forEach(d=>{const close=d.querySelector('.dialog-close');if(close)close.onclick=()=>d.close();d.addEventListener('close',()=>document.body.classList.remove('modal-open'));d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close()}})});
$('.dialog-contact').onclick=()=>$('#people-dialog').close();

// One shared, visibility-aware clock. All continuous functions have periodic endpoints.
const animations=[];let frame=0,last=0;
function wake(){if(!frame&&!document.hidden)frame=requestAnimationFrame(tick)}
function tick(now){frame=0;if(last&&now-last<32){frame=requestAnimationFrame(tick);return}const dt=last?Math.min((now-last)/1000,.05):0;last=now;let visible=false;for(const a of animations){if(!a.visible)continue;visible=true;if(!paused)a.time+=dt;a.draw(paused?a.rest:a.time,dt,paused)}if(visible&&!paused&&!document.hidden)frame=requestAnimationFrame(tick)}
const updateAnimationVisibility=(entries,minRatio=0)=>{for(const e of entries){const a=animations.find(x=>x.el===e.target);if(a){a.visible=e.isIntersecting&&e.intersectionRatio>=minRatio;if(a.visible)wake()}}};
const visibility = new IntersectionObserver(entries=>updateAnimationVisibility(entries,.25),{rootMargin:'0px 0px -8% 0px',threshold:.25});
const ambientVisibility = new IntersectionObserver(entries=>updateAnimationVisibility(entries,0),{rootMargin:'80px',threshold:0});
function addAnimation(el,draw,rest=3,options={}){const a={el,draw,time:0,rest,visible:false};animations.push(a);(options.continuous?ambientVisibility:visibility).observe(el);return a}
document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;last=0}else wake()});
const tau=Math.PI*2;
const clamp=(n,a=0,b=1)=>Math.max(a,Math.min(b,n));
const ease=n=>1-Math.pow(1-clamp(n),3);
function canvasContext(canvas,w,h){const ctx=canvas.getContext('2d');function size(){const width=canvas.getBoundingClientRect().width;const dpr=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(width*dpr);canvas.height=Math.round(width*h/w*dpr);ctx.setTransform(canvas.width/w,0,0,canvas.height/h,0,0);wake()}new ResizeObserver(size).observe(canvas);size();return ctx}

// Layered creator signals: stable reference curves, flowing foreground points,
// and slower, smaller background particles at several depths.
const signalCanvas=$('#signals'), sx=canvasContext(signalCanvas,720,390);
const signalNames=['Creators','Video','Social','Live','Reviews','Communities'];
const peakX=[.55,.62,.43,.49,.55,.47],peakAmp=[-38,-28,18,-27,-21,-32];
function signalPeak(row,t){return peakX[row]+.022*Math.sin(t*Math.PI*2/18+row*.65)}
function signalY(x,row,t=0){
 const center=signalPeak(row,t),breath=1+.22*Math.sin(t*Math.PI*2/14+row*.8);
 const width=.078+.009*Math.sin(t*Math.PI*2/20+row);
 const main=peakAmp[row]*breath*Math.exp(-Math.pow((x-center)/width,2));
 const shoulder=(row%2?-12:8)*(1+.16*Math.sin(t*.35+row))*Math.exp(-Math.pow((x-(row%2?.11:.38))/.1,2));
 const trough=(row>3?17:4)*Math.exp(-Math.pow((x-.63)/.085,2));
 return 55+row*55+main+shoulder+trough+1.5*Math.sin(x*18+row)*Math.sin(Math.PI*x);
}
const signalParticles=Array.from({length:6},(_,row)=>Array.from({length:115},(_,i)=>{
 const depth=i%3,seed=Math.sin(i*127.1+row*311.7)*43758.5453,random=seed-Math.floor(seed);
 return{phase:(i*.61803398875+row*.17)%1,depth,radius:[.85,1.3,1.9][depth]+random*.35,offset:(random-.5)*[58,34,6][depth],speed:[1/32,1/24,1/16][depth],alpha:[.20,.40,.73][depth]};
}));
// A separate drifting layer sits behind the established foreground chart.
const signalCloud=Array.from({length:210},(_,i)=>({x:(i*.61803398875)%1,y:25+((i*97)%330),radius:.65+(i%5)*.27,alpha:.11+(i%4)*.045}));
function drawSignals(t){
 sx.clearRect(0,0,720,390);sx.font='16px "Helvetica Neue",Arial';sx.textBaseline='middle';
 const left=108,width=596,anchors=[];
 for(const p of signalCloud){const x=((p.x-t/48)%1+1)%1;const edge=Math.min(clamp(x*12),clamp((1-x)*12));sx.globalAlpha=p.alpha*edge;sx.fillStyle='#4d83e9';sx.beginPath();sx.arc(left+x*width,p.y+6*Math.sin(p.x*12),p.radius,0,tau);sx.fill();}sx.globalAlpha=1;
 for(let row=0;row<6;row++){
  const base=55+row*55;sx.fillStyle='#5279c6';sx.fillText(signalNames[row],0,base);
  // Faint far-field dots extend through the whole composition, not just the right edge.
  for(const p of signalParticles[row]){if(p.depth===2)continue;const x=(p.phase+t*p.speed)%1;const edge=Math.min(clamp(x*18),clamp((1-x)*12));
   const settle=p.offset*(.7+.3*Math.sin(x*Math.PI));sx.globalAlpha=p.alpha*edge;sx.fillStyle='#3777ed';sx.beginPath();sx.arc(left+x*width,signalY(x,row,t)+settle,p.radius,0,tau);sx.fill();}
  sx.globalAlpha=1;const fade=sx.createLinearGradient(left,0,left+width,0);fade.addColorStop(0,'#7ba8fa');fade.addColorStop(.65,'#4174f6');fade.addColorStop(1,'#b2d0fb');sx.strokeStyle=fade;sx.lineWidth=1.35;sx.beginPath();
  for(let i=0;i<=220;i++){const x=i/220,y=signalY(x,row,t);i?sx.lineTo(left+x*width,y):sx.moveTo(left,y)}sx.stroke();
  for(const p of signalParticles[row]){if(p.depth!==2)continue;const x=(p.phase+t*p.speed)%1;const edge=Math.min(clamp(x*22),clamp((1-x)*10));sx.globalAlpha=p.alpha*edge;sx.fillStyle='#205af2';sx.beginPath();sx.arc(left+x*width,signalY(x,row,t)+p.offset,p.radius,0,tau);sx.fill();}
  sx.globalAlpha=1;if([0,1,3,4].includes(row))anchors.push([left+signalPeak(row,t)*width,signalY(signalPeak(row,t),row,t)]);
 }
 sx.strokeStyle='#3d6cff';sx.lineWidth=1;sx.setLineDash([2,5]);sx.beginPath();anchors.forEach(([x,y],i)=>{if(i){sx.lineTo(x,anchors[i-1][1]);sx.lineTo(x,y)}else sx.moveTo(x,y)});sx.stroke();sx.setLineDash([]);
 for(const[x,y]of anchors){sx.fillStyle='#edf7ff';sx.strokeStyle='#103fea';sx.lineWidth=1.8;sx.beginPath();sx.arc(x,y,7,0,tau);sx.fill();sx.stroke();sx.fillStyle='#245aff';sx.beginPath();sx.arc(x,y,2,0,tau);sx.fill();}
}
drawSignals(1.5);addAnimation(signalCanvas,drawSignals,1.5);

// One background field crosses both capability rows, moving right to left.
const wall=$('.signal-wall'),wx=wall.getContext('2d');
const wallDots=Array.from({length:580},(_,i)=>({x:(i*.61803398875)%1,y:(i*.754877666)%1,r:.7+(i%4)*.35,a:.07+(i%5)*.026}));
addAnimation(wall,(t)=>{const r=wall.getBoundingClientRect(),w=Math.round(r.width),h=Math.round(r.height);if(wall.width!==w||wall.height!==h){wall.width=w;wall.height=h}wx.clearRect(0,0,w,h);for(const p of wallDots){const x=((p.x-t/65)%1+1)%1;const edge=Math.min(clamp(x*12),clamp((1-x)*12),clamp(p.y*10),clamp((1-p.y)*10));wx.globalAlpha=p.a*edge;wx.fillStyle='#447cdf';wx.beginPath();wx.arc(x*w,p.y*h,p.r,0,tau);wx.fill()}wx.globalAlpha=1},0,{continuous:true});

const ns='http://www.w3.org/2000/svg';
// Chat sequence: left question, right reply, dotted connections, three staggered options.
const chat=$('#chat-scene');
if(chat){const bubbles=[...chat.querySelectorAll('.bubble')],products=[...chat.querySelectorAll('.product')], connectors=chat.querySelector('.chat-connectors');
const defs=document.createElementNS(ns,'defs');defs.innerHTML='<clipPath id="connector-mask"><rect id="connector-window" x="0" y="190" width="620" height="0"/></clipPath>';chat.prepend(defs);connectors.setAttribute('clip-path','url(#connector-mask)');const clip=$('#connector-window');
function showItem(el,p,cx,cy,fade=1){el.style.opacity=String(p*fade);el.setAttribute('transform',`translate(${cx} ${cy+(1-p)*9}) scale(${.965+.035*p}) translate(${-cx} ${-cy})`)}
let chatAnimation;
function drawChat(t,dt,staticMode){const phase=staticMode?4.5:Math.min(t*3.5,4.5);const fade=1;showItem(bubbles[0],ease((phase-.3)/.55),200,60,fade);showItem(bubbles[1],ease((phase-1.7)/.55),400,150,fade);const p=ease((phase-2.65)/1);clip.setAttribute('height',String(p*72));connectors.style.opacity=String(fade);products.forEach((g,i)=>showItem(g,ease((phase-3.35-i*.22)/.55),102+i*208,330,fade));chat.querySelectorAll('.typing circle').forEach((c,i)=>c.style.opacity=String(staticMode?.6:.4+.6*(1+Math.sin(t*4-i))/2));if(!staticMode&&phase>=4.5&&chatAnimation)chatAnimation.visible=false;}
drawChat(4.5,0,true);chatAnimation=addAnimation(chat,drawChat,4.5);

}
// Allocation bars expand once on entry. Periodic ordered stipple lives only at the tips.
const barCanvas=$('#allocation');
if(barCanvas){const bx=canvasContext(barCanvas,720,390);const allocations=[[.91,.78],[.55,.41],[.73,.6],[.37,.24]];const barLabels=['Brand','Retail media','Trade','Creator'];
function drawBars(t,dt,staticMode){bx.clearRect(0,0,720,390);bx.font='17px "Helvetica Neue",Arial';bx.textAlign='right';bx.textBaseline='middle';const left=128,max=553;bx.strokeStyle='#6388e2';bx.lineWidth=1;bx.beginPath();bx.moveTo(left,14);bx.lineTo(left,348);bx.stroke();for(let row=0;row<4;row++){let y=39+row*82;bx.fillStyle='#4b73c0';bx.fillText(barLabels[row],left-21,y+15);for(let k=0;k<2;k++){let p=staticMode?1:ease((t-row*.14-k*.08)/1.7);const len=max*allocations[row][k]*p;const yy=y+k*27;const col=k?'#88b2f2':'#1c59ef';const solid=Math.max(0,len-57);bx.fillStyle=col;bx.fillRect(left,yy,solid,20);for(let x=0;x<63;x+=4){let density=clamp(1-x/63);for(let dotY=0;dotY<20;dotY+=4){const wave=.5+.5*Math.sin(x*.24+dotY*.61+t*tau/5);const alpha=clamp(density*.9+wave*.23-.08);const radius=(.38+1.4*density)*Math.min(1,p*3);bx.globalAlpha=alpha;bx.beginPath();bx.arc(left+solid+x,yy+dotY+2,radius,0,tau);bx.fill();}}bx.globalAlpha=1;}}bx.textAlign='left';}
drawBars(4,0,true);addAnimation(barCanvas,drawBars,4);

}
// Chart line draw on entry, with a complete static alternative.
const responseChart=$('.response-chart');
if(responseChart){
 const responseCurves=[...responseChart.querySelectorAll('.curve')];
 const responseLengths=responseCurves.map(path=>path.getTotalLength());
 responseCurves.forEach((path,i)=>{path.style.strokeDasharray=String(responseLengths[i]);path.style.strokeDashoffset=String(responseLengths[i]);});
 addAnimation(responseChart,(t,dt,staticMode)=>{responseCurves.forEach((path,i)=>{const progress=staticMode?1:ease((t-i*.16)/1.5);path.style.strokeDashoffset=String(responseLengths[i]*(1-progress));});},3);
}

// Positions are registered to the original scan's cropped engraving, not a modern projection.
// The tighter crop removes the border, shifting the source origin by 129px, 145px.
const cityPixels={'-79.3832':[378,240],'-63.5752':[441,233],'14.4378':[631,230],'34.7818':[708,288],'77.5946':[820,351]};
const project=([lon])=>cityPixels[String(lon)];
const mapStage=$('.world-map'),mapPadX=Number(mapStage.dataset.mapPadX)||0,mapPadY=Number(mapStage.dataset.mapPadY)||0,mapWidth=972+2*mapPadX,mapHeight=654+2*mapPadY;
const locations=[
{name:'Toronto',slug:'toronto',coords:[-79.3832,43.6532],text:'Advisory & coordination'},
{name:'Halifax',slug:'halifax',coords:[-63.5752,44.6488],text:'Video intelligence and discovery capabilities'},
{name:'Prague',slug:'prague',coords:[14.4378,50.0755],text:'Web intelligence and automation capabilities'},
{name:'Tel Aviv',slug:'israel',coords:[34.7818,32.0853],text:'Agentic shopping and direct-to-consumer capabilities'},
{name:'Bengaluru',slug:'bengaluru',coords:[77.5946,12.9716],text:'Commerce measurement and modeling capabilities'}];
const home=project(locations[0].coords);
locations.forEach((location,i)=>{
 const[x,y]=project(location.coords);const pin=document.createElement('span');
 pin.className=`map-pin ${location.slug}`;pin.style.left=`${(x+mapPadX)/mapWidth*100}%`;pin.style.top=`${(y+mapPadY)/mapHeight*100}%`;
 pin.setAttribute('aria-hidden','true');$('.map-pins').append(pin);
 if(i){const route=document.createElementNS(ns,'path');route.dataset.city=location.slug;const lift={halifax:4,prague:18,israel:24,bengaluru:30}[location.slug],dx=x-home[0],dy=y-home[1];route.setAttribute('d',`M${home[0]},${home[1]} C${home[0]+dx*.32},${home[1]+dy*.32-lift} ${home[0]+dx*.72},${home[1]+dy*.72-lift*.55} ${x},${y}`);$('#map-routes').append(route)}
});

// One discreet traveller per route; no launch swarm or competing two-way packets.
function mapPacket(){const group=document.createElementNS(ns,'g'),halo=document.createElementNS(ns,'circle'),dot=document.createElementNS(ns,'circle');halo.classList.add('map-traveller-halo');halo.setAttribute('r','4.5');halo.setAttribute('fill','#fff');halo.setAttribute('opacity','.45');dot.classList.add('map-traveller-dot');dot.setAttribute('r','2.5');dot.setAttribute('fill','#174b96');dot.setAttribute('stroke','#fff');dot.setAttribute('stroke-width','1');dot.setAttribute('vector-effect','non-scaling-stroke');group.style.opacity='0';group.append(halo,dot);$('#map-travellers').append(group);return group}
const travellers=$$('#map-routes path').map((path,i)=>{const length=path.getTotalLength();path.style.strokeDasharray=String(length);path.style.strokeDashoffset=String(length);return{path,length,delay:i*.16,packet:{group:mapPacket(),outbound:i%2===0,duration:9+i*.8,start:2+i*1.1}}});
// Preserve the moving dots' visual size when the map scales down on a phone.
function sizeMapPackets(){const scale=Math.max(.1,$('#world-map').getBoundingClientRect().width/mapWidth);const mobile=window.innerWidth<=700;$$('.map-traveller-dot').forEach(dot=>dot.setAttribute('r',String((mobile?2:2.5)/scale)));$$('.map-traveller-halo').forEach(halo=>halo.setAttribute('r',String((mobile?4:4.5)/scale)))}
sizeMapPackets();
if('ResizeObserver' in window)new ResizeObserver(sizeMapPackets).observe($('#world-map'));
else window.addEventListener('resize',sizeMapPackets,{passive:true});
function packetState(t,packet){const age=t-packet.start;const cycle=((age/packet.duration)%1+1)%1;return {phase:packet.outbound?cycle:1-cycle,opacity:age<0?0:.72*Math.min(ease((cycle-.18)/.10),ease((.82-cycle)/.10))}}
function placePacket(route,group,phase,opacity){const point=route.path.getPointAtLength(phase*route.length);group.setAttribute('transform',`translate(${point.x} ${point.y})`);group.style.opacity=String(opacity)}
addAnimation($('.world-map'),(t,dt,staticMode)=>{travellers.forEach(a=>{const elapsed=Math.max(0,t-a.delay),progress=ease(elapsed/1.65);a.path.style.strokeDashoffset=String(a.length*(1-(staticMode?1:progress)));const state=staticMode?{phase:.5,opacity:0}:packetState(t,a.packet);placePacket(a,a.packet.group,state.phase,state.opacity)})},4);

// Artwork and the paper field are managed by halftone-rendering.js.
setMotion(reduced.matches);
window.addEventListener('resize',wake);
})();
