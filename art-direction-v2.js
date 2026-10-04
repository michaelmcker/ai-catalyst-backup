/* One image treatment for v2. Source files remain unchanged. */
(() => {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const states = new Set();
  let frame = 0, last = 0;
  const vertex = 'attribute vec2 p;varying vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}';
  const fragment = `precision highp float;
    varying vec2 uv;
    uniform sampler2D source;
    uniform vec2 crop, offset, cssSize;
    uniform float pixelRatio, clock, motion;
    uniform vec3 pointer;
    float b2(vec2 p){vec2 a=mod(floor(p),2.);return 2.*a.x+3.*a.y-4.*a.x*a.y;}
    float ordered(vec2 p){return (16.*b2(p)+4.*b2(p/2.)+b2(p/4.)+.5)/64.;}
    void main(){
      vec3 paper=vec3(.9294118,.9686275,1.);
      vec3 pale=vec3(.76,.86,.97);
      vec3 middle=vec3(.49,.65,.84);
      vec3 navy=vec3(.08,.23,.47);
      vec2 imageUV=vec2(uv.x,1.-uv.y)*crop+offset;
      if(imageUV.x<0.||imageUV.x>1.||imageUV.y<0.||imageUV.y>1.){gl_FragColor=vec4(paper,1.);return;}
      vec3 original=texture2D(source,imageUV).rgb;
      vec3 weights=vec3(.2126,.7152,.0722);
      float paperLight=dot(paper,weights), paleLight=dot(pale,weights), middleLight=dot(middle,weights), navyLight=dot(navy,weights);
      float density=clamp((paperLight-dot(original,weights))/(paperLight-navyLight),0.,1.);
      // The source's pale blue matte must remain clear, not become a patterned sky.
      density*=smoothstep(.014,.080,density);
      float subject=smoothstep(.045,.18,density);
      vec2 delta=(vec2(uv.x,1.-uv.y)-pointer.xy)*cssSize;
      float local=exp(-dot(delta,delta)/(92.*92.))*pointer.z;
      // Change light within the image, never the grid's position or scale.
      float lightMotion=sin(uv.x*5.+uv.y*3.+clock*.28)*.0035*motion;
      density=clamp(density+subject*(lightMotion+local*.065),0.,1.);
      float middleDensity=(paperLight-middleLight)/(paperLight-navyLight);
      float paleDensity=(paperLight-paleLight)/(paperLight-navyLight);
      // A light ink keeps open sky quiet while the subject retains stronger dots.
      vec3 lightInk, darkInk; float amount;
      if(density<paleDensity){lightInk=paper;darkInk=pale;amount=density/paleDensity;}
      else if(density<middleDensity){lightInk=pale;darkInk=middle;amount=(density-paleDensity)/(middleDensity-paleDensity);}
      else{lightInk=middle;darkInk=navy;amount=(density-middleDensity)/(1.-middleDensity);}
      // A one-CSS-pixel grid at every breakpoint and display density.
      float threshold=ordered(floor(gl_FragCoord.xy/pixelRatio));
      gl_FragColor=vec4(mix(lightInk,darkInk,step(threshold,amount)),1.);
    }`;

  function wake() {
    if (!frame && !document.hidden) frame = requestAnimationFrame(tick);
  }
  function tick(now) {
    frame = 0;
    if (document.hidden) return;
    const dt = Math.min(.12, last ? (now-last)/1000 : 1/30);
    if (now-last < 1000/30) { wake(); return; }
    last = now;
    let continuing = false;
    for (const state of states) {
      if (!state.visible || !state.ready) continue;
      if (!state.hovering) state.pointer.power *= Math.exp(-dt*3.8);
      if (state.pointer.power < .002) state.pointer.power = 0;
      if (state.dirty || (!reduced.matches && (state.idle || state.pointer.power))) {
        state.draw(reduced.matches ? 0 : now/1000);
        state.dirty = false;
      }
      if (!reduced.matches && (state.idle || state.pointer.power)) continuing = true;
    }
    if (continuing) wake();
  }
  function position(value, axis) {
    if (value === 'left' || value === 'top') return 0;
    if (value === 'right' || value === 'bottom') return 1;
    if (value === 'center' || !value) return .5;
    const number = parseFloat(value);
    return Number.isFinite(number) && value.includes('%') ? number/100 : axis;
  }
  function setup(stage) {
    const img = stage.querySelector('img');
    if (!img) return;
    const initialise = () => {
      const canvas = stage.querySelector('canvas') || document.createElement('canvas');
      canvas.className = 'site-art-tones';
      canvas.setAttribute('aria-hidden','true');
      if (!canvas.parentElement) stage.append(canvas);
      const gl = canvas.getContext('webgl', {alpha:false, antialias:false, powerPreference:'low-power'});
      if (!gl) { canvas.remove(); return; }
      try {
        const shader = (type, text) => {
          const s = gl.createShader(type); gl.shaderSource(s,text); gl.compileShader(s);
          if (!gl.getShaderParameter(s,gl.COMPILE_STATUS)) throw Error(gl.getShaderInfoLog(s));
          return s;
        };
        const program = gl.createProgram();
        gl.attachShader(program,shader(gl.VERTEX_SHADER,vertex));
        gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fragment));
        gl.linkProgram(program);
        if (!gl.getProgramParameter(program,gl.LINK_STATUS)) throw Error('Artwork link failed');
        gl.useProgram(program);
        const buffer = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
        gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
        const a = gl.getAttribLocation(program,'p'); gl.enableVertexAttribArray(a); gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
        const texture = gl.createTexture(); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D,texture);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
        gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,img);
        const u = {};
        ['source','crop','offset','cssSize','pixelRatio','clock','motion','pointer'].forEach(n=>u[n]=gl.getUniformLocation(program,n));
        gl.uniform1i(u.source,0);
        const state = {stage, canvas, visible:false, ready:true, dirty:true, idle:stage.dataset.siteArt==='hero', hovering:false, pointer:{x:.5,y:.5,power:0}, width:0,height:0,ratio:1,crop:[1,1],offset:[0,0]};
        state.draw = time => {
          gl.useProgram(program);
          gl.uniform2f(u.crop,...state.crop); gl.uniform2f(u.offset,...state.offset);
          gl.uniform2f(u.cssSize,state.width,state.height); gl.uniform1f(u.pixelRatio,state.ratio);
          gl.uniform1f(u.clock,time); gl.uniform1f(u.motion,reduced.matches?0:1);
          gl.uniform3f(u.pointer,state.pointer.x,state.pointer.y,reduced.matches?0:state.pointer.power);
          gl.drawArrays(gl.TRIANGLES,0,6);
          stage.classList.add('site-art-ready');
        };
        function measure() {
          const r = stage.getBoundingClientRect();
          if (!r.width || !r.height) return;
          const style = getComputedStyle(img), values = style.objectPosition.split(' ');
          const contain = style.objectFit === 'contain';
          const scale = (contain?Math.min:Math.max)(r.width/img.naturalWidth,r.height/img.naturalHeight);
          const cx=r.width/(img.naturalWidth*scale),cy=r.height/(img.naturalHeight*scale);
          state.width=r.width; state.height=r.height;
          state.ratio=Math.min(devicePixelRatio||1,2,4096/Math.max(r.width,r.height));
          state.crop=[cx,cy]; state.offset=[(1-cx)*position(values[0],.5),(1-cy)*position(values[1],.5)];
          canvas.width=Math.max(1,Math.round(r.width*state.ratio));canvas.height=Math.max(1,Math.round(r.height*state.ratio));
          gl.viewport(0,0,canvas.width,canvas.height);stage.dataset.ditherCell='1-css-px';
          state.dirty=true;wake();
        }
        new ResizeObserver(measure).observe(stage);
        measure();states.add(state);
        new IntersectionObserver(entries=>{
          state.visible=entries[0].isIntersecting;
          if(state.visible){state.dirty=true;wake();}
        },{rootMargin:'80px',threshold:0}).observe(stage);
        const area=stage.closest('.hero,.page-hero') || stage;
        area.addEventListener('pointermove',e=>{
          if(e.pointerType==='touch'||reduced.matches)return;
          const r=stage.getBoundingClientRect();
          state.pointer.x=(e.clientX-r.left)/r.width;state.pointer.y=(e.clientY-r.top)/r.height;
          state.pointer.power=1;state.hovering=true;state.dirty=true;wake();
        },{passive:true});
        area.addEventListener('pointerleave',()=>{state.hovering=false;wake();});
        canvas.addEventListener('webglcontextlost',()=>{state.ready=false;stage.classList.remove('site-art-ready');});
      } catch (error) {
        canvas.remove();console.warn('v2 artwork uses the supplied image:',error.message);
      }
    };
    if(img.complete&&img.naturalWidth)initialise();else img.addEventListener('load',initialise,{once:true});
  }
  document.querySelectorAll('[data-site-art]').forEach(setup);
  document.addEventListener('visibilitychange',()=>{last=0;if(!document.hidden){states.forEach(s=>s.dirty=true);wake();}});
  reduced.addEventListener('change',()=>{states.forEach(s=>{s.pointer.power=0;s.dirty=true;});wake();});
})();
