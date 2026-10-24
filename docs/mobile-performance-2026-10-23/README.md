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
