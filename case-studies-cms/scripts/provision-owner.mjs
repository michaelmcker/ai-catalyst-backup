// Initial provisioning of a new, empty CMS. Uses EmDash's native invite flow.
// The disabled bootstrap record has no credentials and cannot sign in.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {createKyselyAdapter} from '@emdash-cms/auth/adapters/kysely';
import {createInviteToken} from '@emdash-cms/auth';
const email=process.argv[2];
if(!email||!email.includes('@'))throw Error('Provide the CMS owner email');
const packageDir=path.dirname(import.meta.resolve('emdash').replace('file://',''));
const connectionFile=(await fs.readdir(packageDir)).find(x=>/^connection-.*\.mjs$/.test(x));
if(!connectionFile)throw Error('Installed database adapter not found');
const {t:createDatabase}=await import(pathToFileURL(path.join(packageDir,connectionFile)));
const db=createDatabase({url:'file:'+path.resolve('data.db')});
const adapter=createKyselyAdapter(db);
if(await adapter.countUsers())throw Error('Initial provisioning only: database already has users');
const bootstrap=await adapter.createUser({email:'bootstrap@aicatalyst.invalid',name:'Disabled provisioning record',role:10,emailVerified:false});
await db.updateTable('users').set({disabled:1}).where('id','=',bootstrap.id).execute();
for(const [name,value] of Object.entries({'emdash:setup_complete':true,'emdash:site_url':'https://aicatalyst.biz','emdash:site_title':'AI Catalyst'}))await db.insertInto('options').values({name,value:JSON.stringify(value)}).onConflict(o=>o.column('name').doUpdateSet({value:JSON.stringify(value)})).execute();
const invite=await createInviteToken({baseUrl:'https://aicatalyst.biz/_emdash'},adapter,email,50,bootstrap.id);
await fs.mkdir('.emdash',{recursive:true});await fs.writeFile('.emdash/owner-invite.json',JSON.stringify(invite),{mode:0o600});
await db.destroy();console.log('CMS provisioned; private owner invitation saved locally. No email sent.');
