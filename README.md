# AI Catalyst private website backup — 2026-10-22

This repository includes the approved nine-page website transferred to Randy's Lovable workspace on 21 October, plus its Lovable build source. This is a manual backup; automatic GitHub syncing with Lovable has not been configured.

## Restore the current website

- `current-site/` is the exact, self-contained 83-file production snapshot: nine HTML pages, CSS/JavaScript, original artwork, portraits, logos, map asset and brand film. Serve this folder with a static HTTP server, for example `python3 -m http.server 8080 --directory current-site`.
- The matching current site files are also updated at the repository root for continuity. Older root assets and review evidence remain preserved; use `current-site/` for a clean deployment.
- `lovable-source/` preserves original documents in `site/`, assets in `public/`, the serving adapter, routes, package metadata, lockfile, tests and project configuration from Lovable commit `015d6112e4812db99bdafb95eae5ea9dcfbce225`. Restore this folder as the project root for the TanStack Start version. Install dependencies with Bun, then use the scripts in its `package.json`.
- `backup-records/2026-10-22/` contains the original production manifest, migration verification and per-file SHA-256/Git-blob fingerprints for the Lovable export.

Lovable project: https://lovable.dev/projects/221b4eb9-dd01-4746-a063-72785aa6497f

Original production website: https://ai-catalyst-wheat.vercel.app/

All 83 approved website files were verified byte for byte against the production manifest and migration ZIP. The original HTML, CSS and JavaScript are unchanged. The additional Lovable source export contains 170 files. Its only omitted project file is the unused default `public/favicon.ico`: the connector exposes binary icons through a lossy text response, so that icon cannot be preserved faithfully through this export. The approved website uses `assets/logo.svg` and is fully backed up.

This backup does not change hosting, DNS, repository privacy, or automatic synchronization. It excludes installed dependencies, local credentials and provider-side account settings. The contact email and enquiry delivery remain pending; existing contact routes are preserved.

## Historical material

The October 4 commit and earlier artwork decisions/review material remain in Git history and the existing review folders. Exact artwork eligibility decisions in `review/artwork-decisions-20261003.json` remain applicable, subject to later approved site changes already reflected in this snapshot.

Earlier complete source/review/history preservation: https://drive.google.com/drive/folders/1kZipQ0Iq8yF7MyXBJzEmOUrHBPV-4BIX
