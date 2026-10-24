# Local causal pointer proof

These fixtures are diagnostic documents outside `current-site/`. They must not
be deployed. The production HTML, renderer and assets are not edited. Each
fixture is a snapshot of its named source HTML with an absolute server-relative
asset base and an injected test harness. `manifest.json` records source and
renderer SHA-256 values, so a renderer difference cannot be hidden by the test.

The harness fixes only the WebGL uniform named `clock` to one phase (default 7
seconds; change with `?phase=0`, `?phase=7` or `?phase=17`). It queues animation
frames until **Step frames** is clicked or **N** is pressed. Each step runs two
nominal 24fps frames, enough for the unmodified renderer's trail update. The
0.001ms epsilon avoids floating-point rounding at its elapsed-time threshold.
Queued frames do not decay while screenshots are taken. Pointer events and the
renderer's pointer/trail code remain unchanged. Reduced-motion and the paused
body class are reported, never overridden.

## Capture procedure

1. Open a fixture with normal motion preferences. Wait for the hero's
   `site-art-ready` class and visible canvas, then step several times so the
   renderer has initialized. Record viewport, DPR, frozen phase, motion
   preference, paused body class, hero/image/copy bounds and source hashes.
2. Keep the pointer outside the hero. Capture a small paper-only rectangle
   behind or beside the headline; exclude glyphs, artwork, controls and the
   header. Step and capture that same rectangle again. The stationary pair must
   be pixel-identical; otherwise the region or fixture is not a valid control.
3. Move the real pointer continuously through that rectangle, then press **N**
   without moving it away. Capture again. Any changed pixels now come from
   pointer/trail input at the same ambient phase. Use multiple positions and
   phases because ordered thresholds can remain unchanged at an individual
   field value. Keep the crop fixed and report its coordinates and changed
   pixel count, rather than requiring an arbitrary whole-hero percentage.
4. Repeat the same procedure for reference and candidate at matching viewport,
   DPR, phase and relative paper positions. Capture image-only regions separately
   if artwork wake behavior is being assessed.

Exact Vercel Company uses the time-driven `paperTone` background, whose shader
does not read the pointer uniform. Its paper-only pointer delta may correctly be
zero while its artwork responds to trails. Exact Vercel Home's `v1Paper` is
pointer-aware. Judge candidate parity against the reference; do not invent a
Company paper response to satisfy a test. Frozen-clock proof isolates pointer
causality and does not replace normal-clock visual or animation checks.

The preview server must map the reference asset prefix from the generator's
`--reference-url` to its `--reference-source` directory, and the candidate prefix
to `current-site`. Defaults are `/__vercel/` and `/current-site/`. All original
scripts are loaded from those named source mounts, including the unchanged
renderer. A desktop Safari run is WebKit evidence, not physical iPhone Safari
evidence.
