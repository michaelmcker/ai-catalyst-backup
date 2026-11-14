/* Native links remain usable when JavaScript or preference storage is unavailable. */
(() => {
 'use strict';
 const current=document.documentElement.lang || 'en';
 const picker=document.querySelector('.language-picker');
 if(!picker)return;
 const get=(store,key)=>{try{return window[store].getItem(key);}catch{return null;}};
 const set=(store,key,value)=>{try{window[store].setItem(key,value);}catch{}};
 const links=[...picker.querySelectorAll('[data-language]')];
 links.forEach(link=>{
  if(location.hash && document.getElementById(location.hash.slice(1)))link.hash=location.hash;
  link.addEventListener('click',()=>set('localStorage','aic-language',link.dataset.language));
 });
 document.addEventListener('click',e=>{if(!picker.contains(e.target))picker.open=false;});
 picker.addEventListener('keydown',e=>{if(e.key==='Escape'){picker.open=false;picker.querySelector('summary').focus();}});
 // An explicit localized URL wins. On English, offer a preference without redirecting.
 if(current!=='en'||get('sessionStorage','aic-language-dismissed'))return;
 const saved=get('localStorage','aic-language');
 const resolve=(languages)=>{for(const raw of languages){const l=raw.toLowerCase();if(l==='en'||l.startsWith('en-'))return 'en';if(l==='fr-ca')return 'fr-CA';if(l==='fr'||l.startsWith('fr-'))return 'fr-FR';if(l==='ar'||l.startsWith('ar-'))return 'ar';}return 'en';};
 const preferred=['en','fr-CA','fr-FR','ar'].includes(saved)?saved:resolve(navigator.languages||[navigator.language||'en']);
 if(preferred==='en')return;
 const target=links.find(a=>a.dataset.language===preferred);if(!target)return;
 const copy={'fr-CA':['Lire cette page en français québécois','Fermer'],'fr-FR':['Lire cette page en français','Fermer'],'ar':['اقرأ هذه الصفحة بالعربية','إغلاق']}[preferred];
 const aside=document.createElement('aside');aside.className='language-suggestion';aside.lang=preferred;aside.dir=preferred==='ar'?'rtl':'ltr';
 const link=document.createElement('a');link.href=target.href;link.textContent=copy[0];link.addEventListener('click',()=>set('localStorage','aic-language',preferred));
 const close=document.createElement('button');close.type='button';close.textContent=copy[1];close.addEventListener('click',()=>{set('sessionStorage','aic-language-dismissed','1');aside.remove();});
 aside.append(link,close);document.querySelector('.masthead').after(aside);
})();
