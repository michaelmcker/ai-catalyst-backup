(() => {
  const $ = (s, root = document) => root.querySelector(s);
  const tau = Math.PI * 2;
  const clamp = (n, a = 0, b = 1) => Math.max(a, Math.min(b, n));
  const ease = n => 1 - Math.pow(1 - clamp(n), 3);
  const reducedMedia = matchMedia('(prefers-reduced-motion: reduce)');
  const reduce = reducedMedia.matches;
  const running = new WeakMap();
  function canvasContext(canvas, w, h) {
    const ctx = canvas.getContext('2d');
    const resize = () => { const css = canvas.getBoundingClientRect(); const dpr = Math.min(devicePixelRatio || 1, 2); canvas.width = Math.max(1, Math.round(css.width * dpr)); canvas.height = Math.max(1, Math.round(css.width * h / w * dpr)); ctx.setTransform(canvas.width / w, 0, 0, canvas.height / (h + 32), 0, canvas.height * 16 / (h + 32)); canvas.dispatchEvent(new Event("canvasresize")); };
    new ResizeObserver(resize).observe(canvas); resize(); return ctx;
  }
  function animate(el, draw, duration = 5, options = {}) {
    if (!el) return;
    let visible = false, start = 0, frame = 0, last = 0;
    const staticFrame = () => draw(el.dataset.storyTime !== undefined ? Number(el.dataset.storyTime) : duration, 0, true);
    const stop = () => { cancelAnimationFrame(frame); frame = 0; };
    const tick = now => {
      if (!visible || document.hidden || reducedMedia.matches) { frame = 0; return; }
      if (!start) start = now;
      const raw = (now - start) / 1000, t = options.loop ? raw : Math.min(raw, duration);
      draw(el.dataset.storyTime !== undefined ? Number(el.dataset.storyTime) : t, (now - last) / 1000, false); last = now;
      frame = options.loop || (raw < duration && el.dataset.storyTime === undefined) ? requestAnimationFrame(tick) : 0;
    };
    const resume = () => { if (visible && !document.hidden && !frame && !reducedMedia.matches) { last = performance.now(); frame = requestAnimationFrame(tick); } };
    const io = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; if (!visible) stop(); else if (reducedMedia.matches) staticFrame(); else resume(); }, { threshold: .18 });
    io.observe(el); running.set(el, io);
    el.addEventListener('storychange', () => { if (reducedMedia.matches) staticFrame(); else { draw(Number(el.dataset.storyTime) || duration, 0, false); resume(); } });
    el.addEventListener('canvasresize', () => { if (reducedMedia.matches || !frame) staticFrame(); });
    document.addEventListener('visibilitychange', () => { if (document.hidden) stop(); else resume(); });
    reducedMedia.addEventListener('change', () => { stop(); if (reducedMedia.matches) staticFrame(); else { start = 0; resume(); } });
    if (reducedMedia.matches) staticFrame();
  }
  const signals = $('#signals');
  if (signals) {
    const sx = canvasContext(signals, 720, 390), names = ['Creators', 'Video', 'Social', 'Live', 'Reviews', 'Communities'], peakX = [.55,.62,.43,.49,.55,.47], peakAmp = [-38,-28,18,-27,-21,-32];
    const signalParticles = Array.from({ length: 6 }, (_, row) => Array.from({ length: 115 }, (_, i) => { const depth = i % 3, seed = Math.sin(i * 127.1 + row * 311.7) * 43758.5453, random = seed - Math.floor(seed); return { phase: (i * .61803398875 + row * .17) % 1, depth, radius: [.85, 1.3, 1.9][depth] + random * .35, offset: (random - .5) * [58, 34, 6][depth], speed: [1/32, 1/24, 1/16][depth], alpha: [.2, .4, .73][depth] }; }));
    const signalCloud = Array.from({ length: 210 }, (_, i) => ({ x: (i * .61803398875) % 1, y: 25 + ((i * 97) % 330), radius: .65 + (i % 5) * .27, alpha: .11 + (i % 4) * .045 }));
    const signalPeak = (row, t) => peakX[row] + .022 * Math.sin(t * Math.PI * 2 / 18 + row * .65);
    const signalY = (x, row, t = 0) => { const center = signalPeak(row, t), breath = 1 + .22 * Math.sin(t * Math.PI * 2 / 14 + row * .8), width = .078 + .009 * Math.sin(t * Math.PI * 2 / 20 + row), main = peakAmp[row] * breath * Math.exp(-Math.pow((x - center) / width, 2)), shoulder = (row % 2 ? -12 : 8) * (1 + .16 * Math.sin(t * .35 + row)) * Math.exp(-Math.pow((x - (row % 2 ? .11 : .38)) / .1, 2)), trough = (row > 3 ? 17 : 4) * Math.exp(-Math.pow((x - .63) / .085, 2)); return 55 + row * 55 + main + shoulder + trough + 1.5 * Math.sin(x * 18 + row) * Math.sin(Math.PI * x); };
    animate(signals, t => { sx.clearRect(0, 0, 720, 390); sx.font = (signals.clientWidth<440?25:16) + 'px "Helvetica Neue",Arial'; sx.textBaseline = 'middle'; const left = signals.clientWidth<440?180:108, width = 704-left, anchors = [];
      for (const p of signalCloud) { const x = ((p.x - t / 48) % 1 + 1) % 1, edge = Math.min(clamp(x * 12), clamp((1 - x) * 12)); sx.globalAlpha = p.alpha * edge; sx.fillStyle = '#4d83e9'; sx.beginPath(); sx.arc(left + x * width, p.y + 6 * Math.sin(p.x * 12), p.radius, 0, tau); sx.fill(); }
      for (let row = 0; row < 6; row++) { const base = 55 + row * 55; sx.globalAlpha = 1; sx.fillStyle = '#5279c6'; sx.fillText(names[row], 0, base); for (const p of signalParticles[row]) { if (p.depth === 2) continue; const x = (p.phase + t * p.speed) % 1, edge = Math.min(clamp(x * 18), clamp((1 - x) * 12)); sx.globalAlpha = p.alpha * edge; sx.fillStyle = '#3777ed'; sx.beginPath(); sx.arc(left + x * width, signalY(x, row, t) + p.offset * (.7 + .3 * Math.sin(x * Math.PI)), p.radius, 0, tau); sx.fill(); } sx.globalAlpha = 1; const fade = sx.createLinearGradient(left, 0, left + width, 0); fade.addColorStop(0, '#7ba8fa'); fade.addColorStop(.65, '#4174f6'); fade.addColorStop(1, '#b2d0fb'); sx.strokeStyle = fade; sx.lineWidth = signals.dataset.activeStory==='1'&&[1,2].includes(row)||signals.dataset.activeStory==='2'&&[0,5].includes(row)?2.6:1.35; sx.beginPath(); for (let i = 0; i <= 220; i++) { const x = i / 220, y = signalY(x, row, t); i ? sx.lineTo(left + x * width, y) : sx.moveTo(left + x * width, y); } sx.stroke(); for (const p of signalParticles[row]) { if (p.depth !== 2) continue; const x = (p.phase + t * p.speed) % 1, edge = Math.min(clamp(x * 22), clamp((1 - x) * 10)); sx.globalAlpha = p.alpha * edge; sx.fillStyle = '#205af2'; sx.beginPath(); sx.arc(left + x * width, signalY(x, row, t) + p.offset, p.radius, 0, tau); sx.fill(); } if ([0,1,3,4].includes(row)) anchors.push([left + signalPeak(row, t) * width, signalY(signalPeak(row, t), row, t)]); }
      sx.globalAlpha = 1; sx.strokeStyle = '#3d6cff'; sx.lineWidth = 1; sx.setLineDash([2,5]); sx.beginPath(); anchors.forEach(([x,y], i) => { if (i) { sx.lineTo(x, anchors[i-1][1]); sx.lineTo(x,y); } else sx.moveTo(x,y); }); sx.stroke(); sx.setLineDash([]); for (const [x,y] of anchors) { sx.fillStyle = '#edf7ff'; sx.strokeStyle = '#103fea'; sx.lineWidth = 1.8; sx.beginPath(); sx.arc(x,y,7,0,tau); sx.fill(); sx.stroke(); sx.fillStyle = '#245aff'; sx.beginPath(); sx.arc(x,y,2,0,tau); sx.fill(); }
    }, 6, {loop:true});
  }
  const wall = $('.platform-command .signal-wall');
  if (wall) { const wx = wall.getContext('2d'), dots = Array.from({length: 580}, (_, i) => ({ x: (i * .61803398875) % 1, y: (i * .754877666) % 1, r: .7 + (i % 4) * .35, a: .07 + (i % 5) * .026 })); animate(wall, t => { const r = wall.getBoundingClientRect(), w = Math.max(1, Math.round(r.width)), h = Math.max(1, Math.round(r.height)); if (wall.width !== w || wall.height !== h) { wall.width = w; wall.height = h; } wx.clearRect(0,0,w,h); for (const p of dots) { const x = ((p.x - t / 65) % 1 + 1) % 1, edge = Math.min(clamp(x * 12), clamp((1 - x) * 12), clamp(p.y * 10), clamp((1 - p.y) * 10)); wx.globalAlpha = p.a * edge; wx.fillStyle = '#447cdf'; wx.beginPath(); wx.arc(x * w, p.y * h, p.r, 0, tau); wx.fill(); } wx.globalAlpha = 1; }, 999, { loop: true }); }
  const chat = $('#chat-scene');
  if (chat) { const bubbles = [...chat.querySelectorAll('.bubble')], products = [...chat.querySelectorAll('.product')], connectors = chat.querySelector('.chat-connectors'), ns = 'http://www.w3.org/2000/svg', defs = document.createElementNS(ns,'defs'); defs.innerHTML = '<clipPath id="platform-connector-mask"><rect id="platform-connector-window" x="0" y="190" width="620" height="0"/></clipPath>'; chat.prepend(defs); connectors.setAttribute('clip-path','url(#platform-connector-mask)'); const clip = $('#platform-connector-window');
    const show = (el, p, cx, cy) => { el.style.opacity = String(p); el.setAttribute('transform', `translate(${cx} ${cy + (1-p) * 9}) scale(${.965 + .035 * p}) translate(${-cx} ${-cy})`); };
    animate(chat, t => { const phase = (t * 1.7) % 6; show(bubbles[0], ease((phase-.35)/.55), 200, 60); show(bubbles[1], ease((phase-1.65)/.55), 400, 150); clip.setAttribute('height', String(ease((phase-2.55)/.85) * 72)); products.forEach((g,i) => show(g, ease((phase-3.25-i*.2)/.5), 102+i*208, 330)); chat.querySelectorAll('.typing circle').forEach((c,i) => c.style.opacity = String(.4 + .6 * (1 + Math.sin(t * 4 - i)) / 2)); }, 6, {loop:true});
  }
  const bars = $('#allocation');
  if (bars) { const bx = canvasContext(bars,720,390), values = [[.91,.78],[.55,.41],[.73,.6],[.37,.24]], labels = ['Brand','Retail media','Trade','Creator']; animate(bars, t => { bx.clearRect(0,0,720,390); bx.font = (bars.clientWidth < 440 ? 26 : 17) + 'px "Helvetica Neue",Arial'; bx.textAlign='right'; bx.textBaseline='middle'; const compact=bars.clientWidth<440, left=compact?175:128,max=compact?506:553; bx.strokeStyle='#6388e2'; bx.lineWidth=1; bx.beginPath(); bx.moveTo(left,14); bx.lineTo(left,348); bx.stroke(); for(let row=0;row<4;row++){let y=39+row*82; bx.fillStyle='#4b73c0'; bx.fillText(labels[row],left-21,y+15); for(let k=0;k<2;k++){let p=ease((t-row*.14-k*.08)/1.7), len=max*values[row][k]*p, yy=y+k*27, col=k?'#88b2f2':'#1c59ef'; const solid=Math.max(0,len-57); bx.globalAlpha=bars.dataset.activeStory==='0'&&k===1?.12:bars.dataset.activeStory==='2'&&k===0?.3:1; bx.fillStyle=col; bx.fillRect(left,yy,solid,20); for(let x=0;x<63;x+=4){let density=clamp(1-x/63); for(let dotY=0;dotY<20;dotY+=4){let wave=.5+.5*Math.sin(x*.24+dotY*.61+t*tau/5); bx.globalAlpha=clamp(density*.9+wave*.23-.08); bx.beginPath(); bx.arc(left+solid+x,yy+dotY+2,(.38+1.4*density)*Math.min(1,p*3),0,tau); bx.fill(); } } bx.globalAlpha=1; } } bx.textAlign='left'; }, 5);
  }
  const chart = $('.tradeoffs .response-chart');
  if (chart) {
    // Keep the chart useful before motion starts. The previous version hid every
    // curve at load, leaving a blank graphic when someone scrolls past quickly.
    const paths = [...chart.querySelectorAll('.curve')];
    let played = false;
    const playChart = () => {
      if (played || reduce) return;
      played = true;
      const lengths = paths.map(p => p.getTotalLength());
      paths.forEach((p, i) => { p.style.strokeDasharray = lengths[i]; p.style.strokeDashoffset = lengths[i] * .18; });
      const started = performance.now();
      const draw = now => {
        const t = Math.min((now - started) / 1250, 1);
        paths.forEach((p, i) => { p.style.strokeDashoffset = lengths[i] * .18 * (1 - ease((t - i * .12) / .7)); });
        if (t < 1) requestAnimationFrame(draw);
      };
      requestAnimationFrame(draw);
    };
    const chartObserver = new IntersectionObserver(entries => {
      if (entries.some(entry => entry.isIntersecting)) { playChart(); chartObserver.disconnect(); }
    }, { threshold: .42 });
    chartObserver.observe(chart);
  }
})();

(() => {
 const items=[...document.querySelectorAll('.evidence-flow li')];
 if(!items.length || matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
  if(entry.isIntersecting){entry.target.classList.add('is-visible');observer.unobserve(entry.target);}
 }),{threshold:.18});
 items.forEach((item,i)=>{item.classList.add('motion-ready');item.style.transitionDelay=(i%3)*120+'ms';observer.observe(item);});
})();

