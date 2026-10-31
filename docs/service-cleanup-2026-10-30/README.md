# Service-page and footer cleanup — 30 October 2026

Status: live at https://aicatalyst.biz/ on production deployment `50b8b6c7-a1da-4589-b5bd-2d84ac614497`. Code commit: `ede8c7ee498dc761877e37c82741c98e0f982e09`. Browser control was not used.

The three service pages (Creator Intelligence, Full Commerce MMM, Agentic Live Selling) now have a hero-only art-opening wrapper. The moving paper field previously inherited the full opening wrapper, including film and supporting sections. The renderer and shader source remain unchanged.

Question lists retain their exact copy and become homepage-style white cards beside their section heading. The three benefit explanations become a compact card grid. Service films have their headline and supporting copy above the player and a maximum player width of 880px. MMM retains its allocation canvas and animation, now alongside channel coverage instead of a separate empty-copy stage. Supporting sections have more consistent spacing and a single-column phone layout.

The bridge footer returns to its original full-width stage, with the image anchored left and its original .20 print profile. The smaller approved logo remains. The bridge source asset is unchanged.

MMM previews use the updated film's 104-second planning scene. Live-selling previews use the 92-second “Ask. Answer. Shop.” scene. Both use .08 print and .35 softness. The Command Centre keeps its inline films. Homepage graphics and View video actions remain intact.

## Checks

- `python3 scripts/check-public-site.py` — pass, all 11 public pages and local references.
- `python3 scripts/check-service-cleanup.py` — pass: content, hero field boundary, cards, retained MMM canvas, film cap, footer, mirrors and unchanged motion scripts.
- `python3 scripts/check-direct-vercel.py` and `--self-test` — pass: approved-source preservation and mutation checks.
- `python3 scripts/build-case-studies.py --check` — pass.
- Image-loading and deferred-renderer checks — pass.
- Enclosing portfolio `npm test`, before and after — 168/170 pass both times. Same pre-existing failures: resources article parity and `tests/v2-about-mobile.test.mjs`. This nested static site has no npm test script.
- Rendered viewport/visual proof has not been performed because browser control is prohibited.

## Published release

Cloudflare MCP confirms production deployment `50b8b6c7-a1da-4589-b5bd-2d84ac614497` succeeded and is canonical for aicatalyst.biz and www.aicatalyst.biz. It supersedes `620f198f-ff3d-4d98-a8bd-f642ddea8073` and includes the previously pending naming and thumbnail changes.

The 127-path manifest contains 126 unique asset hashes. Eighteen hashes needed uploading (the remote asset store's missing check also included two older assets); all hashes were confirmed present before publication. MCP created the complete deployment with the retained headers and redirects.

`live-verification.json` records successful HTTP checks of all eleven public pages and exact byte comparisons for twelve assets, including CSS, posters, bridge, logo and motion scripts. This is source/delivery proof, not rendered viewport approval.

The hosted MCP's automatic Authorization injection remains an upstream limitation. A secure, encrypted handoff of only the short-lived project upload token resolved the deployment path without browser use or exposing plaintext credentials. See [authentication.md](authentication.md) and `asset-upload-result.json`. Temporary key/token files were removed.
