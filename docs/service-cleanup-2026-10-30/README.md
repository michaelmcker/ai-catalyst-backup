# Service-page and footer cleanup — 30 October 2026

Status: prepared locally for publication; not live. Browser control was not used.

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

## Release boundary

Signed-in Cloudflare MCP confirms canonical deployment `620f198f-ff3d-4d98-a8bd-f642ddea8073` succeeded and this is a direct-upload Pages project. That release contains the restored homepage graphics. It does not contain this cleanup or the previously prepared naming and preview revision.

`manifest.json` contains 127 public assets, recomputed from current local bytes. `asset-diff.json` identifies 16 new or changed assets against the last published manifest and 111 reusable assets. Headers/redirects must accompany the complete manifest at publication. Instructions, proof images and release records are excluded.

Publication remains blocked by the connector: it forces its connection Authorization onto all requests, conflicting with the separate Pages asset-upload JWT. Automatic approval review rejected exporting that JWT into tool arguments. No new deployment was created with missing asset hashes, no credential workaround was attempted, and no browser upload was used.
