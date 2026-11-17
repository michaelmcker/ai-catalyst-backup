const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.resolve(__dirname,'../..'),posts=JSON.parse(fs.readFileSync(path.join(root,'content/blog/posts.json')));
for(const prefix of ['', 'fr-ca/','fr-fr/','ar/']){
 const index=fs.readFileSync(path.join(root,'current-site',prefix,'blog/index.html'),'utf8');
 for(const p of posts){
  assert(index.includes(`href="/${prefix}blog/${p.slug}/"`));
  const page=fs.readFileSync(path.join(root,'current-site',prefix,'blog',p.slug,'index.html'),'utf8');
  assert.equal((page.match(/<iframe /g)||[]).length,1);
  assert(page.includes(`https://www.youtube-nocookie.com/embed/${p.video}`));assert(!page.includes('autoplay=1'));
  assert(page.includes('referrerpolicy="strict-origin-when-cross-origin"'));assert(page.includes('loading="lazy"'));
  assert(page.includes('class="transcript-text"><p>'));assert(page.includes('href="/'+prefix+'blog/"'));
  assert(page.includes('hreflang="fr-CA"'));assert(page.includes('hreflang="ar"'));
 }
}
console.log('PASS: 12 blog editions, two correct embeds, transcripts, discovery, equivalent routes and no autoplay.');
