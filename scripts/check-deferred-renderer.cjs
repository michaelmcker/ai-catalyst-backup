/* Local-only scheduling regression: evaluates the real production renderer. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2],'utf8');
function run({observer=true,loaded=true,map=true,hero=false}={}){
 const counts={contexts:0,loadListeners:0},observers=[];
 const image={complete:loaded,naturalWidth:loaded?100:0,naturalHeight:loaded?100:0,listeners:[],addEventListener(name,fn,options){assert.equal(name,'load');counts.loadListeners++;this.listeners.push({fn,once:options?.once});},load(){this.complete=true;this.naturalWidth=this.naturalHeight=100;const listeners=this.listeners;this.listeners=listeners.filter(x=>!x.once);listeners.forEach(x=>x.fn());}};
 const bodyStage={dataset:{siteArt:'body'},querySelector(q){return q==='img'?image:null;},append(el){el.parentElement=this;},classList:{add(){},remove(){}}};
 const mapStage={dataset:{},prepend(el){el.parentElement=this;},classList:{add(){},remove(){}}};
 const heroArea={dataset:{artSurface:'white-flow'},style:{setProperty(){}},prepend(el){el.parentElement=this;}};
 const heroBox={closest(){return heroArea;},prepend(el){el.parentElement=this;}};
 const heroStage={dataset:{siteArt:'hero'},querySelector(q){return q==='img'?image:null;},closest(){return heroBox;}};
 function canvas(){return {parentElement:null,className:'',setAttribute(){},remove(){this.parentElement=null;},getContext(type){assert.equal(type,'webgl');counts.contexts++;return null;}};}
 class IO{constructor(callback,options){this.callback=callback;this.options=options;this.targets=new Set();observers.push(this);}observe(x){this.targets.add(x);}unobserve(x){this.targets.delete(x);}fire(target,isIntersecting){this.callback([{target,isIntersecting}]);}}
 const document={hidden:false,body:{classList:{contains(){return false;}}},querySelector(){return {};},querySelectorAll(q){if(q==='[data-site-art]')return hero?[heroStage,bodyStage]:[bodyStage];if(q==='.world-map.dotted-map')return map?[mapStage]:[];throw Error('Unexpected query '+q);},createElement(tag){assert.equal(tag,'canvas');return canvas();},addEventListener(){}};
 const context={document,console,Map,Set,WeakMap,Uint8Array,getComputedStyle(){return {paddingTop:'73px'};},matchMedia(){return {matches:false,addEventListener(){}};},requestAnimationFrame(){return 1;},MutationObserver:class{observe(){}},ResizeObserver:class{observe(){}},addEventListener(){}};
 if(observer)context.IntersectionObserver=IO;
 context.window=context;vm.createContext(context);vm.runInContext(source,context);
 return {counts,observers,image,bodyStage,mapStage,heroStage};
}
function checkDeferred(){
 const r=run();
 assert.equal(r.counts.contexts,0,'offscreen decoded image/map must not create WebGL contexts');
 assert.equal(r.bodyStage.dataset.artDeferred,'waiting');assert.equal(r.mapStage.dataset.artDeferred,'waiting');
 const gate=r.observers.find(x=>x.options.rootMargin==='300px');assert.ok(gate,'separate300px gate');
 gate.fire(r.bodyStage,false);assert.equal(r.counts.contexts,0,'non-intersection must not initialize');
 gate.fire(r.bodyStage,true);assert.equal(r.counts.contexts,1);assert.equal(r.bodyStage.dataset.artDeferred,undefined);
 gate.fire(r.bodyStage,true);assert.equal(r.counts.contexts,1,'body initializes once');
 gate.fire(r.mapStage,true);assert.equal(r.counts.contexts,2);assert.equal(r.mapStage.dataset.artDeferred,undefined);
 gate.fire(r.mapStage,true);assert.equal(r.counts.contexts,2,'map initializes once');
 const pending=run({loaded:false,map:false}),pendingGate=pending.observers.find(x=>x.options.rootMargin==='300px');
 pendingGate.fire(pending.bodyStage,true);assert.equal(pending.counts.contexts,0,'wait for decoded image after proximity');
 assert.equal(pending.bodyStage.dataset.artDeferred,'waiting');assert.equal(pending.counts.loadListeners,1);
 pending.image.load();assert.equal(pending.counts.contexts,1);assert.equal(pending.bodyStage.dataset.artDeferred,undefined);
 pending.image.load();assert.equal(pending.counts.contexts,1,'load notifications cannot duplicate contexts');
 const fallback=run({observer:false});assert.equal(fallback.counts.contexts,2,'no-IO fallback starts image and map');
 const immediate=run({hero:true});assert.equal(immediate.counts.contexts,1,'hero context initializes immediately while body/map wait');assert.equal(immediate.heroStage.dataset.artDeferred,undefined);
 console.log('PASS: real renderer defers cached offscreen image/map, gates decoded loads, initializes once, preserves immediate heroes and falls back without IO');
}
if(process.argv.includes('--expect-red')){
 let failed=false;try{checkDeferred();}catch(error){failed=true;console.log('EXPECTED RED:',error.message);}
 assert.ok(failed,'baseline must fail the regression');
}else checkDeferred();
