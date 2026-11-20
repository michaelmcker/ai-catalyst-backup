const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const fs=require('fs'),http=require('http'),path=require('path'),assert=require('assert');
const root=process.cwd()+'/current-site';
(async()=>{
const server=http.createServer((q,r)=>{let f=path.join(root,decodeURIComponent(q.url.split('?')[0]));if(fs.existsSync(f)&&fs.statSync(f).isDirectory())f+='/index.html';if(!fs.existsSync(f)){r.writeHead(404);r.end();return}r.setHeader('Content-Type',({'.html':'text/html','.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml','.webp':'image/webp','.jpg':'image/jpeg','.ttf':'font/ttf','.woff2':'font/woff2'})[path.extname(f)]||'application/octet-stream');r.end(fs.readFileSync(f))});
await new Promise(ok=>server.listen(8773,'127.0.0.1',ok));
const browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? {executablePath:process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE} : {})});
const results=[];
for(const reducedMotion of ['no-preference','reduce']){
const page=await browser.newPage({reducedMotion});await page.route('https://**/*',r=>r.abort());
for(const width of [1440,1024,768,390,320])for(const prefix of ['','fr-ca/','fr-fr/','ar/']){
await page.setViewportSize({width,height:900});await page.goto('http://localhost:8773/'+prefix+'platform.html',{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);for(const id of ['signals','allocation']){await page.locator('#'+id).scrollIntoViewIfNeeded();await page.waitForTimeout(250)}await page.locator('.command-introduction').scrollIntoViewIfNeeded();await page.waitForTimeout(400);
const result=await page.evaluate(()=>{
const box=s=>{const e=document.querySelector(s),r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height,right:r.right,bottom:r.bottom}};
return {width:innerWidth,locale:document.documentElement.lang,motion:matchMedia('(prefers-reduced-motion:reduce)').matches,overflow:document.documentElement.scrollWidth-innerWidth,headingSize:parseFloat(getComputedStyle(document.querySelector("#command-title")).fontSize),copy:box('.command-introduction__copy'),film:box('.command-introduction__film'),graphics:['chat-scene','signals','allocation'].map(id=>{const e=document.getElementById(id),r=e.getBoundingClientRect();let painted=null;if(e.tagName==='CANVAS'){const data=e.getContext('2d').getImageData(0,0,e.width,e.height).data;painted=data.some((v,i)=>i%4===3&&v>0)}return {id,w:r.width,h:r.height,hidden:!!e.closest('[hidden],[aria-hidden="true"]'),painted}}),iframes:document.querySelectorAll('.service-film iframe').length};
});
assert(result.overflow<=1,JSON.stringify(result));assert(result.iframes===0);assert(result.headingSize<=64,JSON.stringify(result));assert(result.graphics.every(g=>g.w>0&&g.h>0&&!g.hidden&&g.painted!==false),JSON.stringify(result));
if(width<1000)assert(result.film.bottom<=result.copy.y+1,JSON.stringify(result));else if(prefix==='ar/')assert(result.film.right<=result.copy.x+1,JSON.stringify(result));else assert(result.copy.right<=result.film.x+1,JSON.stringify(result));
results.push(result);
if(reducedMotion==='no-preference'&&[1440,390].includes(width)&&['','ar/'].includes(prefix))await page.screenshot({path:'/private/tmp/aic-command-'+(prefix?'ar':'en')+'-'+width+'.png'});
const play=page.locator('.command-introduction .service-film__play');await play.focus();await page.keyboard.press('Enter');const frame=page.locator('.command-introduction iframe');await frame.waitFor();assert((await frame.getAttribute('src')).includes('/NkQtLriHVbA?'));assert(await frame.getAttribute('title'));
}
await page.close();
}
fs.writeFileSync('/private/tmp/aic-command-results.json',JSON.stringify(results,null,2));console.log('PASS: '+results.length+' locale/width/motion cases, painted graphics, RTL/mobile ordering, no overflow and keyboard player activation.');await browser.close();server.close();
})().catch(e=>{console.error(e);process.exit(1)});
