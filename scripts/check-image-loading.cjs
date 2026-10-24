#!/usr/bin/env node
/* Execute the actual loader against controlled load/intersection/scroll events. */
const fs=require('node:fs');
const path=require('node:path');
const vm=require('node:vm');
const assert=require('node:assert/strict');

const root=path.resolve(__dirname,'..');
const sourcePath=process.argv.find(value=>value.endsWith('.js'))||path.join(root,'current-site/image-loading.js');
const source=fs.readFileSync(sourcePath,'utf8');

function fixture(code,{complete=false,withHero=true,withObserver=true,count=3}={}){
  const listeners=new Map(),timers=new Map(),microtasks=[],observers=[],writes=[];
  let nextTimer=0;
  function target(){
    const handlers=new Map();
    return {
      handlers,
      addEventListener(name,fn,options){if(!handlers.has(name))handlers.set(name,new Map());handlers.get(name).set(fn,options);},
      removeEventListener(name,fn){handlers.get(name)?.delete(fn);},
      fire(name){for(const [fn,options]of [...(handlers.get(name)||[])]){if(options?.once)handlers.get(name).delete(fn);fn({type:name,target:this});}},
      listenerCount(){return [...handlers.values()].reduce((sum,map)=>sum+map.size,0);}
    };
  }
  const hero=Object.assign(target(),{complete}),windowTarget=target();
  const images=Array.from({length:count},(_,i)=>{
    let src;
    return {dataset:{deferredSrc:`images/original-${i}.webp`},get src(){return src;},set src(value){src=value;writes.push([i,value]);}};
  });
  class IO{
    constructor(callback,options){this.callback=callback;this.options=options;this.observed=new Set();this.disconnected=false;observers.push(this);}
    observe(image){this.observed.add(image);}
    unobserve(image){this.observed.delete(image);}
    disconnect(){this.disconnected=true;this.observed.clear();}
    fire(entries){this.callback(entries);}
  }
  const context={
    document:{querySelectorAll(selector){assert.equal(selector,'img[data-deferred-src]');return images;},querySelector(selector){assert.equal(selector,'[data-site-art="hero"] img');return withHero?hero:null;}},
    window:windowTarget,
    queueMicrotask(callback){microtasks.push(callback);},
    setTimeout(callback,delay){const id=nextTimer++;timers.set(id,{callback,delay});return id;},
    clearTimeout(id){timers.delete(id);},
    Set
  };
  if(withObserver)context.IntersectionObserver=IO;
  vm.createContext(context);vm.runInContext(code,context);
  return {images,hero,window:windowTarget,timers,microtasks,observers,writes,
    flush(){while(microtasks.length)microtasks.shift()();},
    timeout(){const timer=[...timers.values()][0];assert.ok(timer);assert.equal(timer.delay,4000);timer.callback();}};
}

function check(code){
  const f=fixture(code);
  assert.equal(f.writes.length,0,'pending hero must retain exclusive initial image fetches');
  assert.equal(f.observers.length,0,'no image observer before hero readiness');
  assert.equal(f.timers.size,1);assert.equal(f.hero.listenerCount(),2);assert.equal(f.window.listenerCount(),1);
  f.hero.fire('load');
  assert.equal(f.observers.length,1);assert.equal(f.writes.length,0,'hero completion alone must not fetch offscreen images');
  assert.equal(f.timers.size,0);assert.equal(f.hero.listenerCount(),0);assert.equal(f.window.listenerCount(),0);
  const observer=f.observers[0];assert.equal(observer.options.rootMargin,'300px');assert.equal(observer.observed.size,3);
  observer.fire([{target:f.images[0],isIntersecting:false}]);assert.equal(f.writes.length,0);
  observer.fire([{target:f.images[0],isIntersecting:true}]);assert.equal(f.writes.length,1);assert.equal(f.images[0].dataset.deferredSrc,undefined);assert.equal(f.images[0].src,'images/original-0.webp');
  observer.fire([{target:f.images[0],isIntersecting:true}]);assert.equal(f.writes.length,1,'intersection must assign each src once');
  observer.fire(f.images.slice(1).map(target=>({target,isIntersecting:true})));assert.equal(f.writes.length,3);assert.ok(observer.disconnected,'release observer when every image is loaded');
  f.hero.fire('error');f.window.fire('scroll');assert.equal(f.observers.length,1,'activation must run once');

  for(const event of ['error','scroll','timeout']){
    const r=fixture(code);
    if(event==='error')r.hero.fire('error');else if(event==='scroll')r.window.fire('scroll');else r.timeout();
    assert.equal(r.observers.length,1,event+' activates proximity loading');assert.equal(r.writes.length,0);
    assert.equal(r.hero.listenerCount(),0);assert.equal(r.window.listenerCount(),0);assert.equal(r.timers.size,0);
    r.hero.fire('load');assert.equal(r.observers.length,1,event+' cannot activate twice');
  }
  const cached=fixture(code,{complete:true});assert.equal(cached.observers.length,0);cached.flush();assert.equal(cached.observers.length,1,'cached hero activates on microtask');assert.equal(cached.timers.size,0);
  const noHero=fixture(code,{withHero:false});noHero.flush();assert.equal(noHero.observers.length,1,'missing hero cannot strand deferred images');
  const fallback=fixture(code,{withObserver:false});assert.equal(fallback.writes.length,0);fallback.hero.fire('load');assert.equal(fallback.writes.length,3,'no-IO fallback loads every deferred image');assert.ok(fallback.images.every(image=>image.dataset.deferredSrc===undefined));
  const empty=fixture(code,{count:0});assert.equal(empty.timers.size,0);assert.equal(empty.window.listenerCount(),0);assert.equal(empty.hero.listenerCount(),0);
}

check(source);
if(process.argv.includes('--self-test')){
  for(const [name,broken]of [
    ['missing loader',''],
    ['eager loader',"document.querySelectorAll('img[data-deferred-src]').forEach(image=>{image.src=image.dataset.deferredSrc;delete image.dataset.deferredSrc;});"]
  ]){
    let rejected=false;try{check(broken);}catch{rejected=true;}
    assert.ok(rejected,`regression must reject ${name}`);
  }
}
console.log('PASS: hero-first fetch gate;300px intersections; cached/error/scroll/4s/no-IO fallbacks; one-time src transfer and listener cleanup'+(process.argv.includes('--self-test')?'; missing/eager mutations rejected':''));
