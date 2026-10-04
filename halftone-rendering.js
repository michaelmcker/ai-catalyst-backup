/* Three layers: halftone file, static printing, and optional moving hero field. */
(() => {
  'use strict';
  const reduced=matchMedia('(prefers-reduced-motion: reduce)'),states=new Set(),fields=new Map();
  // Each source retains its own halftone base. These profiles add screen-scale print.
  const profiles={
    scene:{print:.68,softness:1.8,edges:'0 0 0 0'},
    architecture:{print:.58,softness:1.3,edges:'.035 .035 .08 .12'},
    painting:{print:.62,softness:1.6,edges:'.035 .035 .08 .12'},
    close:{print:.58,softness:.7,edges:'.12 .08 .12 .18'},
    footer:{print:.20,softness:.6,edges:'.015 .015 .05 .08'},
    map:{print:.10,softness:0,edges:'0 0 0 0'}
  };
  function setting(value,fallback){return value!==undefined&&value!==''&&Number.isFinite(Number(value))?Number(value):fallback;}
  let frame=0,last=0;
  const vertex='attribute vec2 p;varying vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}';
  const printing=`
    float b2(vec2 p){vec2 a=mod(floor(p),2.);return 2.*a.x+3.*a.y-4.*a.x*a.y;}
    float order4(vec2 p){return (4.*b2(p)+b2(p/2.)+.5)/16.;}
    float order8(vec2 p){return (16.*b2(p)+4.*b2(p/2.)+b2(p/4.)+.5)/64.;}
    float weather(vec2 pixels,float t){
      vec2 world=pixels/1100.;t*=.19;
      float bend=.22*sin(world.x*4.8+t*.7)+.10*sin(world.x*9.-t*.5);
      float field=.50+.26*sin((world.y+bend)*9.2+t)+.17*sin(world.x*5.4-world.y*3.2-t*.65);
      float level=clamp(field,0.,.999)*3.;
      float band=(floor(level)+smoothstep(.38,.62,fract(level)))/3.;
      return .025+band*.17;
    }
    vec3 paperTone(vec2 pixels,float t,float height){
      float fade=smoothstep(0.,.14,1.-pixels.y/height);
      // A fixed print screen with smoothly changing ink opacity avoids twinkling dots.
      float dots=step(order8(pixels),.19);
      float density=.48+weather(pixels,t)*1.8;
      return mix(vec3(1.),vec3(.58,.74,.94),dots*density*fade);
    }`;
  const imageFragment=`precision highp float;varying vec2 uv;
    uniform sampler2D source,trail;
    uniform vec2 crop,offset,cssSize,fieldOrigin,fieldSize,texel;
    uniform float clock,motion,hero,printStrength,atlas,softness,continuous,printPattern,printDepth;
    uniform vec4 edgeFade;
    ${printing}
    vec3 imageSample(vec2 p){
      vec3 c=texture2D(source,p).rgb;if(softness<.01)return c;
      vec2 s=texel*softness;
      return c*.25+(texture2D(source,p+vec2(s.x,0.)).rgb+texture2D(source,p-vec2(s.x,0.)).rgb+texture2D(source,p+vec2(0.,s.y)).rgb+texture2D(source,p-vec2(0.,s.y)).rgb)*.125+(texture2D(source,p+s).rgb+texture2D(source,p-s).rgb+texture2D(source,p+vec2(s.x,-s.y)).rgb+texture2D(source,p+vec2(-s.x,s.y)).rgb)*.0625;
    }
    void main(){
      vec2 v=vec2(uv.x,1.-uv.y),pixels=v*cssSize,worldPixels=pixels+fieldOrigin;
      vec3 paper=vec3(.9294118,.9686275,1.);
      vec2 imageUV=v*crop+offset;
      if(imageUV.x<0.||imageUV.x>1.||imageUV.y<0.||imageUV.y>1.){gl_FragColor=vec4(0.);return;}
      vec3 base=imageSample(imageUV);
      float sourceAlpha=texture2D(source,imageUV).a;
      if(atlas>.5){float tone=dot(base,vec3(.299,.587,.114));base=mix(vec3(.08,.22,.43),paper,smoothstep(.16,.84,tone));}
      float wake=texture2D(trail,worldPixels/fieldSize).r*motion;
      float cell=1.;
      vec2 stepped=(floor(pixels/cell)+.5)*cell;
      vec3 sampled=imageSample((stepped/cssSize)*crop+offset);
      if(atlas>.5){float tone=dot(sampled,vec3(.299,.587,.114));sampled=mix(vec3(.08,.22,.43),paper,smoothstep(.16,.84,tone));}
      float lum=dot(sampled,vec3(.299,.587,.114)),light=clamp((lum-.10)/.85,0.,1.);
      // Static printing remains when all movement is disabled.
      float threshold=order4(pixels);
      // Keep the print thresholds and artwork geometry static. Local luminance
      // and edge contrast protect dark figures and detailed architecture.
      vec2 detailStep=max(texel*3.,crop/cssSize*2.);
      float leftTone=dot(texture2D(source,imageUV-vec2(detailStep.x,0.)).rgb,vec3(.299,.587,.114));
      float rightTone=dot(texture2D(source,imageUV+vec2(detailStep.x,0.)).rgb,vec3(.299,.587,.114));
      float upTone=dot(texture2D(source,imageUV-vec2(0.,detailStep.y)).rgb,vec3(.299,.587,.114));
      float downTone=dot(texture2D(source,imageUV+vec2(0.,detailStep.y)).rgb,vec3(.299,.587,.114));
      float detail=max(max(abs(lum-leftTone),abs(lum-rightTone)),max(abs(lum-upTone),abs(lum-downTone)));
      float quietArea=(1.-smoothstep(.018,.10,detail))*smoothstep(.50,.79,lum);
      float movingBand=motion*smoothstep(.22,.88,.5+.5*sin(v.x*5.6+v.y*2.2-clock*.18));
      float local=wake*quietArea;
      vec3 ink=mix(vec3(.035,.16,.49),paper,step(threshold,light));
      // Scenic print nudges the original shading instead of replacing it with two inks.
      vec3 tonalInk=clamp(base+vec3((step(threshold,light)-light)*printDepth),vec3(0.),paper);
      ink=mix(ink,tonalInk,continuous);
      float imageMask=1.-smoothstep(.90,.975,dot(base,vec3(.299,.587,.114)));
      float printZone=printPattern<.5?0.:(printPattern<1.5?smoothstep(.62,.68,v.x):smoothstep(.54,.59,v.y));
      float printAmount=clamp(mix(printStrength,.92,printZone*.72),0.,1.);
      vec3 col=mix(base,ink,printAmount*imageMask);
      float bluePass=(movingBand*.045+local*.035)*quietArea;
      col=mix(col,vec3(.20,.40,.74),bluePass);
      float whiteArea=smoothstep(.85,.985,lum);
      vec3 backdrop=hero>.5?paperTone(worldPixels,clock,fieldSize.y):paper;
      col=mix(col,backdrop,whiteArea);
      // Feather at the sampled image edges, including letterboxing. Alpha lets
      // the actual shared paper field show through instead of painting a box.
      float edges=mix(1.,smoothstep(0.,max(edgeFade.x,.001),imageUV.x),step(.001,edgeFade.x))*mix(1.,smoothstep(0.,max(edgeFade.y,.001),1.-imageUV.x),step(.001,edgeFade.y))*mix(1.,smoothstep(0.,max(edgeFade.z,.001),imageUV.y),step(.001,edgeFade.z))*mix(1.,smoothstep(0.,max(edgeFade.w,.001),1.-imageUV.y),step(.001,edgeFade.w));
      float feather=mix(edges,step(order8(worldPixels),edges),.52);
      gl_FragColor=vec4(col,feather*sourceAlpha);
    }`;
  const fieldFragment=`precision highp float;varying vec2 uv;uniform vec2 cssSize;uniform float clock;${printing}
    void main(){gl_FragColor=vec4(paperTone(vec2(uv.x,1.-uv.y)*cssSize,clock,cssSize.y),1.);}`;

  function wake(){if(!frame&&!document.hidden)frame=requestAnimationFrame(tick);}
  function tick(now){
    frame=0;if(document.hidden)return;
    if(now-last<1000/24){wake();return;}
    const dt=Math.min(.12,last?(now-last)/1000:1/24);last=now;
    for(const field of fields.values())if(field.visible)field.update(dt);
    let continuing=false;
    for(const state of states){
      if(!state.visible||!state.ready)continue;
      if(state.dirty||(!reduced.matches&&state.hero)){state.draw(reduced.matches?0:now/1000);state.dirty=false;}
      if(state.hero&&!reduced.matches)continuing=true;
    }
    if(continuing)wake();
  }
  function renderer(canvas,fragment){
    const gl=canvas.getContext('webgl',{alpha:fragment===imageFragment,premultipliedAlpha:false,antialias:false,powerPreference:'low-power'});if(!gl)return null;
    const compile=(type,text)=>{const s=gl.createShader(type);gl.shaderSource(s,text);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    const program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vertex));gl.attachShader(program,compile(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('Artwork shader link failed');
    gl.useProgram(program);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
    const a=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
    const u={};['source','trail','crop','offset','cssSize','fieldOrigin','fieldSize','clock','motion','hero','printStrength','edgeFade','atlas','texel','softness','continuous','printPattern','printDepth'].forEach(n=>u[n]=gl.getUniformLocation(program,n));
    const state={canvas,gl,program,u,ready:true,visible:false,dirty:true,hero:false,width:1,height:1,rect:null};
    state.fit=rect=>{state.rect=rect;state.width=rect.width;state.height=rect.height;const ratio=Math.min(devicePixelRatio||1,2,4096/Math.max(1,rect.width,rect.height));canvas.width=Math.max(1,Math.round(rect.width*ratio));canvas.height=Math.max(1,Math.round(rect.height*ratio));gl.viewport(0,0,canvas.width,canvas.height);state.dirty=true;};
    states.add(state);return state;
  }
  function texture(state,unit){
    const {gl}=state;gl.activeTexture(unit);const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);return t;
  }
  function visibility(element,state,field){new IntersectionObserver(entries=>{state.visible=entries[0].isIntersecting;if(field)field.visible=state.visible;if(state.visible){state.dirty=true;wake();}},{rootMargin:'80px',threshold:0}).observe(element);}
  function heroField(hero){
    const area=hero.closest('.art-opening,.hero-scene')||hero;if(fields.has(area))return fields.get(area);
    area.style.setProperty('--art-header-space',getComputedStyle(document.querySelector('#main')).paddingTop);
    const canvas=document.createElement('canvas');canvas.className='site-hero-field';canvas.setAttribute('aria-hidden','true');area.prepend(canvas);
    const state=renderer(canvas,fieldFragment);if(!state){canvas.remove();return null;}
    const trail=document.createElement('canvas'),ctx=trail.getContext('2d',{alpha:false});
    const field={area,state,trail,ctx,visible:false,rect:null,pending:[],previous:null};state.hero=true;area.dataset.artMotion='field-and-trail';
    state.draw=time=>{const {gl,u}=state;gl.useProgram(state.program);gl.uniform2f(u.cssSize,state.width,state.height);gl.uniform1f(u.clock,time);gl.drawArrays(gl.TRIANGLES,0,6);};
    function measure(){const r=canvas.getBoundingClientRect();if(!r.width||!r.height)return;field.rect=r;state.fit(r);trail.width=Math.max(64,Math.ceil(r.width/5));trail.height=Math.max(64,Math.ceil(r.height/5));ctx.fillStyle='#000';ctx.fillRect(0,0,trail.width,trail.height);state.draw(reduced.matches?0:performance.now()/1000);wake();}
    const sizeObserver=new ResizeObserver(measure);sizeObserver.observe(area);sizeObserver.observe(canvas);measure();
    function stamp(x,y,radius){const sx=trail.width/field.rect.width,sy=trail.height/field.rect.height,gx=x*trail.width,gy=y*trail.height,rad=radius*Math.min(sx,sy);const g=ctx.createRadialGradient(gx,gy,0,gx,gy,rad);g.addColorStop(0,'rgba(255,255,255,.70)');g.addColorStop(.35,'rgba(255,255,255,.50)');g.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=g;ctx.fillRect(gx-rad,gy-rad,rad*2,rad*2);}
    field.update=dt=>{
      ctx.globalCompositeOperation='source-over';ctx.fillStyle=`rgba(0,0,0,${reduced.matches?1:1-Math.exp(-5.8*dt)})`;ctx.fillRect(0,0,trail.width,trail.height);
      if(!reduced.matches){ctx.globalCompositeOperation='lighten';for(const p of field.pending){const distance=Math.hypot((p.to.x-p.from.x)*field.rect.width,(p.to.y-p.from.y)*field.rect.height),steps=Math.max(1,Math.ceil(distance/5));for(let i=0;i<=steps;i++){const a=i/steps;stamp(p.from.x+(p.to.x-p.from.x)*a,p.from.y+(p.to.y-p.from.y)*a,32+p.speed*14);}}}field.pending=[];
    };
    area.addEventListener('pointermove',event=>{if(event.pointerType==='touch'||reduced.matches)return;const r=canvas.getBoundingClientRect(),next={x:(event.clientX-r.left)/r.width,y:(event.clientY-r.top)/r.height};if(field.previous){const distance=Math.hypot((next.x-field.previous.x)*r.width,(next.y-field.previous.y)*r.height);if(distance>.3){field.pending.push({from:field.previous,to:next,speed:Math.min(distance/60,1)});if(field.pending.length>24)field.pending.shift();}}field.previous=next;wake();},{passive:true});
    area.addEventListener('pointerleave',()=>{field.previous=null;});
    visibility(area,state,field);fields.set(area,field);return field;
  }
  function position(value,fallback){if(value==='left'||value==='top')return 0;if(value==='right'||value==='bottom')return 1;const number=parseFloat(value);return Number.isFinite(number)&&value.includes('%')?number/100:fallback;}
  function setup(stage){
    const img=stage.querySelector('img');if(!img)return;
    const isHero=stage.dataset.siteArt==='hero',field=isHero?heroField(stage.closest('.hero,.page-hero')):null;
    function initialise(){
      const canvas=stage.querySelector('canvas')||document.createElement('canvas');canvas.className='site-art-tones';canvas.setAttribute('aria-hidden','true');if(!canvas.parentElement)stage.append(canvas);
      try{
        const state=renderer(canvas,imageFragment);if(!state){canvas.remove();return;}
        const {gl,u}=state;state.hero=isHero;stage.dataset.artLayers=isHero?'base-static-moving':'base-static';stage.dataset.artMotion=isHero?'luminance-edge-aware-tone':'static';
        const source=texture(state,gl.TEXTURE0);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img);
        const trail=texture(state,gl.TEXTURE1),empty=document.createElement('canvas');empty.width=empty.height=1;gl.uniform1i(u.source,0);gl.uniform1i(u.trail,1);
        function measure(){const r=stage.getBoundingClientRect();if(!r.width||!r.height)return;const styles=getComputedStyle(img),values=styles.objectPosition.split(' '),scale=(styles.objectFit==='contain'?Math.min:Math.max)(r.width/img.naturalWidth,r.height/img.naturalHeight),cx=r.width/(img.naturalWidth*scale),cy=r.height/(img.naturalHeight*scale);state.crop=[cx,cy];state.offset=[(1-cx)*position(values[0],.5),(1-cy)*position(values[1],.5)];if(stage.dataset.artCrop){const [x,y,w,h]=stage.dataset.artCrop.split(' ').map(Number);state.crop=[w,h];state.offset=[x,y];}state.fit(r);stage.dataset.ditherCell='1-css-px';wake();}
        state.draw=time=>{
          gl.useProgram(state.program);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,source);gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,trail);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,field?field.trail:empty);
          gl.uniform2f(u.crop,...state.crop);gl.uniform2f(u.offset,...state.offset);gl.uniform2f(u.cssSize,state.width,state.height);
          const profile=profiles[stage.dataset.artProfile];
          gl.uniform1f(u.printDepth,['map','footer'].includes(stage.dataset.artProfile)?.13:.34);
          gl.uniform1f(u.printPattern,stage.dataset.artPrintPattern==='drift'?2:0);
          gl.uniform1f(u.continuous,['scene','architecture','painting','footer','map'].includes(stage.dataset.artProfile)?1:0);
          gl.uniform2f(u.texel,1/img.naturalWidth,1/img.naturalHeight);gl.uniform1f(u.softness,setting(stage.dataset.artSoftness,profile?profile.softness:0));
          gl.uniform2f(u.fieldOrigin,field?state.rect.left-field.rect.left:0,field?state.rect.top-field.rect.top:0);gl.uniform2f(u.fieldSize,field?field.rect.width:1,field?field.rect.height:1);
          const defaultEdges=isHero?'.24 .13 .17 .3':'.08 .08 .17 .22';
          const edges=(stage.dataset.artFeather||(profile?profile.edges:defaultEdges)).split(' ').map(Number);
          gl.uniform1f(u.printStrength,Math.max(0,Math.min(1,setting(stage.dataset.artPrint,profile?profile.print:(isHero?.72:.42)))));gl.uniform4f(u.edgeFade,...edges);gl.uniform1f(u.atlas,stage.dataset.artColor==='atlas'?1:0);
          gl.uniform1f(u.clock,isHero?time:0);gl.uniform1f(u.motion,isHero&&!reduced.matches?1:0);gl.uniform1f(u.hero,isHero?1:0);gl.drawArrays(gl.TRIANGLES,0,6);stage.classList.add('site-art-ready');
        };
        new ResizeObserver(measure).observe(stage);measure();state.draw(reduced.matches?0:performance.now()/1000);visibility(stage,state);
        canvas.addEventListener('webglcontextlost',()=>{state.ready=false;stage.classList.remove('site-art-ready');});
      }catch(error){canvas.remove();console.warn('Artwork uses its halftone base:',error.message);}
    }
    if(img.complete&&img.naturalWidth)initialise();else img.addEventListener('load',initialise,{once:true});
  }
  document.querySelectorAll('[data-site-art]').forEach(setup);
  window.addEventListener('resize',()=>{const spacing=getComputedStyle(document.querySelector('#main')).paddingTop;fields.forEach(f=>f.area.style.setProperty('--art-header-space',spacing));},{passive:true});
  document.addEventListener('visibilitychange',()=>{last=0;if(!document.hidden){states.forEach(s=>s.dirty=true);wake();}});
  reduced.addEventListener('change',()=>{fields.forEach(f=>{f.pending=[];f.previous=null;});states.forEach(s=>s.dirty=true);wake();});
  window.addEventListener('aic:artwork-refresh',()=>{states.forEach(s=>s.dirty=true);wake();});
})();
