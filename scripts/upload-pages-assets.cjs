/* Encrypted project-token bridge; see docs/service-cleanup-2026-10-30/authentication.md. */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const b3 = require(process.env.AI_CATALYST_BLAKE3_MODULE || 'blake3-wasm');
const base = path.resolve(__dirname, '..');
const manifestPath = process.argv[3] || 'docs/service-cleanup-2026-10-30/manifest.json';
const manifest = JSON.parse(fs.readFileSync(path.resolve(base, manifestPath)));
const authDir = process.argv[2];
if (!authDir || !authDir.startsWith('/private/tmp/aicatalyst-pages-auth-')) throw Error('Expected the temporary directory created by prepare-pages-upload.cjs');
const mime = {html:'text/html',css:'text/css',js:'application/javascript',svg:'image/svg+xml',jpg:'image/jpeg',webp:'image/webp',png:'image/png',mp4:'video/mp4',json:'application/json',xml:'application/xml',woff2:'font/woff2'};
let token;
async function request(endpoint, body) {
  if (!['check-missing', 'upload', 'upsert-hashes'].includes(endpoint)) throw Error('Unsupported endpoint');
  const r = await fetch('https://api.cloudflare.com/client/v4/pages/assets/' + endpoint, {
    method:'POST', headers:{Authorization:'Bearer ' + token, 'Content-Type':'application/json'}, body:JSON.stringify(body)
  });
  const data = await r.json();
  if (!r.ok || !data.success) throw Error(endpoint + ' failed HTTP ' + r.status + ', codes: ' + (data.errors || []).map(e=>e.code).join(','));
  return data.result;
}
(async()=>{
  const files = new Map();
  if (!Object.keys(manifest).length || Object.keys(manifest).length > 20000) throw Error('Invalid release asset count');
  for (const [name, hash] of Object.entries(manifest)) {
    if (!name.startsWith('/') || name.includes('..')) throw Error('Invalid release path');
    const bytes = fs.readFileSync(path.join(base, 'current-site', name));
    const ext = path.extname(name).slice(1);
    if (b3.hash(bytes.toString('base64') + ext).toString('hex').slice(0,32) !== hash) throw Error('Changed asset: ' + name);
    files.set(hash, {key:hash,value:bytes.toString('base64'),metadata:{contentType:mime[ext] || 'application/octet-stream'},base64:true});
  }
  const envelope = JSON.parse(fs.readFileSync(path.join(authDir, 'envelope.json')));
  const key = crypto.privateDecrypt({key:fs.readFileSync(path.join(authDir, 'private.pem')),oaepHash:'sha256'},Buffer.from(envelope.wrappedKey,'base64'));
  const encrypted = Buffer.from(envelope.ciphertext,'base64');
  const decipher = crypto.createDecipheriv('aes-256-gcm',key,Buffer.from(envelope.iv,'base64'));
  decipher.setAuthTag(encrypted.subarray(-16));
  token = Buffer.concat([decipher.update(encrypted.subarray(0,-16)),decipher.final()]).toString();
  key.fill(0);
  const hashes = [...files.keys()];
  const missing = await request('check-missing', {hashes});
  if (!Array.isArray(missing) || missing.some(h=>!files.has(h))) throw Error('Unexpected missing hashes');
  console.log(JSON.stringify({stage:'authenticated',assets:hashes.length,missing:missing.length}));
  for(let i=0;i<missing.length;i+=5) {
    await request('upload', missing.slice(i,i+5).map(h=>files.get(h)));
    console.log(JSON.stringify({stage:'uploaded',completed:Math.min(i+5,missing.length),total:missing.length}));
  }
  await request('upsert-hashes',{hashes});
  const remaining = await request('check-missing',{hashes});
  if (remaining.length) throw Error('Release assets remain missing');
  const result={success:true,manifestPaths:Object.keys(manifest).length,uniqueAssets:hashes.length,uploaded:missing.length,missingAfter:0,authentication:'Encrypted project-scoped short-lived Pages token; general API credential stayed in MCP',checkedAt:new Date().toISOString()};
  fs.writeFileSync(path.join(base,'docs/service-cleanup-2026-10-30/asset-upload-result.json'), JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result));
})().catch(e=>{console.error(e.message);process.exitCode=1;}).finally(()=>{
  token=undefined;
  for(const name of ['private.pem','envelope.json','public.pem']) {try{fs.unlinkSync(path.join(authDir,name));}catch{}}
});
