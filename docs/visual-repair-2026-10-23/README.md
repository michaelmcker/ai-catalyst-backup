> Rejected and superseded: the fixed-grain change removed the approved moving dither and image treatment. These checks did not establish equivalence to Vercel. Current restoration evidence is ../approved-restoration-2026-10-23/.

# Hero composition and print repair

Michael rejected the previous mobile release. Its homepage figure and headline were squeezed into a 40/60 split, the four panoramic openings remained image-first on phones, and responsive source images became blurred by the shared shader. The original Vercel composition is useful for scale, but Michael explicitly clarified that its original dithering was also faulty.

## Physical cause and correction

`srcset`/`sizes` makes `naturalWidth` density-corrected. On the deployed narrow Platform page, a physical 640px bitmap reported only 156px because a full-width image was incorrectly marked `40vw`. The shader used that smaller value for its nine-tap smoothing footprint, multiplying the blur. It now takes texel dimensions from the selected source's width descriptor, uses `100vw` for panoramas, and does not smooth already-resampled delivery variants again. Responsive source changes still re-upload the decoded texture.

Home again uses the substantial sword composition with a full-width mobile headline and measured clearance around the final line. The four panoramic pages use headline/support first, then an immediately adjoining full-width image at every breakpoint. Desktop retains headline left/support right. Solutions, Company, Briefing and Training keep the side primitive.

The print finish preserves modeled blue shading. The shared paper uses fixed one-CSS-pixel grains instead of the visibly tiled grid, with a slow change in opacity rather than moving binary thresholds. Home's field sits behind the artwork instead of multiplying another screen over it. Close-up paper reveals that common field; the scenic drift override is removed and additional scenic print strength/depth is reduced. Reduced motion freezes the finish. No original master was regenerated or edited: all 25 optimized sources match revision `9bc79bd` byte for byte.

## Verification

- `rendered-checks.json`: 54 browser captures across all nine pages at 320, 390, 430, 768, 1024 and 1440 pixels. `scripts/check-mobile-hero.py` checks the requested order, substantial Home scale and headline width, full-width delivery hint, physical texture resolution, flush joins, image readiness and overflow.
- `rejected-live-checks.json` and `before-*.png`: captured previous production release. The revised geometry checks fail on its Home composition, all four panoramic orders and source-sizing hints.
- `grain-checks.json`: 18 actual screenshots checked for visible pale print at both top edges. `scripts/check-hero-grain.py` accounts for screenshot scaling. These pixel checks detect blank/dark fields; screenshots remain necessary to judge the finish.
- `resize-checks.json`: an already-loaded Home page was resized from phone to desktop and back. Texture replacement remained ready with the physical selected width; Chrome can retain the larger candidate after shrinking.
- `network-local.json`: cold local browser transport capture, retained as diagnostic data. It is not a production performance benchmark.
- Public contact/navigation checks, JavaScript syntax, responsive image budgets and source/master byte checks passed. No console warnings/errors were observed in the sampled rendered pages.

Screenshots use Chromium viewport emulation, including visible desktop scrollbar behavior. Physical iPhone Safari rendering and field Core Web Vitals have not been measured. Publication and custom-domain verification are recorded separately after deployment.

## Published verification

Code revision `2aac3c894c1f0cd8583ec5d93d2ca3f27db7c4fe` was pushed to GitHub and published through the official built-in Cloudflare connection. Production deployment `70a17f9d-4f2a-4cbd-a651-412e8099cc42` reports success and is the project's canonical deployment. `aicatalyst.biz` and `www.aicatalyst.biz` both serve the new repair4 shader.

`live-checks.json` passes the same nine-page mobile geometry and physical texture checks on the custom domain. `live-desktop-checks.json` checks Home and the four panoramas at desktop width. `live-*.png` captures the published phone compositions. No sampled console warning/error was observed.

The cold-cache narrow-viewport capture transferred **169,795 bytes across 27 responses**, including the 28,223-byte hero response and Cloudflare's existing beacon. This is approximately 95% below the earlier 3,354,706-byte baseline. It is a measurement on this desktop browser/network, not an iPhone field performance or Core Web Vitals result. The source image masters remain unchanged.
