/* A shared tonal treatment for every subpage: real image dithering and an idle field. */
(() => {
  const hero = document.querySelector('.page-hero');
  if (!hero) return;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const pointer = {x:.5,y:.5,power:0};
  const draws = [];
  let inView = true, frame = 0, last = 0;
  hero.addEventListener('pointermove', e => {
    if (e.pointerType === 'touch') return;
    const r=hero.getBoundingClientRect();pointer.x=(e.clientX-r.left)/r.width;pointer.y=1-(e.clientY-r.top)/r.height;pointer.power=1;
  },{passive:true});
  hero.addEventListener('pointerleave',()=>pointer.power=0);
  const bayer = 'float b2(vec2 p){vec2 a=mod(floor(p),2.);return 2.*a.x+3.*a.y-4.*a.x*a.y;} float threshold(vec2 p){return (16.*b2(p)+4.*b2(p/2.)+b2(p/4.)+.5)/64.;}';
  function renderer(canvas, fragment) {
    const gl=canvas.getContext('webgl',{alpha:true,premultipliedAlpha:false,antialias:false,powerPreference:'low-power'});
    if(!gl)return null;
    function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;}
    const prog=gl.createProgram();
    gl.attachShader(prog,shader(gl.VERTEX_SHADER,'attribute vec2 p;varying vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}'));
    gl.attachShader(prog,shader(gl.FRAGMENT_SHADER,'precision highp float;varying vec2 uv;uniform vec2 size;uniform float time;uniform vec3 pointer;'+bayer+fragment));
    gl.linkProgram(prog);if(!gl.getProgramParameter(prog,gl.LINK_STATUS))throw new Error('Hero renderer unavailable');gl.useProgram(prog);
    const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
    const a=gl.getAttribLocation(prog,'p');gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,2,gl.FLOAT,false,0,0);
    const uniforms={};['size','time','pointer','crop','offset'].forEach(n=>uniforms[n]=gl.getUniformLocation(prog,n));
    return {gl,prog,uniforms,draw(t){
      const r=canvas.getBoundingClientRect(),scale=Math.min(1,1600/Math.max(1,r.width));
      const w=Math.max(1,Math.round(r.width*scale)),h=Math.max(1,Math.round(r.height*scale));
      if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;gl.viewport(0,0,w,h);}
      gl.useProgram(prog);gl.uniform2f(uniforms.size,w,h);gl.uniform1f(uniforms.time,t);gl.uniform3f(uniforms.pointer,pointer.x,pointer.y,pointer.power);
      gl.drawArrays(gl.TRIANGLES,0,6);
    }};
  }
  const atmosphere=hero.querySelector('.page-atmosphere,.platform-atmosphere');
  if(atmosphere)try{
    const field=renderer(atmosphere,`void main(){vec2 q=vec2(gl_FragCoord.x,size.y-gl_FragCoord.y)/900.;float t=time*.28;float bend=.18*sin(q.x*4.7+t)+.07*sin(q.x*8.-t*.6);float wave=.50+.26*sin((q.y+bend)*8.4+t)+.18*sin(q.x*4.8-q.y*2.7-t*.7);vec2 delta=(uv-pointer.xy)*vec2(size.x/size.y,1.);wave+=exp(-dot(delta,delta)/.018)*pointer.z*.28;float density=.07+clamp(wave,0.,1.)*.4;float dotInk=step(threshold(gl_FragCoord.xy),density);float edge=smoothstep(0.,.12,uv.y);gl_FragColor=vec4(.25,.49,.88,dotInk*.24*edge);}`);
    if(field)draws.push(t=>field.draw(t));
  }catch(e){console.warn('Hero atmosphere fallback',e.message);}
  const art=hero.querySelector('.page-hero__art:not(.page-hero__film)'),img=art?.querySelector('img');
  if(img){
    const setup=()=>{try{
      const canvas=document.createElement('canvas');canvas.className='hero-tones';canvas.setAttribute('aria-hidden','true');art.append(canvas);
      const rendererImage=renderer(canvas,`uniform sampler2D image;uniform vec2 crop;uniform vec2 offset;void main(){vec2 sampleUV=vec2(uv.x,1.-uv.y)*crop+offset;vec3 source=texture2D(image,sampleUV).rgb;float l=dot(source,vec3(.2126,.7152,.0722));float ink=clamp((.98-l)*1.4,0.,1.);float region=.5+.5*sin(uv.x*6.+uv.y*4.+time*.3);ink+=.018*(region-.5);vec2 delta=(uv-pointer.xy)*vec2(size.x/size.y,1.);ink+=exp(-dot(delta,delta)/.018)*pointer.z*.14;float stepped=floor(ink*3.)/3.+step(threshold(gl_FragCoord.xy),fract(ink*3.))/3.;float tone=mix(ink,stepped,.92);vec3 paper=vec3(.9294,.9686,1.);vec3 blue=vec3(.04,.20,.49);gl_FragColor=vec4(mix(paper,blue,clamp(tone,0.,1.)),1.);}`);
      if(!rendererImage){canvas.remove();return;}
      const {gl,uniforms}=rendererImage,texture=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,texture);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,img);
      draws.push(t=>{
        const triptych=img.src.includes("commerce-triptych"),panels=triptych?3:1,panelIndex=triptych?(document.body.classList.contains("conversion")?2:document.body.classList.contains("commerce")?1:0):0;
        const sourceWidth=img.naturalWidth/panels,r=art.getBoundingClientRect(),cover=Math.max(r.width/sourceWidth,r.height/img.naturalHeight),cx=r.width/(sourceWidth*cover),cy=r.height/(img.naturalHeight*cover);
        const values=getComputedStyle(img).objectPosition.split(' '),px=parseFloat(values[0])/100||0,py=values[1]==='bottom'?1:(parseFloat(values[1])/100||0);
        gl.uniform2f(uniforms.crop,cx/panels,cy);gl.uniform2f(uniforms.offset,(panelIndex+(1-cx)*px)/panels,(1-cy)*py);rendererImage.draw(t);art.classList.add('has-tones');
      });start();
    }catch(e){console.warn('Hero image fallback',e.message);}};
    if(img.complete&&img.naturalWidth)setup();else img.addEventListener('load',setup,{once:true});
  }
  function tick(now){frame=0;if(!inView||document.hidden)return;if(now-last>40){last=now;pointer.power*=.94;draws.forEach(draw=>draw(reduced.matches?0:now/1000));}if(!reduced.matches)frame=requestAnimationFrame(tick);}
  function start(){if(!frame)frame=requestAnimationFrame(tick);}
  new IntersectionObserver(entries=>{inView=entries[0].isIntersecting;start();},{threshold:0}).observe(hero);
  document.addEventListener('visibilitychange',start);reduced.addEventListener('change',start);window.addEventListener('resize',start,{passive:true});start();
})();
