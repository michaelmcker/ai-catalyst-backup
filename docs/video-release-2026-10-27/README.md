# Service-page films — October 27, 2026

Adds one 16:9 video section directly after each complete service-page hero:

- Full Commerce MMM: existing `Tu0k3DwfSoU` upload.
- Training and adoption: revised `aMTtgMEdvO4` upload.
- Agentic consumer intelligence: revised Agentic Selling `MzZwU48xdvE` upload.

The posters retain clear detail, blue toning and a faint 16% print pass. A central play control and small duration identify the film without an extra promotional label. Playback loads a privacy-enhanced YouTube iframe only after activation; the original YouTube link remains a functional fallback without JavaScript. Existing hero artwork, narration, page copy and other service content remain unchanged.

Shared implementation: `service-films.css`, `service-films.js`, and three local poster images. Public sources live in `current-site/` with root mirrors. `scripts/service-films-markup.json` records the exact authorized additions for the existing source-preservation checker.

Release manifest: 109 assets, including 8 changed/new assets and 101 preserved assets from production `1c1a2107-18ae-4ba9-9105-f943b5354ea2`. `_headers` is unchanged. Media masters, instructions, proof fixtures and local backup files are excluded from deployment.

Validation: 171 repository tests passed before and after changes; public-site/link/JavaScript checks, strict original-source preservation with the explicit film additions, compositor/scheduler negative controls, image-loader behavior and deferred-renderer checks passed. Desktop 1280px and phone 390px checks confirm 16:9 players, no horizontal overflow and correct video IDs. MMM embed playback was observed advancing. Training and Agentic Selling upload processing and copyright checks completed without issues.

The older standalone image-delivery builder still expects the original logo master and rejects the previously approved filled-logo substitution. The strict source verifier independently checks the approved filled logo and all 17 delivered image derivatives, including dimensions, alpha and RGB error. No logo or existing image derivative is changed in this release.

See `deployment.json` for the final Cloudflare deployment and GitHub commit. Physical iPhone playback remains outside the browser checks.
