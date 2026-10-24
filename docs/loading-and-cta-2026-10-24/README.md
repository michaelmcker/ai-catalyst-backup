# Hero actions, copy and image loading

The requested changes are a shared row for How We Work's two actions, vector
up-right arrows, larger Company/Training phone headlines, a shorter complete
Start a Conversation subhead, and faster image loading.

## Implementation

- How We Work's link and film button share one row at320–1440px; selectors,
  accessible labels and its single existing film dialog remain intact.
- All31 literal up-right glyphs in public HTML now use the existing aria-hidden
  SVG icon. There are no font/emoji arrow substitutions.
- Company and Training have larger mobile titles with more reading width.
  Briefing joins the existing row composition so its entire shortened paragraph
  sits below the artwork. No paragraph is split around an image.
- The17 reviewed full-size VP8L delivery files save7,774,110 bytes compared with
  their masters, or23.39% across replaced files. All39 original images remain
  unchanged. Dimensions and alpha are exact; decoded RGB channels can differ
  by at most2 levels. This is near-lossless encoding, not identical pixels.
  The derivation, hashes, pixel gates and URL map are in
  ../image-delivery-2026-10-24/manifest.json.
- Every page preloads its exact hero at high priority. Thirty explicit body,
  advisor and footer images wait for the hero, scrolling or a4s stall guard,
  then load within300px of the viewport. Complete noscript image fallbacks
  retain the content when scripting is disabled. Tiny header/client logos stay
  immediate. Hash-named delivery assets use immutable caching.
- Body artwork and the map defer shader setup until within300px. The hero
  remains immediate. All shader strings, dither strengths, original source
  dimensions, colours and pointer/weather calculations remain unchanged by
  this scheduling repair. The new script introduces no1px image placeholder.

## Evidence and limits

`rows.json` and `row-results.json` contain16 phone captures: four pages at
320/390/430/600px, DPR3. They pass complete approved text, unclipped character
bounds, a contiguous full-width paragraph below the image, and10px clearance
from independent original-source protected ink. Company/Training keep their
requested larger type. Briefing's main architecture is checked separately from
its intentionally quiet paper area. Actions are measured side by side at all
four phone widths and768/1024/1440px (`wide-actions.json`).

`all-pages.json` checks all nine heroes at390px: ready artwork, no horizontal
overflow, and held/deferred below-fold images. `native-safari/` contains eight
page-only screenshots of actual macOS Safari Responsive Design Mode at320 and
390px. Those are visual WebKit evidence, not physical iPhone verification or
native per-character mask measurements.

The controlled local loading probe uses the same390px iframe, cache disabled,
80ms emulated latency and250,000 download bytes/sec. First rendered Company
artwork measured12,006ms before,9,253ms after compression alone and5,441ms after
hero-first fetching. Its hero payload fell from1,336,716 to1,015,040 bytes.
This is one controlled before/after example, not field LCP, a distribution of
measurements, a guarantee of connection speed or an iPhone timing. Raw resource
records and the red-capable paired check are retained in loading-*.json.
The baseline used as its own candidate is rejected by the loading check.

`compression/` compares five original/derivative hero pairs under frozen
reduced-motion rendering at390px/DPR3. All artwork rectangles match. Mean
whole-frame absolute RGB error is0.20–0.44 channel levels;0.075–0.265% of pixels
have a channel difference over16. A few binary dither dots can flip even when
source channels differ by only2; the report records this rather than claiming
identical rendering. Native Safari review retains the approved fine print and
continuous field.

`noscript-fallback.json/png` records a page parsed with script execution disabled:
all nine Company fallbacks have actual decoded images and pending placeholders
are hidden. Execution was restored only to inspect the parsed DOM; the compositor
had not started. Hero-first loader unit tests exercise load/error/cached/scroll/
4s/no-IO paths, once-only loading and listener cleanup. The renderer test runs
the actual source and rejects eager offscreen setup.

## Commands

Run from the repository root:

```
python3 scripts/check-public-site.py
python3 scripts/check-direct-vercel.py --self-test
python3 scripts/check-direct-vercel.py
python3 scripts/build-image-delivery.py --check
python3 scripts/check-mobile-hero-row.py docs/loading-and-cta-2026-10-24/rows.json --output docs/loading-and-cta-2026-10-24/row-results.json
node scripts/check-image-loading.cjs --self-test
node scripts/check-deferred-renderer.cjs current-site/halftone-rendering.js
python3 scripts/check-loading-proof.py docs/loading-and-cta-2026-10-24/loading-baseline.json docs/loading-and-cta-2026-10-24/loading-final.json
```

The static snapshot has no npm test script. Review fixtures, original caches,
instructions, source manifests and screenshots stay outside the public104-file
manifest. Publish a preview through Randy's built-in Cloudflare connection;
production remains unchanged pending Michael's iPhone review. Deployment receipt
and final public-response checks are added after publication.
