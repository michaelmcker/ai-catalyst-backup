/* Base artwork, print finish, and the verified Roman/Greco V1 dither motion.
   V1 source: restored-home-motion.js SHA1 97804df71db9e4b59ed0f2a73391b616903fb382.
   The homepage uses the original threshold animation; other art profiles stay intact. */
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
  let frame=0,last=0,clock=0;
  const motionPaused=()=>reduced.matches||document.body.classList.contains('motion-paused');
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
    }
    float v1Field(vec2 pixels,float clock,vec2 size,vec3 pointer){
      vec2 world=pixels/1100.;float t=clock*.19;
      float bend=.22*sin(world.x*4.8+t*.7)+.10*sin(world.x*9.-t*.5);
      float field=.50+.26*sin((world.y+bend)*9.2+t)+.17*sin(world.x*5.4-world.y*3.2-t*.65);
      vec2 delta=(pixels/size-pointer.xy)*vec2(size.x/size.y,1.);
      return field+exp(-dot(delta,delta)/.006)*pointer.z*.11;
    }
    float v1Density(float field){
      float level=clamp(field,0.,.999)*3.;
      float band=(floor(level)+smoothstep(.38,.62,fract(level)))/3.;
      return .025+band*.275;
    }
    vec3 v1Paper(vec2 pixels,float t,vec2 size,vec3 pointer){
      // V1 prints the whole moving region as changing dot density, not outlines.
      float dotInk=step(order8(pixels),v1Density(v1Field(pixels,t,size,pointer)));
      float fade=smoothstep(0.,.14,1.-pixels.y/size.y);
      return mix(vec3(1.),vec3(.58,.74,.94),dotInk*fade);
    }`;
  const imageFragment=`precision highp float;varying vec2 uv;
    uniform sampler2D source,trail;
    uniform vec2 crop,offset,cssSize,fieldOrigin,fieldSize,texel,artOrigin;
    uniform vec3 pointer;
    uniform float clock,motion,hero,clearPaper,printStrength,atlas,softness,continuous,printPattern,printDepth,whiteSurface,composite,sourceReady;
    uniform vec4 edgeFade;
    ${printing}
    vec3 imageSample(vec2 p){
      vec3 c=texture2D(source,p).rgb;if(softness<.01)return c;
      vec2 s=texel*softness;
      return c*.25+(texture2D(source,p+vec2(s.x,0.)).rgb+texture2D(source,p-vec2(s.x,0.)).rgb+texture2D(source,p+vec2(0.,s.y)).rgb+texture2D(source,p-vec2(0.,s.y)).rgb)*.125+(texture2D(source,p+s).rgb+texture2D(source,p-s).rgb+texture2D(source,p+vec2(s.x,-s.y)).rgb+texture2D(source,p+vec2(-s.x,s.y)).rgb)*.0625;
    }
    void main(){
      vec2 v=vec2(uv.x,1.-uv.y),pixels=v*cssSize,worldPixels=pixels+fieldOrigin;
      vec3 commonPaper=vec3(1.);
      if(composite>.5){
        // One full-hero framebuffer owns the paper, image and their boundary.
        // Artwork-local coordinates preserve the authored print and crop maths.
        worldPixels=v*fieldSize;
        commonPaper=mix(paperTone(worldPixels,clock,fieldSize.y),v1Paper(worldPixels,clock,fieldSize,pointer),whiteSurface);
        if(whiteSurface<.5){
          // At rest this is exactly paperTone. Apply only the original V1
          // pointer Gaussian to its ordered dot density, so subpage paper
          // responds behind live text and keyed image paper in the same pass.
          // Dot size, weather, base density and ink strength remain unchanged.
          float disturbance=max(0.,v1Field(worldPixels,clock,fieldSize,pointer)-v1Field(worldPixels,clock,fieldSize,vec3(pointer.xy,0.)));
          float dots=step(order8(worldPixels),.19+disturbance);
          float fade=smoothstep(0.,.14,1.-worldPixels.y/fieldSize.y);
          float density=.48+weather(worldPixels,clock)*1.8;
          commonPaper=mix(vec3(1.),vec3(.58,.74,.94),dots*density*fade);
        }
        pixels=worldPixels-artOrigin;v=pixels/cssSize;
        if(sourceReady<.5||v.x<0.||v.x>1.||v.y<0.||v.y>1.){gl_FragColor=vec4(commonPaper,1.);return;}
      }
      vec3 paper=mix(vec3(.9294118,.9686275,1.),vec3(1.),whiteSurface);
      vec2 imageUV=v*crop+offset;
      if(imageUV.x<0.||imageUV.x>1.||imageUV.y<0.||imageUV.y>1.){gl_FragColor=composite>.5?vec4(commonPaper,1.):vec4(0.);return;}
      vec3 base=imageSample(imageUV);
      float sourceAlpha=texture2D(source,imageUV).a;
      if(atlas>.5){float tone=dot(base,vec3(.299,.587,.114));base=mix(vec3(.08,.22,.43),paper,smoothstep(.16,.84,tone));}
      float wake=texture2D(trail,worldPixels/fieldSize).r*motion;
      float v1=whiteSurface*hero;
      float cell=1.+step(.68,wake)*v1;
      vec2 stepped=(floor(pixels/cell)+.5)*cell;
      vec3 sampled=imageSample((stepped/cssSize)*crop+offset);
      if(atlas>.5){float tone=dot(sampled,vec3(.299,.587,.114));sampled=mix(vec3(.08,.22,.43),paper,smoothstep(.16,.84,tone));}
      float lum=dot(sampled,vec3(.299,.587,.114)),light=clamp((lum-.10)/.85,0.,1.);
      // Static printing remains when all movement is disabled.
      float local=floor(wake*5.)/5.;
      float threshold=mix(order4(pixels),order8(pixels),step(.4,local)*.35*v1);
      // Exact V1 tonal weather: source coordinates stay fixed as ink thresholds move.
      float slow=clock*.32;
      float ambient=(sin(v.x*6.+v.y*2.+slow)+.5*sin(v.y*8.-v.x*3.-slow*.7))*.095*motion*v1;
      float bias=ambient*(1.-local*.7)+local*.038*v1;
      // Other page profiles retain their quiet tonal pass. Local luminance
      // and edge contrast protect dark figures and detailed architecture.
      vec2 detailStep=max(texel*3.,crop/cssSize*2.);
      float leftTone=dot(texture2D(source,imageUV-vec2(detailStep.x,0.)).rgb,vec3(.299,.587,.114));
      float rightTone=dot(texture2D(source,imageUV+vec2(detailStep.x,0.)).rgb,vec3(.299,.587,.114));
      float upTone=dot(texture2D(source,imageUV-vec2(0.,detailStep.y)).rgb,vec3(.299,.587,.114));
      float downTone=dot(texture2D(source,imageUV+vec2(0.,detailStep.y)).rgb,vec3(.299,.587,.114));
      float detail=max(max(abs(lum-leftTone),abs(lum-rightTone)),max(abs(lum-upTone),abs(lum-downTone)));
      float quietArea=(1.-smoothstep(.018,.10,detail))*smoothstep(.50,.79,lum);
      float movingBand=motion*smoothstep(.22,.88,.5+.5*sin(v.x*5.6+v.y*2.2-clock*.18));
      vec3 ink=mix(vec3(.035,.16,.49),paper,step(threshold+bias,light));
      // Scenic print nudges the original shading instead of replacing it with two inks.
      vec3 tonalInk=clamp(base+vec3((step(threshold,light)-light)*printDepth),vec3(0.),paper);
      ink=mix(ink,tonalInk,continuous);
      float imageMask=1.-smoothstep(.90,.975,dot(base,vec3(.299,.587,.114)));
      float printZone=printPattern<.5?0.:(printPattern<1.5?smoothstep(.62,.68,v.x):smoothstep(.54,.59,v.y));
      float printAmount=clamp(mix(printStrength,.92,printZone*.72),0.,1.);
      vec3 col=mix(base,ink,clamp(printAmount*imageMask+local*.23*v1,0.,1.));
      float bluePass=(movingBand*.045+wake*quietArea*.035)*quietArea*(1.-v1);
      col=mix(col,vec3(.20,.40,.74),bluePass);
      float whiteArea=mix(smoothstep(.85,.985,lum),smoothstep(.72,.91,lum)*(1.-smoothstep(.025,.10,detail)),clearPaper);
      vec3 backdrop=hero>.5?mix(paperTone(worldPixels,clock,fieldSize.y),v1Paper(worldPixels,clock,fieldSize,pointer),whiteSurface):paper;
      if(composite<.5&&clearPaper<.5)col=mix(col,backdrop,whiteArea);
      // Feather at the sampled image edges, including letterboxing. Alpha lets
      // the actual shared paper field show through instead of painting a box.
      float edges=mix(1.,smoothstep(0.,max(edgeFade.x,.001),imageUV.x),step(.001,edgeFade.x))*mix(1.,smoothstep(0.,max(edgeFade.y,.001),1.-imageUV.x),step(.001,edgeFade.y))*mix(1.,smoothstep(0.,max(edgeFade.z,.001),imageUV.y),step(.001,edgeFade.z))*mix(1.,smoothstep(0.,max(edgeFade.w,.001),1.-imageUV.y),step(.001,edgeFade.w));
      if(composite>.5){
        // The source masters have opaque pale-blue paper, not transparency.
        // Fully release clean RGB214/235/252 and RGB234/247/254 paper (including
        // small grain), rather than retaining a weaker second paper screen.
        // Scenic profiles keep their original skies and light architecture.
        float keyedPaper=(1.-continuous)*smoothstep(.80,.885,lum)*(1.-smoothstep(.025,.10,detail));
        // Smooth CSS-pixel stage edges replace the binary rectangular Bayer
        // alpha contour. The original source-space feather remains intact.
        float stageEdge=smoothstep(0.,12.,pixels.x)*smoothstep(0.,12.,cssSize.x-pixels.x)*smoothstep(0.,12.,pixels.y)*smoothstep(0.,12.,cssSize.y-pixels.y);
        float coverage=edges*mix(stageEdge,1.,continuous)*sourceAlpha*(1.-keyedPaper);
        gl_FragColor=vec4(mix(commonPaper,col,coverage),1.);return;
      }
      float feather=mix(edges,step(order8(worldPixels),edges),.52);
      float alpha=feather*sourceAlpha*(1.-clearPaper*whiteArea);
      // Match the standard premultiplied drawing buffer without changing the
      // original body-art colour or alpha once it reaches the page compositor.
      gl_FragColor=vec4(col*alpha,alpha);
    }`;
  const fieldFragment=`precision highp float;varying vec2 uv;uniform vec2 cssSize;uniform vec3 pointer;uniform float clock,whiteSurface;${printing}
    void main(){vec2 v=vec2(uv.x,1.-uv.y);gl_FragColor=vec4(mix(paperTone(v*cssSize,clock,cssSize.y),v1Paper(v*cssSize,clock,cssSize,pointer),whiteSurface),1.);}`;
  const mapFragment=`precision highp float;varying vec2 uv;uniform sampler2D source;uniform vec2 cssSize;uniform vec3 pointer;uniform float clock;${printing}
    void main(){
      vec2 v=vec2(uv.x,1.-uv.y),pixels=v*cssSize;
      float mask=texture2D(source,v).a;
      float density=v1Density(v1Field(pixels,clock,cssSize,pointer));
      // A quieter version of the same density field, clipped to the existing land dots.
      float ink=.16+step(order8(pixels),density)*.52;
      float compact=1.-step(700.,cssSize.x);
      vec3 baseInk=mix(vec3(.5294,.6627,.8745),vec3(.24,.40,.63),compact);
      vec3 darkInk=mix(vec3(.16,.38,.72),vec3(.12,.29,.54),compact);
      vec3 color=mix(baseInk,darkInk,ink);
      gl_FragColor=vec4(color*mask,mask);
    }`;

  function wake(){if(!frame&&!document.hidden)frame=requestAnimationFrame(tick);}
  function tick(now){
    frame=0;if(document.hidden)return;
    if(now-last<1000/24){wake();return;}
    const dt=Math.min(.05,last?(now-last)/1000:1/24);last=now;
    const paused=motionPaused();if(!paused)clock+=dt;
    for(const field of fields.values())if(field.visible)field.update(dt);
    let continuing=false;
    for(const state of states){
      if(!state.visible||!state.ready)continue;
      if(state.dirty||(!paused&&state.hero)){state.draw(paused?0:clock);state.dirty=false;}
      if(state.hero&&!paused)continuing=true;
    }
    if(continuing)wake();
  }
  function renderer(canvas,fragment,opaque=false){
    const gl=canvas.getContext('webgl',{alpha:!opaque&&fragment!==fieldFragment,premultipliedAlpha:true,antialias:false,powerPreference:'low-power'});if(!gl)return null;
    const compile=(type,text)=>{const s=gl.createShader(type);gl.shaderSource(s,text);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
    const program=gl.createProgram();gl.attachShader(program,compile(gl.VERTEX_SHADER,vertex));gl.attachShader(program,compile(gl.FRAGMENT_SHADER,fragment));gl.linkProgram(program);
    if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error('Artwork shader link failed');
    gl.useProgram(program);const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
    const a=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
    const u={};['source','trail','crop','offset','cssSize','fieldOrigin','fieldSize','clock','motion','hero','clearPaper','printStrength','edgeFade','atlas','texel','softness','continuous','printPattern','printDepth','whiteSurface','pointer','composite','sourceReady','artOrigin'].forEach(n=>u[n]=gl.getUniformLocation(program,n));
    const state={canvas,gl,program,u,ready:true,visible:false,dirty:true,hero:false,opaque,width:1,height:1,rect:null};
    state.fit=rect=>{state.rect=rect;state.width=rect.width;state.height=rect.height;const ratio=Math.min(devicePixelRatio||1,opaque?3:2,4096/Math.max(1,rect.width,rect.height));canvas.width=Math.max(1,Math.round(rect.width*ratio));canvas.height=Math.max(1,Math.round(rect.height*ratio));canvas.dataset.artBackingRatio=String(ratio);gl.viewport(0,0,canvas.width,canvas.height);state.dirty=true;};
    states.add(state);return state;
  }
  function texture(state,unit){
    const {gl}=state;gl.activeTexture(unit);const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);return t;
  }
  function visibility(element,state,field){
    if(typeof IntersectionObserver!=='function'){state.visible=true;if(field)field.visible=true;state.dirty=true;wake();return;}
    new IntersectionObserver(entries=>{state.visible=entries[0].isIntersecting;if(field)field.visible=state.visible;if(state.visible){state.dirty=true;wake();}},{rootMargin:'80px',threshold:0}).observe(element);
  }
  function heroField(hero,isMap=false){
    const area=isMap?hero:hero.closest('.art-opening,.hero-scene')||hero;
    if(fields.has(area))return fields.get(area);
    if(!isMap)area.style.setProperty('--art-header-space',getComputedStyle(document.querySelector('#main')).paddingTop);
    const canvas=document.createElement('canvas');
    canvas.className=isMap?'map-dither-field':'site-hero-field site-hero-composite';canvas.setAttribute('aria-hidden','true');
    // Heroes render paper and artwork into one opaque surface below live copy.
    // There is no independently masked artwork canvas or CSS multiply pass.
    const whiteHero=!isMap&&area.dataset.artSurface==='white-flow';
    const host=whiteHero?hero:area;host.prepend(canvas);
    let state;
    try{state=renderer(canvas,isMap?mapFragment:imageFragment,!isMap)}catch(error){canvas.remove();console.warn('Dither uses its static fallback:',error.message);return null;}
    if(!state){canvas.remove();return null;}
    const trail=document.createElement('canvas'),ctx=trail.getContext('2d',{alpha:false});
    const whiteSurface=isMap||area.dataset.artSurface==='white-flow';
    const field={area,host,state,trail,ctx,whiteSurface,visible:false,rect:null,pending:[],previous:null,cursor:[0,0,0],elapsed:0,scrollStamp:null,art:null};
    state.hero=true;area.dataset.artMotion=isMap?'v1-dithered-land':'v1-density-and-wake';
    let maskTexture=null,maskGeneration=0,artTexture=null,trailTexture=null;
    if(isMap){maskTexture=texture(state,state.gl.TEXTURE0);state.ready=false;}
    else{
      const {gl,u}=state;
      artTexture=texture(state,gl.TEXTURE0);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array([0,0,0,0]));
      trailTexture=texture(state,gl.TEXTURE1);
      gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array([0,0,0,255]));
      gl.uniform1i(u.source,0);gl.uniform1i(u.trail,1);
      field.uploadSource=img=>{gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,artTexture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img);state.dirty=true;};
      area.dataset.artComposite='single-opaque-surface';
      canvas.dataset.artOpaque='true';
    }
    state.draw=time=>{
      if(!field.rect)return;
      const {gl,u}=state;gl.useProgram(state.program);
      let artworkReady=false;
      if(isMap){gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,maskTexture);gl.uniform1i(u.source,0);}
      else{
        // Position can change without a ResizeObserver notification (wrapping,
        // image alignment or scroll). Read both live rectangles on every draw.
        field.rect=canvas.getBoundingClientRect();
        const art=field.art,ready=art&&measureHeroArt(field);artworkReady=Boolean(ready);
        gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,artTexture);
        gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,trailTexture);
        gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,field.trail);
        gl.uniform1f(u.composite,1);gl.uniform1f(u.sourceReady,ready?1:0);
        gl.uniform1f(u.hero,1);gl.uniform1f(u.motion,motionPaused()?0:1);
        gl.uniform2f(u.fieldSize,state.width,state.height);
        gl.uniform2f(u.cssSize,ready?art.rect.width:1,ready?art.rect.height:1);
        gl.uniform2f(u.artOrigin,ready?art.rect.left-field.rect.left:0,ready?art.rect.top-field.rect.top:0);
        if(ready)heroArtUniforms(field);
      }
      gl.uniform1f(u.whiteSurface,whiteSurface?1:0);
      if(isMap)gl.uniform2f(u.cssSize,state.width,state.height);
      gl.uniform3f(u.pointer,...field.cursor);gl.uniform1f(u.clock,time);gl.drawArrays(gl.TRIANGLES,0,6);
      if(!isMap)canvas.dataset.artDrawReady=String(artworkReady);
      if(!isMap&&artworkReady){
        field.art.stage.querySelectorAll('canvas').forEach(oldCanvas=>oldCanvas.remove());
        field.art.stage.classList.add('site-art-ready');
        field.art.stage.dataset.artDrawReady='true';
      }
    };
    function updateMapMask(){
      // Rasterize only the existing SVG land-dot layer. Routes, labels and markers
      // remain live SVG above this canvas, with an intact static fallback beneath.
      const generation=++maskGeneration,svg=area.querySelector('#world-map').cloneNode(true);
      svg.setAttribute('xmlns','http://www.w3.org/2000/svg');svg.setAttribute('width',canvas.width);svg.setAttribute('height',canvas.height);
      svg.querySelectorAll('#map-routes,#map-travellers,#map-markers,#map-labels').forEach(el=>el.remove());
      svg.querySelector('#world-dot-pattern circle').setAttribute('fill','#fff');
      const url=URL.createObjectURL(new Blob([new XMLSerializer().serializeToString(svg)],{type:'image/svg+xml'})),mask=new Image();
      mask.onload=()=>{URL.revokeObjectURL(url);if(generation!==maskGeneration)return;
        const {gl}=state;gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,maskTexture);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,mask);
        state.ready=true;state.dirty=true;area.classList.add('map-dither-ready');wake();
      };
      mask.onerror=()=>{URL.revokeObjectURL(url);if(generation===maskGeneration){state.ready=false;area.classList.remove('map-dither-ready');}};
      mask.src=url;
    }
    function measure(){
      if(!isMap){
        // Match the full surface to the device-pixel grid, including native 3x
        // phones. All paper and image samples now share that one backing grid.
        const bounds=host.getBoundingClientRect();
        if(!bounds.width||!bounds.height)return;
        const ratio=Math.min(devicePixelRatio||1,3,4096/Math.max(bounds.width,bounds.height));
        const left=Math.floor(bounds.left*ratio)/ratio,top=Math.floor(bounds.top*ratio)/ratio;
        const right=Math.ceil(bounds.right*ratio)/ratio,bottom=Math.ceil(bounds.bottom*ratio)/ratio;
        const values={left:`${left-bounds.left}px`,top:`${top-bounds.top}px`,right:'auto',bottom:'auto',width:`${right-left}px`,height:`${bottom-top}px`};
        for(const [name,value]of Object.entries(values))if(canvas.style.getPropertyValue(name)!==value)canvas.style.setProperty(name,value,'important');
      }
      const r=canvas.getBoundingClientRect();if(!r.width||!r.height)return;
      field.rect=r;state.fit(r);trail.width=whiteSurface?256:Math.max(64,Math.ceil(r.width/5));trail.height=whiteSurface?160:Math.max(64,Math.ceil(r.height/5));
      ctx.fillStyle='#000';ctx.fillRect(0,0,trail.width,trail.height);
      if(isMap)updateMapMask();else state.draw(motionPaused()?0:clock);
      wake();
    }
    field.measure=measure;
    const sizeObserver=new ResizeObserver(measure);sizeObserver.observe(area);measure();
    function stamp(x,y,radius){
      const gx=x*trail.width,gy=y*trail.height,rad=whiteSurface?radius:radius*Math.min(trail.width/field.rect.width,trail.height/field.rect.height);
      const g=ctx.createRadialGradient(gx,gy,0,gx,gy,rad);g.addColorStop(0,'rgba(255,255,255,.70)');g.addColorStop(.35,'rgba(255,255,255,.50)');g.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=g;ctx.fillRect(gx-rad,gy-rad,rad*2,rad*2);
    }
    field.update=dt=>{
      if(!field.rect)return;
      const paused=motionPaused();field.cursor[2]=paused?0:field.cursor[2]*Math.exp(-dt*3.2);
      field.elapsed+=dt;if(!paused&&field.elapsed<1/18)return;
      const elapsed=field.elapsed;field.elapsed=0;
      ctx.globalCompositeOperation='source-over';ctx.fillStyle=`rgba(0,0,0,${paused?1:1-Math.exp(-5.8*elapsed)})`;ctx.fillRect(0,0,trail.width,trail.height);
      if(!paused){
        ctx.globalCompositeOperation='lighten';
        for(const p of field.pending){const steps=Math.max(1,Math.ceil(Math.hypot((p.to.x-p.from.x)*trail.width,(p.to.y-p.from.y)*trail.height)/5));for(let i=0;i<=steps;i++){const a=i/steps;stamp(p.from.x+(p.to.x-p.from.x)*a,p.from.y+(p.to.y-p.from.y)*a,whiteSurface?8+p.speed*3:32+p.speed*14);}}
        if(field.scrollStamp)stamp(.60,field.scrollStamp.y,9);
      }
      field.pending=[];field.scrollStamp=null;
    };
    area.addEventListener('pointermove',event=>{
      if(event.pointerType==='touch'||motionPaused())return;
      const r=canvas.getBoundingClientRect(),next={x:(event.clientX-r.left)/r.width,y:(event.clientY-r.top)/r.height};
      field.cursor=[next.x,next.y,1];
      if(field.previous){const distance=Math.hypot((next.x-field.previous.x)*r.width,(next.y-field.previous.y)*r.height);if(distance>.3){field.pending.push({from:field.previous,to:next,speed:Math.min(distance/60,1)});if(field.pending.length>24)field.pending.shift();}}
      field.previous=next;wake();
    },{passive:true});
    area.addEventListener('pointerleave',()=>{field.previous=null;});
    if(whiteSurface)window.addEventListener('scroll',()=>{
      if(!field.visible||motionPaused()||!matchMedia('(pointer: coarse)').matches)return;
      const r=canvas.getBoundingClientRect();field.scrollStamp={y:Math.max(0,Math.min(1,(innerHeight*.6-r.top)/r.height))};wake();
    },{passive:true});
    canvas.addEventListener('webglcontextlost',()=>{
      state.ready=false;area.classList.remove('map-dither-ready');
      if(!isMap){canvas.style.setProperty('display','none','important');field.art?.stage.classList.remove('site-art-ready');}
    });
    visibility(area,state,field);fields.set(area,field);return field;
  }
  function position(value,fallback){if(value==='left'||value==='top')return 0;if(value==='right'||value==='bottom')return 1;const number=parseFloat(value);return Number.isFinite(number)&&value.includes('%')?number/100:fallback;}
  function measureHeroArt(field){
    const art=field.art,{stage,img}=art,r=stage.getBoundingClientRect();
    if(!r.width||!r.height||!img.complete||!img.naturalWidth){art.rect=null;return false;}
    const styles=getComputedStyle(img),values=styles.objectPosition.split(' ');
    const scale=(styles.objectFit==='contain'?Math.min:Math.max)(r.width/img.naturalWidth,r.height/img.naturalHeight);
    const cx=r.width/(img.naturalWidth*scale),cy=r.height/(img.naturalHeight*scale);
    art.rect=r;art.crop=[cx,cy];art.offset=[(1-cx)*position(values[0],.5),(1-cy)*position(values[1],.5)];
    if(stage.dataset.artCrop){const [x,y,w,h]=stage.dataset.artCrop.split(' ').map(Number);art.crop=[w,h];art.offset=[x,y];}
    stage.dataset.artCompositeRect=[r.left-field.rect.left,r.top-field.rect.top,r.width,r.height].map(value=>value.toFixed(3)).join(' ');
    return true;
  }
  function heroArtUniforms(field){
    const {gl,u}=field.state,{stage,img,crop,offset}=field.art,profile=profiles[stage.dataset.artProfile];
    gl.uniform2f(u.crop,...crop);gl.uniform2f(u.offset,...offset);
    gl.uniform1f(u.printDepth,['map','footer'].includes(stage.dataset.artProfile)?.13:.34);
    gl.uniform1f(u.printPattern,stage.dataset.artPrintPattern==='drift'?2:0);
    gl.uniform1f(u.continuous,['scene','architecture','painting','footer','map'].includes(stage.dataset.artProfile)?1:0);
    gl.uniform2f(u.texel,1/img.naturalWidth,1/img.naturalHeight);
    gl.uniform1f(u.softness,setting(stage.dataset.artSoftness,profile?profile.softness:0));
    const edges=(stage.dataset.artFeather||(profile?profile.edges:'.24 .13 .17 .3')).split(' ').map(Number);
    gl.uniform4f(u.edgeFade,...edges);
    gl.uniform1f(u.printStrength,Math.max(0,Math.min(1,setting(innerWidth<=700?stage.dataset.mobileArtPrint??stage.dataset.artPrint:stage.dataset.artPrint,profile?profile.print:.72))));
    gl.uniform1f(u.atlas,stage.dataset.artColor==='atlas'?1:0);
    gl.uniform1f(u.clearPaper,stage.dataset.artAsset==='sword-hand'?1:0);
    stage.dataset.artTextureWidth=String(img.naturalWidth);
  }
  function setupHero(stage,img,field){
    function initialise(){
      try{
        field.uploadSource(img);field.art={stage,img,rect:null,crop:null,offset:null};
        stage.dataset.artLayers='base-static-moving';
        stage.dataset.artMotion=field.whiteSurface?'v1-threshold-and-wake':'luminance-edge-aware-tone';
        stage.dataset.artComposite='single-opaque-surface';stage.dataset.ditherCell='1-css-px';
        const refresh=()=>{field.measure();field.state.dirty=true;wake();};
        new ResizeObserver(refresh).observe(stage);refresh();
        img.addEventListener('load',()=>{if(img.naturalWidth){field.uploadSource(img);refresh();}});
      }catch(error){stage.classList.remove('site-art-ready');console.warn('Artwork uses its halftone base:',error.message);}
    }
    if(img.complete&&img.naturalWidth)initialise();else img.addEventListener('load',initialise,{once:true});
  }
  function setup(stage){
    const img=stage.querySelector('img');if(!img)return;
    const isHero=stage.dataset.siteArt==='hero',field=isHero?heroField(stage.closest('.hero,.page-hero')):null;
    if(isHero){if(field)setupHero(stage,img,field);return;}
    let initialised=false;
    function initialise(){
      // A cached image may already be decoded when its viewport gate opens.
      // Load and observer notifications must still create only one renderer.
      if(initialised||!img.complete||!img.naturalWidth)return;
      initialised=true;delete stage.dataset.artDeferred;
      const canvas=stage.querySelector('canvas')||document.createElement('canvas');canvas.className='site-art-tones';canvas.setAttribute('aria-hidden','true');if(!canvas.parentElement)stage.append(canvas);
      try{
        const state=renderer(canvas,imageFragment);if(!state){canvas.remove();return;}
        const {gl,u}=state;state.hero=isHero;stage.dataset.artLayers=isHero?'base-static-moving':'base-static';stage.dataset.artMotion=isHero&&field?.whiteSurface?'v1-threshold-and-wake':isHero?'luminance-edge-aware-tone':'static';
        const source=texture(state,gl.TEXTURE0);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,img);
        const trail=texture(state,gl.TEXTURE1),empty=document.createElement('canvas');empty.width=empty.height=1;gl.uniform1i(u.source,0);gl.uniform1i(u.trail,1);
        function measure(){const r=stage.getBoundingClientRect();if(!r.width||!r.height)return;const styles=getComputedStyle(img),values=styles.objectPosition.split(' '),scale=(styles.objectFit==='contain'?Math.min:Math.max)(r.width/img.naturalWidth,r.height/img.naturalHeight),cx=r.width/(img.naturalWidth*scale),cy=r.height/(img.naturalHeight*scale);state.crop=[cx,cy];state.offset=[(1-cx)*position(values[0],.5),(1-cy)*position(values[1],.5)];if(stage.dataset.artCrop){const [x,y,w,h]=stage.dataset.artCrop.split(' ').map(Number);state.crop=[w,h];state.offset=[x,y];}state.fit(r);stage.dataset.ditherCell='1-css-px';wake();}
        state.draw=time=>{
          // A responsive artwork may start hidden; wait until ResizeObserver measures it.
          if(!state.crop||!state.rect||(field&&!field.rect))return;
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
          gl.uniform1f(u.printStrength,Math.max(0,Math.min(1,setting(innerWidth<=700?stage.dataset.mobileArtPrint??stage.dataset.artPrint:stage.dataset.artPrint,profile?profile.print:(isHero?.72:.42)))));gl.uniform4f(u.edgeFade,...edges);gl.uniform1f(u.atlas,stage.dataset.artColor==='atlas'?1:0);
          gl.uniform3f(u.pointer,...(field?field.cursor:[0,0,0]));gl.uniform1f(u.clock,isHero?time:0);gl.uniform1f(u.motion,isHero&&!motionPaused()?1:0);gl.uniform1f(u.hero,isHero?1:0);gl.uniform1f(u.clearPaper,isHero&&stage.dataset.artAsset==='sword-hand'?1:0);gl.uniform1f(u.whiteSurface,field&&field.whiteSurface?1:0);gl.drawArrays(gl.TRIANGLES,0,6);stage.classList.add('site-art-ready');
        };
        new ResizeObserver(measure).observe(stage);measure();state.draw(motionPaused()?0:clock);visibility(stage,state);
        canvas.addEventListener('webglcontextlost',()=>{state.ready=false;stage.classList.remove('site-art-ready');});
      }catch(error){canvas.remove();console.warn('Artwork uses its halftone base:',error.message);}
    }
    nearViewport(stage,()=>{
      if(img.complete&&img.naturalWidth)initialise();else img.addEventListener('load',initialise,{once:true});
    });
  }
  // Native lazy images can decode far below the fold. Delay shader creation,
  // texture upload and map rasterisation until a separate 300px viewport gate.
  const deferredStarts=new WeakMap();
  const nearObserver=typeof IntersectionObserver==='function'?new IntersectionObserver(entries=>{
    for(const entry of entries){
      if(!entry.isIntersecting)continue;
      nearObserver.unobserve(entry.target);
      const start=deferredStarts.get(entry.target);deferredStarts.delete(entry.target);
      start?.();
    }
  },{rootMargin:'300px',threshold:0}):null;
  function nearViewport(element,start){
    let started=false;
    const once=()=>{if(started)return;started=true;start();};
    element.dataset.artDeferred='waiting';
    if(!nearObserver){once();return;}
    deferredStarts.set(element,once);nearObserver.observe(element);
  }
  document.querySelectorAll('[data-site-art]').forEach(setup);
  document.querySelectorAll('.world-map.dotted-map').forEach(map=>nearViewport(map,()=>{delete map.dataset.artDeferred;heroField(map,true);}));
  window.addEventListener('resize',()=>{const spacing=getComputedStyle(document.querySelector('#main')).paddingTop;fields.forEach(f=>{if(!f.area.classList.contains('dotted-map')){f.area.style.setProperty('--art-header-space',spacing);f.measure();}});},{passive:true});
  document.addEventListener('visibilitychange',()=>{last=0;if(!document.hidden){states.forEach(s=>s.dirty=true);wake();}});
  function resetMotion(){fields.forEach(f=>{f.pending=[];f.previous=null;f.cursor=[0,0,0];f.scrollStamp=null;f.ctx.fillStyle='#000';f.ctx.fillRect(0,0,f.trail.width,f.trail.height);});states.forEach(s=>s.dirty=true);last=0;wake();}
  reduced.addEventListener('change',resetMotion);
  let wasPaused=motionPaused();new MutationObserver(()=>{const paused=motionPaused();if(paused!==wasPaused){wasPaused=paused;resetMotion();}}).observe(document.body,{attributes:true,attributeFilter:['class']});
  window.addEventListener('aic:artwork-refresh',()=>{states.forEach(s=>s.dirty=true);wake();});
})();

