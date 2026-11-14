/* Never show a receipt until transport confirms it. Destination configured at release. */
(() => {
 const localeMessages={"fr-CA": ["L’envoi du formulaire n’est pas connecté. Écrivez à randy@aicatalyst.biz ou appelez le 416-270-0132. Votre message n’a pas été envoyé.", "Envoi…", "Votre demande a été reçue. Nous communiquerons avec vous.", "Nous n’avons pas pu confirmer l’envoi. Veuillez réessayer. Votre message est toujours ici."], "fr-FR": ["L’envoi du formulaire n’est pas connecté. Écrivez à randy@aicatalyst.biz ou appelez le 416-270-0132. Votre message n’a pas été envoyé.", "Envoi…", "Votre demande a bien été reçue. Nous vous recontacterons.", "Nous n’avons pas pu confirmer l’envoi. Veuillez réessayer. Votre message est toujours présent."], "ar": ["إرسال النموذج غير متصل. راسل randy@aicatalyst.biz أو اتصل بالرقم 416-270-0132. لم يتم إرسال رسالتك.", "جارٍ الإرسال…", "تم استلام استفسارك. سنتواصل معك.", "تعذّر تأكيد الإرسال. يُرجى المحاولة مجددًا. لا تزال رسالتك محفوظة هنا."]};
 const msg=(i,fallback)=>localeMessages[document.documentElement.lang]?.[i]||fallback;
 const choice=document.querySelector('select[name=interest]');
 if(choice){const value=new URLSearchParams(location.search).get('interest');if([...choice.options].some(o=>o.value===value))choice.value=value;}
 document.querySelectorAll('form[data-enquiry]').forEach(form=>{
  const status=form.querySelector('.form-status');
  const endpoint=form.dataset.endpoint||document.querySelector('meta[name="enquiry-endpoint"]')?.content;
  const contact=form.previousElementSibling;
  form.hidden=!endpoint;
  if(contact?.classList.contains('enquiry-contact'))contact.hidden=Boolean(endpoint);
  form.addEventListener('submit',async event=>{
   event.preventDefault();if(!form.reportValidity())return;
   if(!endpoint){status.classList.add('is-error');status.textContent=msg(0,"Enquiry delivery is not connected. Email randy@aicatalyst.biz or call 416-270-0132. Your message has not been sent.");status.focus();return;}
   const button=form.querySelector('[type=submit]');const original=button.textContent;button.disabled=true;button.textContent=msg(1,"Sending\u2026");form.setAttribute('aria-busy','true');status.classList.remove('is-error');status.textContent='';
   try{const response=await fetch(endpoint,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});if(!response.ok)throw new Error('Delivery not confirmed');const receipt=await response.json();if(receipt.success!==true)throw new Error('Receipt not confirmed');status.textContent=msg(2,"Your enquiry has been received. We will be in touch.");form.reset();}
   catch(error){status.classList.add('is-error');status.textContent=msg(3,"We could not confirm delivery. Please try again. Your message is still here.");}
   finally{button.disabled=false;button.textContent=original;form.removeAttribute('aria-busy');status.focus();}
  });
 });
})();
