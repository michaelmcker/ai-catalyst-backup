# AI Catalyst website and backup

## Current production — 23 October 2026

The editable production site is `current-site/`, served from Randy's Cloudflare Pages project `ai-catalyst` at https://aicatalyst.biz/ and https://www.aicatalyst.biz/. The Pages address https://ai-catalyst-9l3.pages.dev/ also remains available. Matching root public files are kept in sync.

Public contact: `randy@aicatalyst.biz`, `416-270-0132`, Toronto, Canada. Randy confirmed the mailbox already works. Email links open the visitor's mail application. The existing enquiry forms remain hidden unless a delivery endpoint is configured.

Validate source with `python3 scripts/check-public-site.py`. Rendered hero/pattern evidence is in `docs/hero-correction-2026-10-23/`. Deployment uploads only `current-site/`, excluding instructions, review material, historical exports and evidence.

The latest visual repair restores the substantial right-hand Home figure and full-width mobile headline. Company, How We Work, Briefing and Training retain text left/image right. All four panoramic pages place their headline section first and the full-width image directly below at every breakpoint; desktop puts headline left and support right.

The original Vercel composition informs scale, but its dithering was also flawed. The revised finish retains modeled image shading, with a restrained fixed-grain screen and a continuous field behind copy and artwork. It removes the extra Home multiply layer, heavy scenic drift and shader blur of already-resampled images. Texture sampling uses the selected srcset width, because naturalWidth is density-corrected and can be much smaller than the uploaded bitmap.

Rebuild delivery images with `python3 scripts/build-image-variants.py` (requires cwebp), then mirror changed public files to the root. Run `python3 scripts/check-image-budget.py` and `python3 scripts/check-mobile-hero.py docs/visual-repair-2026-10-23/rendered-checks.json`. Current screenshots and checks are in `docs/visual-repair-2026-10-23/`. The previous mobile-performance folder records the rejected release, including its incorrect compact Home and image-first panorama assumptions.

## Original backup — 22 October 2026

This repository includes the approved nine-page website transferred to Randy's Lovable workspace on 21 October, plus its Lovable build source. This is a manual backup; automatic GitHub syncing with Lovable has not been configured.

### Restore the original snapshot

- At the October 22 backup commit (`68dbb96`), `current-site/` is the exact, self-contained 83-file production snapshot: nine HTML pages, CSS/JavaScript, original artwork, portraits, logos, map asset and brand film. The current branch contains the later production changes described above. Serve its current folder with a static HTTP server, for example `python3 -m http.server 8080 --directory current-site`.
- The matching current site files are also updated at the repository root for continuity. Older root assets and review evidence remain preserved; use `current-site/` for a clean deployment.
- `lovable-source/` preserves original documents in `site/`, assets in `public/`, the serving adapter, routes, package metadata, lockfile, tests and project configuration from Lovable commit `015d6112e4812db99bdafb95eae5ea9dcfbce225`. Restore this folder as the project root for the TanStack Start version. Install dependencies with Bun, then use the scripts in its `package.json`.
- `backup-records/2026-10-22/` contains the original production manifest, migration verification and per-file SHA-256/Git-blob fingerprints for the Lovable export.

Lovable project: https://lovable.dev/projects/221b4eb9-dd01-4746-a063-72785aa6497f

Original production website: https://ai-catalyst-wheat.vercel.app/

At the October 22 backup commit, all 83 approved website files were verified byte for byte against the production manifest and migration ZIP. The additional Lovable source export contains 170 files. Its only omitted project file is the unused default `public/favicon.ico`: the connector exposes binary icons through a lossy text response, so that icon cannot be preserved faithfully through this export. The approved website uses `assets/logo.svg` and is fully backed up.

That original backup excludes installed dependencies, local credentials and provider-side account settings. The current Cloudflare deployment and direct contact routes are described above; automatic Lovable synchronization remains unconfigured.

## Historical material

The October 4 commit and earlier artwork decisions/review material remain in Git history and the existing review folders. Exact artwork eligibility decisions in `review/artwork-decisions-20261003.json` remain applicable, subject to later approved site changes already reflected in this snapshot.

Earlier complete source/review/history preservation: https://drive.google.com/drive/folders/1kZipQ0Iq8yF7MyXBJzEmOUrHBPV-4BIX
