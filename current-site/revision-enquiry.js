/* Never show a receipt until transport confirms it. Destination configured at release. */
(() => {
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
   if(!endpoint){status.classList.add('is-error');status.textContent='Enquiry delivery is not connected. Please contact AI Catalyst on LinkedIn. Your message has not been sent.';status.focus();return;}
   const button=form.querySelector('[type=submit]');const original=button.textContent;button.disabled=true;button.textContent='Sending…';form.setAttribute('aria-busy','true');status.classList.remove('is-error');status.textContent='';
   try{const response=await fetch(endpoint,{method:'POST',body:new FormData(form),headers:{Accept:'application/json'}});if(!response.ok)throw new Error('Delivery not confirmed');const receipt=await response.json();if(receipt.success!==true)throw new Error('Receipt not confirmed');status.textContent='Your enquiry has been received. We will be in touch.';form.reset();}
   catch(error){status.classList.add('is-error');status.textContent='We could not confirm delivery. Please try again. Your message is still here.';}
   finally{button.disabled=false;button.textContent=original;form.removeAttribute('aria-busy');status.focus();}
  });
 });
})();
