const fs=require('fs'),vm=require('vm'),assert=require('assert/strict');
const script=fs.readFileSync('current-site/language-switcher.js','utf8');
function run(lang,languages,saved,blocked=false){
 const records={};const nodes=[];let suggestion;
 const make=()=>({dataset:{},children:[],addEventListener(t,f){this[t]=f;},append(...n){this.children.push(...n)},remove(){this.removed=true;}});
 const links=['en','fr-CA','fr-FR','ar'].map(l=>({...make(),dataset:{language:l},href:'https://example.test/'+l+'/solutions.html'}));
 const picker={...make(),querySelectorAll:()=>links,querySelector:()=>({focus(){records.focus=true}}),contains:()=>false};
 const document={documentElement:{lang},querySelector:s=>s==='.language-picker'?picker:{after(el){suggestion=el;}},addEventListener(){},createElement:()=>make(),getElementById:()=>true};
 const store={getItem(k){if(blocked)throw Error('blocked');return k==='aic-language'?saved:null;},setItem(k,v){if(blocked)throw Error('blocked');records[k]=v;}};
 vm.runInNewContext(script,{document,window:{localStorage:store,sessionStorage:store},location:{hash:'#contact'},navigator:{languages}});
 return {suggestion,links,picker,records};
}
assert.equal(run('ar',['fr-CA']).suggestion,undefined);
assert.equal(run('en',['fr-CA']).suggestion.children[0].href,'https://example.test/fr-CA/solutions.html');
assert.equal(run('en',['fr-BE']).suggestion.children[0].href,'https://example.test/fr-FR/solutions.html');
assert.equal(run('en',['ar-SA']).suggestion.children[0].href,'https://example.test/ar/solutions.html');
assert.equal(run('en',['de-DE']).suggestion,undefined);
assert.equal(run('en',['fr-CA'],'en').suggestion,undefined);
assert.ok(run('en',['ar-EG'],null,true).suggestion);
const result=run('en',['ar']);result.suggestion.children[1].click();assert.equal(result.records['aic-language-dismissed'],'1');
result.links[1].click();assert.equal(result.records['aic-language'],'fr-CA');
result.picker.keydown({key:'Escape'});assert.equal(result.records.focus,true);
console.log('PASS: browser-language priority, explicit URLs/choices, dismiss, blocked storage and Escape.');
