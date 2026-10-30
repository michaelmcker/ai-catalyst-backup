# Static case studies and smaller footer

Michael requested a simple case-study dashboard with clickable studies and videos, without a true CMS, plus a smaller footer logo/bridge and a slightly stronger dither finish.

The public index and Analucia/Sofia detail page are static HTML under current-site/case-studies/, mirrored at the repository root. The homepage keeps only its View case studies link. Local content/case-studies.json is the input; scripts/build-case-studies.py creates the index, detail pages and sitemap without a server, database, account or browser editor. Add approved studies to that file and rebuild. Existing Analucia copy, poster and YouTube film are retained; no additional client results are invented.

The old CMS source is removed from the active tree and preserved in Git history. Its local ignored state and Cloudflare D1/KV data are retained for rollback rather than purged. After the static deployment, the three CMS Worker routes and its minute schedule are disconnected; its unused owner invitation is expired. Legacy /_emdash paths redirect to /case-studies/.

A final, footer-only stylesheet applies to all eleven pages: 160px desktop and 140px phone logos, a contained bridge stage capped at 880px wide and 240px high (140px high on phones), and a smaller accompanying signature. The existing renderer’s supported data-art-print override increases only the footer from .20 to .34. The original bridge image, source masters, shared shaders and other profiles are unchanged.

Validation: static-output parity and public-site checks pass across all eleven pages; strict original-source preservation and negative controls pass; loader and deferred-renderer checks pass. Browser review confirms the clickable study, actual inline Sofia playback, 160/140px footer logos, 880px desktop bridge stage, 140px phone art height, and no horizontal overflow. Separate Safari review was attempted but interrupted by app activity and a browser-control timeout, so Safari/physical iPhone behavior is not claimed. The enclosing portfolio npm suite has the same unrelated resources.test.mjs article failure before and after: 170 of 171 pass.

The release has 116 public assets, with fourteen changed/new and 102 prior hashes retained. Headers are preserved; a legacy-CMS redirect file is added. No CMS runtime or admin assets are included in the Pages manifest.
