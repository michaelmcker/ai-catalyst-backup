# Command Centre media release

Restored the retained Agentic Live Selling SVG, Creator Economy Intelligence canvas and Full Commerce MMM canvas on the platform page. The overview film now accompanies the introduction: copy left/film right on desktop, film first below 1000px, and logical reversed columns for Arabic without mirroring media.

The film is `NkQtLriHVbA`, confirmed from the sent email to Randy and independently through YouTube metadata as **Agentic Commerce Command Centre**. YouTube reports `status: OK` and `playableInEmbed: true`. The poster is its official 1280×720 thumbnail, locally compressed to about 85 KB. It follows the existing blue poster treatment and starts the player only after activation.

All four editions were regenerated and model-reviewed; this is not native-speaker certification. Existing page copy, dedicated service films, homepage graphics/video actions, telemetry and HopShop remain intact.

Rendered checks passed 40 cases: four languages × five widths (1440, 1024, 768, 390, 320) × normal/reduced motion. They verify painted canvas content, visible SVG, column/stack order, heading size, no horizontal overflow, no iframe before activation and keyboard activation of the correct film. Evidence is in `aic-command-results.json` and the four desktop/phone screenshots. External requests were blocked during these local layout checks; YouTube playback availability was checked separately through its player metadata.

Testing identified and fixed two issues: an older ID selector overrode the new heading size, and ResizeObserver cleared reduced-motion canvas bitmaps after their initial static paint. The scoped heading selector and static redraw preserve the intended layout and diagram content.

Passing checks:

- `python3 tests/localization/command-centre-media.py`
- `node tests/localization/command-centre-media.cjs` with the temporary Playwright module/browser paths supplied through `PLAYWRIGHT_MODULE` and `PLAYWRIGHT_CHROMIUM_EXECUTABLE`
- `python3 tests/localization/check.py`
- `python3 scripts/build-localized-site.py --check`
- `python3 tests/localization/discovery.py`
- `python3 scripts/check-public-site.py`
- `python3 scripts/build-case-studies.py --check`
- `python3 scripts/build-blog.py --check`
- `node tests/localization/blog.cjs`
- `node --check restored-platform-motion.js` and `git diff --check`

Known unrelated failures: enclosing portfolio `npm test` remains 168/170 before and after (article completeness and `v2-about-mobile`); historical `check-service-cleanup.py` compares the renderer against October 30 and fails on `halftone-rendering.js`, whose bytes are unchanged from HEAD in this release. No test assertions were weakened to hide these failures.

Public release uses the complete previous 206-path manifest plus the one new poster (207 paths). Only the four platform editions, shared platform CSS, reduced-motion renderer and poster change in the deployed manifest. `_headers` and `_redirects` are retained as separate named deployment parts.

Production deployment `1b8c2af0-669c-494f-9578-bb52c560d4ba` succeeded and was confirmed canonical through Cloudflare. Live readback verified all 60 HTML editions plus seven shared assets/discovery files against release source, normalizing only the existing Cloudflare email-protection markup in HTML. See `deployment.json` and `live-verification.json`. Implementation is backed up on the existing `codex/multilingual-site-20261113` GitHub branch.
