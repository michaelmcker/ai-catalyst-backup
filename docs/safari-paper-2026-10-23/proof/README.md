# Isolated paper continuity proof

These files are local diagnostics, excluded from `current-site/` and every
deployment manifest. They do not modify the public renderer or layout.

`python3 scripts/prepare-paper-proof.py` generates twelve identical geometries:
original/candidate renderer, Home/Company rendering branch, and tinted/grained/
transparent source texture. The original script is served from the verified
download at `/__vercel/halftone-rendering.js`. The candidate is served from
`/current-site/halftone-rendering.js`. The manifest records hashes at generation
time; regenerate after changing the candidate and before capturing evidence.

Each page is 390 CSS pixels wide and 600 pixels high. Its illustration stage has
fractional coordinates `(180.375, 64.625, 208.25, 339.75)` to expose grid alignment
at a non-integer origin. Text and controls do not occupy the measured regions.
`motion-paused` freezes both image and field at clock zero. The full-page capture
must follow `html[data-paper-proof-ready="true"]`; that attribute is set after
the renderer marks the art ready. The JSON script `#paper-proof-capture-state`
records the actual user agent, DPR, viewport, canvas dimensions and WebGL context
attributes for the capture operator to save beside the screenshots.

The opaque textures use actual pale source-paper colors: Home `(214,235,252)`
and Company `(234,247,254)`. Their grain variants alternate RGB values by +/-2
at adjacent source pixels. The matching controls have exactly the same RGB
values with alpha zero. A source paper region should be visually equivalent to
the common field it replaces, including at a feathered stage boundary.

Capture the twelve pages at 390x600 CSS pixels with browser DPR set separately
to 1, 2 and 3. Use the filenames under `fixtures[].screenshots` in manifest.json.
Then run:

```sh
python3 scripts/check-paper-proof.py CAPTURE_DIR --require-original-failure --output docs/safari-paper-2026-10-23/proof/pixel-results.json
```

The checker compares tinted/grained paper to its transparent control within
the same renderer, scene, paused phase and DPR. Candidate pixels must differ
by no more than two RGB channel levels in both an interior region and a strip
crossing the left boundary. `--require-original-failure` also demands an exposed
original discontinuity somewhere at every tested DPR, preventing an insensitive
fixture from passing as a repair. It does not require every original case to
fail: Home's original luminance key already removes much of this particular
source color in conforming engines.

This establishes isolated paper parity, not the quality of every illustration,
live pointer motion, full-site layout or actual iOS execution. A Chromium
failure demonstrates a source/compositing problem independently of Safari.
Only results captured in iPhone Safari establish how these fixtures behave on
that device. The DPR filename alone is not evidence of an iPhone or WebKit.

An additional Safari hypothesis is supported by WebKit issue200026: older
compositors can mishandle `premultipliedAlpha:false`, turning light blue partial
alpha output white. The fix landed in WebKit main on2026-09-08, which does not
establish the installed iOS version contains it. A valid independent A/B changes
the context to premultiplied alpha and multiplies final RGB by alpha; changing
the flag alone is invalid. See [WebKit's issue](https://bugs.webkit.org/show_bug.cgi?id=200026)
and [its merged implementation](https://github.com/WebKit/WebKit/pull/73156).
