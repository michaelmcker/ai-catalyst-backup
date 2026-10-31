const assert=require('node:assert/strict');
const fs=require('node:fs');
const crypto=require('node:crypto');
const vm=require('node:vm');
const {execFileSync}=require('node:child_process');
const path=require('node:path');
const plan=JSON.parse(execFileSync(process.execPath,[path.join(__dirname,'prepare-pages-upload.cjs')],{encoding:'utf8'}));
const fixture='non-secret-upload-test-fixture';
function decrypt(envelope,privateKey){
 const key=crypto.privateDecrypt({key:privateKey,oaepHash:'sha256'},Buffer.from(envelope.wrappedKey,'base64'));
 const cipher=Buffer.from(envelope.ciphertext,'base64');
 const decoder=crypto.createDecipheriv('aes-256-gcm',key,Buffer.from(envelope.iv,'base64'));
 decoder.setAuthTag(cipher.subarray(-16));
 return Buffer.concat([decoder.update(cipher.subarray(0,-16)),decoder.final()]).toString();
}
(async()=>{
 assert.equal(fs.statSync(plan.directory).mode&0o777,0o700);
 assert.equal(fs.statSync(plan.directory+'/private.pem').mode&0o777,0o600);
 const context={crypto:crypto.webcrypto,TextEncoder,btoa,atob,accountId:plan.mcpAccount,cloudflare:{request:async request=>{
  assert.equal(request.method,'GET');
  assert.equal(request.path,'/accounts/'+plan.mcpAccount+'/pages/projects/ai-catalyst/upload-token');
  return {success:true,result:{jwt:fixture}};
 }}};
 const envelope=await vm.runInNewContext('('+plan.code+')()',context);
 const privateKey=fs.readFileSync(plan.directory+'/private.pem');
 assert.equal(decrypt(envelope,privateKey),fixture);
 assert(!JSON.stringify(envelope).includes(fixture));
 const corrupt={...envelope};const bytes=Buffer.from(corrupt.ciphertext,'base64');bytes[0]^=1;corrupt.ciphertext=bytes.toString('base64');
 assert.throws(()=>decrypt(corrupt,privateKey));
 const wrong=crypto.generateKeyPairSync('rsa',{modulusLength:2048});
 assert.throws(()=>decrypt(envelope,wrong.privateKey));
 console.log('PASS: MCP WebCrypto to local Node round-trip; private file modes, tamper detection and wrong-key rejection.');
})().catch(e=>{console.error(e.message);process.exitCode=1;}).finally(()=>{
 for(const name of ['private.pem','public.pem','mcp-execute.js'])fs.unlinkSync(plan.directory+'/'+name);
 fs.rmdirSync(plan.directory);
});
