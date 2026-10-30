import fs from 'node:fs/promises';
import path from 'node:path';
import { transform } from 'esbuild';
async function walk(dir){for(const e of await fs.readdir(dir,{withFileTypes:true})){const p=path.join(dir,e.name);if(e.isDirectory())await walk(p);else if(p.endsWith('.mjs')){const result=await transform(await fs.readFile(p,'utf8'),{minify:true,format:'esm',target:'es2022',legalComments:'none'});await fs.writeFile(p,result.code);}}}
await walk('dist/server');
const config=JSON.parse(await fs.readFile('dist/server/wrangler.json','utf8'));config.upload_source_maps=false;await fs.writeFile('dist/server/wrangler.json',JSON.stringify(config));
console.log('Minified server modules for the Worker upload; exports and module paths preserved.');
