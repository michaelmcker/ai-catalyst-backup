> Superseded visual release: Michael rejected the compact Home composition and image-first panoramic mobile openings after publication. The responsive image change also exposed a shader sampling bug. Geometry and static-motion assertions below describe that rejected release, not current acceptance criteria. See ../visual-repair-2026-10-23/ for the repair. Original network captures remain historical measurements.

# Mobile portrait heroes and image delivery

The reported phone issue was reproduced on the deployed site: Home used a 72%-wide off-screen image stage, while Company, How We Work and Briefing placed full-width artwork above their copy. The portrait heroes now retain smaller right-hand artwork and left-hand copy on phones. The existing panoramic primitive remains separate.

## Loading findings

The captured cold-cache homepage load transferred 3,354,706 bytes in 28 requests. The HTML response arrived after roughly 76 ms on this desktop connection; its load event occurred after 718 ms. These are browser observations on the test connection, not real-iPhone field metrics or Lighthouse results.

- The original hero transferred 1,734,258 bytes, including response overhead.
- Three lower-page SVG product images transferred 1,486,568 bytes immediately, despite being far outside the initial viewport.
- The homepage explicitly requested a 90% mobile dither pass. The shader also ran continuously while the hero was visible.
- The enhancement hid the source image while its canvas faded in, producing an avoidable temporary loss of contrast.

## Changes

- Original artwork files remain unchanged. cwebp delivery variants use fingerprinted names and responsive srcset/sizes. The 640px Home, Company, How We Work and Briefing variants are 27,682, 23,184, 15,686 and 19,452 bytes respectively. Their 1280px versions are below 130 KB.
- Product thumbnails use 320px variants and an IntersectionObserver rather than eager SVG image hrefs. Optional offscreen shaders and map rasterisation also wait until their sections approach.
- Phones render the print treatment once. Desktop retains a quiet tonal pass, with fixed dot positions. The added close-up print amount is 18%, and Home's mobile amount is 14%.
- Home and side heroes use a 60/40 copy/art composition below 701px. Desktop subpage art is contained in the right 52% of the shared field. Text remains inside the hero, with no copy/image collision or off-screen source stage.
- Responsive source changes re-upload the selected WebGL texture after decoding, preserving the image when an already-loaded page changes breakpoint.
- Removed the enhancement fade, obsolete homepage float-measuring code and a duplicate Briefing enquiry script. Homepage scripts use defer.

## Verification

`check-mobile-hero.py` failed on the captured original geometry and passes on the corrected geometry. `check-image-budget.py` failed before the variants/lazy SVG images were added and now passes. The shared public-site check passes.

`rendered-checks.json` contains all nine pages at 1440, 1024, 768, 390 and 320 pixels: 45 checks, all hero images loaded, no horizontal overflow, exact header joins and flush panoramic image/copy joins. Mobile portrait text and image rectangles do not collide. Pixel-identical mobile captures verify the static finish. The film dialog and expanded Training menu route were exercised successfully, with no browser errors.

Screenshots named `ai-catalyst-before-*` show the deployed baseline. `after-*` screenshots show the local correction. Production measurements are recorded separately after publication.

## Published verification

Code revision `ff882fa428daba3b43d8c2d13a12a8ccf2390915` was published through the official built-in Cloudflare connection to Randy's `ai-catalyst` project. Deployment `6b31159c-b489-4244-a6ac-d02a84c718ec` reports success. Both `aicatalyst.biz` and `www.aicatalyst.biz` remain active.

The same cold-cache, narrow-viewport browser check transferred **150,951 bytes in 25 requests**, down **95.5%** from 3,354,706 bytes. The mobile hero response transferred 28,222 bytes including headers. The observed load event was 253 ms versus 718 ms before, on this desktop network. These measurements describe the test connection rather than real-device Core Web Vitals.

`live-checks.json` verifies all nine custom-domain pages: images loaded, zero horizontal overflow, exact header joins and no retired links. The four portrait geometry checks pass on the published pages. `live-*.png` captures their actual production appearance. `performance-live.json` and `deployment.json` retain the network and Cloudflare evidence. Original source bytes for all 25 optimized masters were checked against the previous release and are unchanged.
