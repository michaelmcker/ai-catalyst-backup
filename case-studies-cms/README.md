# AI Catalyst case studies CMS

The public collection lives at https://aicatalyst.biz/case-studies/ and each published study has its own route, starting with `/case-studies/analucia-sofia/`. The homepage contains only a View case studies link. Navigation and footer links point to the collection.

Scaffolded with the official `create-emdash@1.4.0` Starter / Cloudflare template. EmDash's native editor, draft/publish workflow, revisions, preview and scheduled publishing manage a `case_studies` collection. Eight editable fields cover title, client, summary, image URL, image description, YouTube URL, duration and rich-text case study. Public queries read published entries, and drafts are not reachable through public detail URLs.

## Runtime

- Node 24.15+ for development/builds. `npm ci`, `npm run typecheck`, `npm run build`.
- Cloudflare Worker `ai-catalyst-case-studies`, in the existing Randy account.
- D1 stores schema/content. KV stores native Astro sessions.
- Only `/case-studies*`, `/_emdash/*` and `/_astro/*` go to this Worker. Existing pages, artwork, scripts and styles remain on the existing Cloudflare Pages deployment.
- Public templates reuse the site's shared navigation/footer and assets. No whole-site migration or custom admin was introduced.
- Media uses existing public image URLs and YouTube links. Uploading binary media is not configured; R2 is not enabled on this account and was not activated.
- The native minute scheduler is wired to the Worker. English-only admin catalogs and server-module minification keep the upload below the Workers free script-size limit.

## Editing and owner onboarding

The editor is `https://aicatalyst.biz/_emdash/admin`. A private, seven-day native EmDash invitation for the owner is stored in the gitignored `.emdash/owner-invite.json`; never commit it, the database, `.env`, or deployment payloads. The owner must complete their own passkey registration. No email was sent.

Initial provisioning uses a disabled, credential-free bootstrap record with Subscriber permissions to close the anonymous first-admin setup flow. It cannot log in. The owner's invitation grants Admin through EmDash's normal invitation/passkey flow. No development user, development session, or bypass credential was deployed. Setup is marked complete and the production dev-bypass endpoint returns 403.

The encryption key is in Cloudflare's secret binding and the gitignored local `.env`. Preserve it for future deployments. `scripts/provision-owner.mjs` and `scripts/export-initial-d1.py` are **first-install tools for a new empty database**, not deploy hooks. Never re-import the bootstrap database over owner-edited production content. Deploying code subsequently retains the existing D1 database.

## Preview

The built Worker can be previewed with `wrangler dev --config dist/server/wrangler.json --persist-to "$PWD/.wrangler/cms-preview" --ip 127.0.0.1 --port 3044`. Use a fixed persistence path; placing local data under `dist/` loses it on rebuild. Shared assets come from the existing static site's local server during `astro dev` through a development-only middleware branch. Production shared-asset requests continue to Pages.

First-install proof and the release manifest live in `../docs/case-study-collection-2026-10-29/`. Public copy is the existing source-backed Analucia/Sofia concierge material; it claims no unverified conversion results or one-to-many live-selling show.
