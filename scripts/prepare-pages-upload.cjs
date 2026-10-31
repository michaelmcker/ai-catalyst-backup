/* Produces MCP code containing only a public encryption key, never credentials. */
const fs=require('node:fs');
const crypto=require('node:crypto');
const dir=fs.mkdtempSync('/private/tmp/aicatalyst-pages-auth-');
fs.chmodSync(dir,0o700);
const keys=crypto.generateKeyPairSync('rsa',{modulusLength:2048,publicKeyEncoding:{type:'spki',format:'pem'},privateKeyEncoding:{type:'pkcs8',format:'pem'}});
fs.writeFileSync(dir+'/private.pem',keys.privateKey,{mode:0o600});
fs.writeFileSync(dir+'/public.pem',keys.publicKey,{mode:0o600});
const code=`async()=>{
 const t=await cloudflare.request({method:'GET',path:\`/accounts/\${accountId}/pages/projects/ai-catalyst/upload-token\`});
 if(!t.success||!t.result?.jwt)throw Error('No project upload token');
 const pem=${JSON.stringify(keys.publicKey)};
 const bytes=Uint8Array.from(atob(pem.replace(/-----[^-]+-----|\\s/g,'')),c=>c.charCodeAt(0));
 const publicKey=await crypto.subtle.importKey('spki',bytes,{name:'RSA-OAEP',hash:'SHA-256'},false,['encrypt']);
 const aes=crypto.getRandomValues(new Uint8Array(32)),iv=crypto.getRandomValues(new Uint8Array(12));
 const key=await crypto.subtle.importKey('raw',aes,'AES-GCM',false,['encrypt']);
 const cipher=await crypto.subtle.encrypt({name:'AES-GCM',iv},key,new TextEncoder().encode(t.result.jwt));
 const wrapped=await crypto.subtle.encrypt({name:'RSA-OAEP'},publicKey,aes);
 const b64=b=>btoa(String.fromCharCode(...new Uint8Array(b)));
 return {algorithm:'RSA-OAEP-SHA256/AES-256-GCM',wrappedKey:b64(wrapped),iv:b64(iv),ciphertext:b64(cipher)};
}`;
fs.writeFileSync(dir+'/mcp-execute.js',code,{mode:0o600});
console.log(JSON.stringify({directory:dir,mcpAccount:'bbbb85e86074305e7fd5623be9406076',code}));
