(() => {
  const frame = document.querySelector('.page-hero__film');
  if (!frame) return;
  const video = frame.querySelector('.film-preview'), canvas = frame.querySelector('.film-tones');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const gl = canvas.getContext('webgl', {alpha:false, antialias:false, powerPreference:'low-power'});
  let visible = true, raf = 0, last = 0;
  const play = () => { if (visible && !reduced.matches && !document.hidden) video.play().catch(() => {}); else video.pause(); };
  if (gl) {
    const shader = (type, source) => { const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error('Preview shader unavailable');return s; };
    try {
      const program=gl.createProgram();
      gl.attachShader(program,shader(gl.VERTEX_SHADER,'attribute vec2 p;varying vec2 uv;void main(){uv=p*.5+.5;gl_Position=vec4(p,0.,1.);}'));
      gl.attachShader(program,shader(gl.FRAGMENT_SHADER,`precision mediump float;varying vec2 uv;uniform sampler2D film;float b2(vec2 p){vec2 a=mod(floor(p),2.);return 2.*a.x+3.*a.y-4.*a.x*a.y;}void main(){vec3 c=texture2D(film,vec2(.5+(uv.x-.5)*.5625,1.-uv.y)).rgb;float l=dot(c,vec3(.2126,.7152,.0722));float dark=clamp((.965-l)*1.36,0.,1.);vec2 px=floor(gl_FragCoord.xy/1.25);float threshold=(16.*b2(px)+4.*b2(px/2.)+b2(px/4.)+.5)/64.;float quant=floor(dark*4.)/4.;float dots=step(threshold,fract(dark*4.))/4.;float tone=mix(dark,quant+dots,.85);vec3 paper=vec3(.9294,.9686,1.);vec3 ink=vec3(.035,.15,.43);gl_FragColor=vec4(mix(paper,ink,tone),1.);}`));
      gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error('Preview shader unavailable');gl.useProgram(program);
      const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);
      const p=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(p);gl.vertexAttribPointer(p,2,gl.FLOAT,false,0,0);
      const tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
      function draw(now) {
        raf=0;if(!visible||document.hidden)return;
        if(video.readyState>=2 && now-last>40){last=now;const size=Math.min(900,Math.round(frame.clientWidth*(devicePixelRatio||1)));if(canvas.width!==size){canvas.width=size;canvas.height=size;gl.viewport(0,0,size,size);}gl.texImage2D(gl.TEXTURE_2D,0,gl.RGB,gl.RGB,gl.UNSIGNED_BYTE,video);gl.drawArrays(gl.TRIANGLES,0,6);frame.classList.add('film-is-ready');}
        if(!reduced.matches)raf=requestAnimationFrame(draw);
      }
      const start=()=>{play();if(!raf)raf=requestAnimationFrame(draw);};
      video.addEventListener('loadeddata',start);
      new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;start();},{threshold:.01}).observe(frame);
      document.addEventListener('visibilitychange',start);reduced.addEventListener('change',start);
      start();
    } catch { play(); }
  } else play();
})();
