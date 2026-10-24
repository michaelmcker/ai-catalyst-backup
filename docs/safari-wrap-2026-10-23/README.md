# Mobile subject wrapping proof

This is the regression contract for Company, How We Work/Solutions and Training.
It is outside the deployment manifest. The accepted Briefing page is a control:
its HTML must remain byte-identical to revision `9763a3a`, and this repair must
not import the new wrap CSS or JavaScript there.

## Structure and authorized scope

Only the three affected pages add an empty
`<span class="hero-mobile-subject-space" aria-hidden="true" hidden></span>`
immediately after the first hero `h1`. The original float before the heading is
retained for the approved desktop layout. The new float is enabled only at
700px and below; a later float cannot shorten the preceding heading's lines.
Supporting paragraphs have the full reading width, while the source subject's
projected exclusion shapes individual lines. Artwork dimensions follow the
source aspect ratio and its origin is independent of paragraph height.

The projected polygon uses the float's `getBoundingClientRect()` border box.
CSS therefore needs an explicit `border-box` after the shape value:
`shape-outside: var(--mobile-wrap-shape) border-box`. A basic shape otherwise
uses the float's margin box. With the existing 26px top margin and negative
right margin, that default silently changes the polygon's origin and size from
the geometry measured by JavaScript. The margin still positions the float; it
must not also become an implicit offset inside the image/exclusion coordinate
mapping. Record the computed shape value in the capture where available.

`mobile-subject-wrap.css?v=20261023-wrap1` follows the existing responsive CSS
link, and `mobile-subject-wrap.js?v=20261023-wrap1` precedes the renderer script.
Only Company, Solutions and Training import them. `check-direct-vercel.py`
verifies these exact HTML exceptions and the Briefing checkpoint; its existing
renderer and original-asset checks remain in force.

## What the collision check measures

`scripts/check-mobile-subject-wrap.py` reads captured DOM geometry. It compares
each non-whitespace character's `Range.getClientRects()` bounds with an
independent mask generated from the approved source artwork. It does not reuse
the CSS shape polygon and does not reject overlap with the full image rectangle:
copy is supposed to occupy the image's quiet paper area.

Each source mask is the actual luminance-below-0.82 ink inside a separate figure
ROI. Components smaller than 16 source pixels are discarded as isolated dots;
all substantial components are retained so a disconnected helmet, hand or
garment detail cannot disappear merely because it is not the largest component.
The checker requires a substantial nonempty mask and records its source hash,
dimensions, threshold, ROI, component count and pixel count. Object fit, object
position and any explicit source crop project the mask into the captured art
stage. Character bounds need 10 CSS pixels of clearance from that protected ink.

These are conservative character boxes, not exact glyph outlines. A failure can
include a box's empty corners or an intentional close approach and needs visual
review; it must not be silently waived or relabelled as a measured glyph hit.
A pass covers the figure's dark ink, not every pale silhouette pixel, scenery,
all animation phases, font quality or physical iPhone behavior. The lower scene
still requires screenshot review, particularly around the kneeler's landscape.

Every measured character must also remain inside the hero bounds and horizontal
viewport, with only 0.5 CSS pixels of measurement tolerance. This tests clipping
per character rather than only checking the containing paragraph. The hero may
extend below the initial screen and remain reachable by normal page scrolling;
that is not text clipping. Original wording remains locked separately by the
source verifier, and each capture's full text must match its character records.

## Capture set

Capture Company, Solutions and Training at 320, 390, 430 and 600 CSS pixels after
the actual page reports `data-mobile-wrap="ready"`, its source image is decoded,
and the compositor is ready. Keep screenshots and matching read-only geometry
JSON. Use stable scroll position and record the browser and capture kind.
Geometry from the in-app browser is Chromium evidence. Native macOS Safari
screenshots are WebKit visual evidence; they are not physical iPhone captures.
Where native Safari cannot provide character JSON, label those screenshots as
visual review only rather than claiming they passed this automated test.

Before replacing the fixed-column layout, retain its geometry as a baseline.
The checker must reject that baseline's 54% paragraph width. Also retain
Briefing screenshots and confirm that it was not changed. Desktop and tablet
composition checks continue separately.

The JSON input is an array of records (or `*-capture.json` files in a folder).
Each record contains:

```json
{
  "page": "company",
  "width": 390,
  "scrollWidth": 390,
  "browser": "in-app Chromium",
  "captureKind": "responsive emulation",
  "wrapReady": true,
  "afterHeadline": true,
  "hero": {"left": 0, "top": 73, "right": 390, "bottom": 673},
  "copy": {"left": 0, "top": 73, "right": 390, "bottom": 673},
  "headline": {"left": 24, "top": 101, "right": 366, "bottom": 179},
  "paragraph": {"left": 24, "top": 205, "right": 366, "bottom": 430},
  "span": {"left": 180, "top": 179, "right": 390, "bottom": 640},
  "art": {"left": -60, "top": 200, "right": 450, "bottom": 540},
  "styles": {"paddingLeft": "24px", "paddingRight": "24px", "artPosition": "absolute"},
  "image": {
    "src": "images/art-v3/company-knight.webp",
    "naturalWidth": 1536,
    "naturalHeight": 1024,
    "objectFit": "contain",
    "objectPosition": "50% 50%",
    "crop": null
  },
  "texts": {"headline": "Complete actual heading", "paragraph": "Complete actual paragraph"},
  "glyphs": [
    {"char": "C", "role": "headline", "rects": [{"left": 24, "top": 101, "right": 47, "bottom": 144}]}
  ],
  "screenshot": "company-390.png"
}
```

The numbers and abbreviated glyph array above illustrate the schema; they are
not captured results and deliberately cannot pass text-completeness validation.
Use the entire actual heading and paragraph text, plus every non-space
character's rectangles. Include `texts.action` and `role: "action"` records for
the visible hero link/button text. An optional `image.sha256` is checked against
the source. `image.crop`, if present, is `[offsetX, offsetY, width, height]` in
normalized source coordinates, matching `data-art-crop`.

A read-only character collector for the browser capture is:

```js
function characterBounds(element, role) {
  const output = [];
  const walker = document.createTreeWalker(element, 4);
  let node;
  while ((node = walker.nextNode())) {
    if (node.parentElement.closest('[aria-hidden="true"],svg')) continue;
    let offset = 0;
    for (const char of node.data) {
      const end = offset + char.length;
      if (!/\s/u.test(char)) {
        const range = document.createRange();
        range.setStart(node, offset);
        range.setEnd(node, end);
        output.push({char, role, rects: Array.from(range.getClientRects(), r => ({
          left:r.left, top:r.top, right:r.right, bottom:r.bottom
        }))});
      }
      offset = end;
    }
  }
  return output;
}
```

`afterHeadline` is measured with
`mobileFloat.previousElementSibling === heading`. Record actual computed copy
padding and image `objectFit`/`objectPosition`; do not substitute the intended
values from the stylesheet. The source-aspect test checks measured geometry,
while source review confirms that art height is not derived from paragraph
height. A single capture alone cannot prove behavior for every future copy edit.

## Commands and sensitivity controls

```sh
python3 scripts/check-mobile-subject-wrap.py --self-test
python3 scripts/check-mobile-subject-wrap.py baseline.json --widths 390 --expect-baseline-failure --output baseline-results.json
python3 scripts/check-mobile-subject-wrap.py captures.json --output wrap-results.json
```

For an initial 390px-only pass, append `--widths 390`; this does not stand in for
the complete 12-record capture set. Self-test rejects the old 54% paragraph
constraint and deliberately moves a character onto real protected source ink.
An empty mask or incomplete character capture cannot pass.
It also moves a character 0.75px beyond the hero/viewport edge and requires that
capture to fail the stricter 0.5px clipping gate.

The retained `baseline.json` has three actual 390px records, so its command
explicitly selects that width. Company and Solutions reproduce a restricted
paragraph width; Training already had a full-width paragraph but lacked the
new after-headline float and independent source-aspect stage. This sensitivity
run is a rejection of the previous layout, not an accepted candidate result.

The float's exclusion may extend below the actual image to keep resumed copy
clear of the last row of ink. The current 40px extension changes exclusion
height only; the image must still retain its source aspect ratio. Conservative
character bounds and 10px clearance remain the collision contract even when
the visible ink is only punctuation. Report a proximity flag as proximity,
rather than asserting that a glyph visibly overlaps the artwork.

## Captured results

`results.json` records 12 of 12 passing candidate captures: Company, Solutions
and Training at 320, 390, 430 and 600px. Paragraphs use the complete reading
width; after-headline floats and source-aspect image stages are ready. Complete
character records remain inside the hero/horizontal viewport within the 0.5px
tolerance and meet the independent protected-source-ink clearance test.
`baseline-results.json` rejects all three earlier 390px records, establishing
that the regression check distinguishes the previous layout.

Every candidate's captured `texts` object is exactly equal to its page's
baseline text: 12 of 12 comparisons pass, including heading, supporting copy
and action text. The source verifier independently locks the original HTML
copy, apart from the previously approved contact/navigation substitutions.
Text has not been shortened or rewritten to obtain these layouts.

`native-safari/` retains 12 page-only cropped screenshots from native macOS
Safari Responsive Design Mode, covering those same three pages and four
widths. These received visual review. They have no corresponding per-character
Safari JSON and therefore are not claimed as automated collision-test passes.
They are not physical iPhone Safari captures.

`desktop-tablet-control.json` contains 24 records forming 12 baseline/candidate
pairs: Company, Solutions, Training and the unchanged Briefing control at 768,
1024 and 1440px. Hero, headline, paragraph and artwork rectangles match exactly
within every pair. `resize-without-reload.json` adds nine records from each of
the three affected pages passing through phone, tablet and phone again. The
mobile wrap enables, clears and re-enables correctly without document reload,
and the recorded widths show no horizontal overflow.

These are local browser and source checks. No production deployment or physical
iPhone result is established by this folder; publication evidence and any
subsequent device feedback must be recorded separately.
