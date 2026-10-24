# Hero paper and responsive repair

## Why copying Vercel still showed a box

The direct Vercel transfer preserved the original renderer, including problems
in its paper compositing. The artwork masters are opaque RGB WebP images with
pale blue paper baked into their pixels. They are not transparent cutouts.
The renderer generated a background field and generated paper again inside the
image shader, while retaining some source-paper color. Its final feather also
mixed a smooth edge with a binary Bayer alpha contour. Those paths could expose
the image boundary even when the source files matched Vercel exactly.

This is reproducible independently of Safari. The isolated constant/grained
paper fixtures in `proof/` compare tinted source paper with a transparent
control at the same position and frozen phase. At DPR 1, 2 and 3 the original
renderer exceeds the two-level RGB tolerance; the largest observed difference
is 55. The candidate's maximum difference is 0 across all 24 candidate ROI
comparisons. The 36 screenshot inputs and full results are retained in
`proof/captures/` and `proof/pixel-results.json`. This proves parity for those
paper colors and geometries; it does not establish every real illustration or
physical iOS rendering is correct.

The old renderer also requested `premultipliedAlpha:false`, a path for which
WebKit has a documented incorrect-compositing defect. A fix landed in WebKit
main on 2026-09-08; that does not establish it is present in a particular iOS
release. We have not identified Michael's installed Safari as exhibiting that
specific defect. See [the WebKit issue](https://bugs.webkit.org/show_bug.cgi?id=200026)
and [its fix](https://github.com/WebKit/WebKit/pull/73156).

## What the candidate changes

One full-width, opaque WebGL surface now evaluates the common paper and artwork
in the same fragment pass. Clean pale source paper resolves to that common
field. A smooth stage boundary replaces the binary rectangular alpha contour;
the original source-space feather is retained. There is no cross-canvas CSS
multiply operation in the hero. The surface uses an opaque framebuffer, so
partially transparent hero pixels no longer go through the browser's page
compositor. Other transparent artwork outputs use valid premultiplied RGB and
alpha together.

The hero backing store follows native device DPR up to 3, subject to the 4096px
axis limit, instead of capping a DPR 3 phone at 2 and resampling that intermediate
surface. The authored print remains measured in CSS pixels. The original
artwork masters, image profile strengths, ordered-screen functions, weather,
thresholds and artwork motion calculation are preserved and covered by the
source allowlist check.

The original nonwhite subpage `paperTone` function ignored the pointer. A
deliberate, documented extension applies the existing V1 pointer Gaussian to
that paper's ordered dot density. Its resting density, weather and ink strength
remain the original values. This is an authorized behavior correction, not a
claim that Vercel's original Company background already responded to the mouse.
The frozen-clock reference Company capture changes zero paper pixels after
pointer movement; every candidate page changes paper pixels after movement.
Reduced motion keeps the Company paper unchanged after virtual frames and
pointer movement.

## Responsive composition

The phone portrait openings put the headline at the upper left of the complete
hero composition, 28px below its top, on the existing 24px gutter (20px at 320px).
The subject is positioned independently of that live headline. Supporting copy
uses the quieter part of the composition. Training and Briefing use a float
exclusion shaped around the image on phones at widths up to 700px, allowing the
copy to wrap instead of forcing it into a narrow paragraph column. Their image
stages are capped at 560px and anchored at the right on wider phones. Briefing's
remaining copy flows below the lower horizon of its fixed image stage.

Tablet widths 701–1199 retain copy left and artwork right, including the
1024px and 1180px cases. At 1200px and above, desktop subpage artwork retains the
approved full-stage composition; a full-width artwork rectangle is intentional
there and is not treated as a failed split by the geometry check.

The four panoramic pages retain headline left, supporting paragraph right and
the image immediately below at every width. The image is flush with the text
row and spans the hero width. Randy's email/phone/Toronto contact changes,
LinkedIn removals and expanded-menu Training entry remain part of the source
allowlist; this repair does not revert those approved changes.

## Evidence and checks

`responsive/geometry-{320,390,430,600,768,1024,1180,1440}.json` records 50 hero
layouts: all nine pages at 320, 390, 768 and 1440, the five portrait pages at
1024 and 1180, and Training/Briefing at 430 and 600. The check
requires no document overflow above 1px, one ready opaque surface, full-width
paper, native 3x phone backing pixels, phone headline positioning, tablet splits
and the panoramic arrangement. Geometry is not a proof that a subject never
intersects a glyph; review the retained screenshots as well.

`pointer/` contains separate stationary and pointer captures at a frozen 7s
clock. All nine candidate stationary controls are pixel-identical. Each
candidate paper ROI changes after pointer movement; original Company and the
reduced-motion Company controls do not. `pointer/pixel-results.json` records
exact coordinates and counts. The harness description is in
`pointer/README.md`.

Native macOS Safari responsive-mode captures are retained under `proof/safari/`:
Company at 393px and 768px, Home at 393px and Training at 390px, using 3x
backing. Any further captures in that folder have the same desktop-only device
limit. These are WebKit desktop evidence. They are not captures from an iPhone,
not an iOS simulator, and not a substitute for Michael's offered iPhone Safari
check.

Run:

```sh
python3 scripts/check-paper-proof.py docs/safari-paper-2026-10-23/proof/captures --require-original-failure --output docs/safari-paper-2026-10-23/proof/pixel-results.json
python3 scripts/check-safari-hero-proof.py
python3 scripts/check-direct-vercel.py
python3 scripts/check-public-site.py
```

The first two commands verify captured behavior; the latter two verify the
approved source/content allowlist and public contact/navigation contract.
Successful local checks do not mean the candidate has been published. During
these captures production remained unchanged. A new preview is the next
checkpoint for actual iPhone Safari feedback before production promotion.


## Published preview

Built-in Cloudflare connection created preview deployment `3b7f62f1-a17d-4894-b3ee-b0a8b3777103` from code commit `9c2a817ad9642afe4880a75381a8b1552f118997`:
https://3b7f62f1.ai-catalyst-9l3.pages.dev/

The 85-file public manifest uses cache key `20261023-direct8`. All nine live
phone pages draw one ready opaque surface with no document overflow. Browser
resource exports confirm all nine HTML documents plus the renderer and two
added stylesheets match the committed files byte for byte. The live Briefing
1024px check keeps both text blocks left of the image. See `preview/` and
`deployment.json`. Public HTTP requests from Python returned403; source-byte
verification instead uses resources loaded by the normal preview browser.

Production deployment remains `f87c264b-eafd-441a-ade0-d4a03d7f02e4`. This preview
has not been promoted. Physical iPhone Safari appearance remains pending
Michael's review of this new preview.
