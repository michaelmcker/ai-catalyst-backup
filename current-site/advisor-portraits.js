/* Fine static blue printing, retaining the photographs' facial tones. */
(() => {
  const ink=[12,48,112],paper=[232,244,255],cell=1;
  const order=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5];
  document.querySelectorAll('[data-portrait-print]').forEach(stage => {
    const image=stage.querySelector('img'),canvas=document.createElement('canvas');
    canvas.className='advisor-print';canvas.setAttribute('aria-hidden','true');
    stage.append(canvas);
    function draw(){
      if(!image.complete||!image.naturalWidth)return;
      const r=stage.getBoundingClientRect();if(!r.width||!r.height)return;
      const cols=Math.ceil(r.width/cell),rows=Math.ceil(r.height/cell);
      const sample=document.createElement('canvas');sample.width=cols;sample.height=rows;
      const ctx=sample.getContext('2d',{willReadFrequently:true});
      const scale=Math.max(cols/image.naturalWidth,rows/image.naturalHeight)*(Number(stage.dataset.portraitZoom)||1);
      const width=image.naturalWidth*scale,height=image.naturalHeight*scale;
      const vertical=stage.dataset.portraitY===undefined?.4:Number(stage.dataset.portraitY);
      ctx.drawImage(image,(cols-width)/2,(rows-height)*vertical,width,height);
      const pixels=ctx.getImageData(0,0,cols,rows),data=pixels.data;
      for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){
        const at=(y*cols+x)*4;
        const lum=(data[at]*.299+data[at+1]*.587+data[at+2]*.114)/255;
        const light=Math.min(1,Math.max(0,(lum-.04)/.96));
        const printed=light>(order[(y%4)*4+x%4]+.5)/16?1:0;
        const tone=light*.76+printed*.24;
        for(let c=0;c<3;c++)data[at+c]=Math.round(ink[c]+(paper[c]-ink[c])*tone);
        data[at+3]=255;
      }
      ctx.putImageData(pixels,0,0);
      const ratio=Math.min(devicePixelRatio||1,2);canvas.width=Math.round(r.width*ratio);canvas.height=Math.round(r.height*ratio);
      const out=canvas.getContext('2d');out.setTransform(ratio,0,0,ratio,0,0);out.imageSmoothingEnabled=false;
      out.drawImage(sample,0,0,r.width,r.height);
      stage.dataset.portraitCell='1-css-px';
      stage.classList.add('portrait-ready');
    }
    new ResizeObserver(draw).observe(stage);
    if(image.complete)draw();else image.addEventListener('load',draw,{once:true});
  });
})();
