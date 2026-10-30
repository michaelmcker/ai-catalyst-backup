import {defineMiddleware} from 'astro:middleware';
// Preview shared assets from this project's existing static-site server.
// Production requests for these paths go directly to Cloudflare Pages.
export const onRequest=defineMiddleware(async ({url},next)=>{
 if(import.meta.env.DEV&&!url.pathname.startsWith('/_')&&(/\.(css|js)$/.test(url.pathname)||url.pathname.startsWith('/assets/')||url.pathname.startsWith('/images/'))){return fetch('http://127.0.0.1:3043'+url.pathname+url.search);}
 return next();
});
