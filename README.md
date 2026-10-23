# AI Catalyst website and backup

## Current production — 23 October 2026

The editable production site is `current-site/`, served from Randy's Cloudflare Pages project at https://ai-catalyst-9l3.pages.dev/. The 84-file site includes the corrected portrait/scenic hero layouts, continuous hero pattern, direct email and phone contact, and Training and adoption in all nine expanded menus. Matching root public files are kept in sync.

Public contact: `randy@aicatalyst.biz`, `416-270-0132`, Toronto, Canada. Email links open the visitor's mail application; mailbox delivery and Google Workspace readiness require separate verification. The existing enquiry forms remain hidden unless a delivery endpoint is configured.

Validate source with `python3 scripts/check-public-site.py`. Rendered hero/pattern evidence is in `docs/hero-correction-2026-10-23/`. Deployment uploads only `current-site/`, excluding instructions, review material, historical exports and evidence.

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
