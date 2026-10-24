# Frozen-clock pointer proof

These diagnostic documents stay outside `current-site/` and are excluded from
deployment. Each fixture copies its named source HTML, adds an absolute local
asset base and injects a test harness. The harness does not edit the loaded
renderer or artwork. `manifest.json` records the source snapshots, renderer URLs
and hashes at fixture preparation. The candidate renderer includes the declared
opaque-compositing repair; it is not presented as byte-identical to Vercel.

## Why stationary controls matter

An ordinary before/after hero screenshot can differ because time advanced,
even if the mouse did nothing. This harness fixes only the WebGL uniform named
`clock` to 7s and queues animation frames. **Step frames**, or **N**, runs two
virtual frames at the original nominal 24fps interval. The small timestamp
epsilon avoids rounding below the trail update threshold. Pointer events and
the renderer's normal pointer/trail logic still run. Queued frames do not decay
while screenshots are saved.

With the pointer outside the hero, `stationary0` and `stationary1` must be
pixel-identical in the selected paper ROI. Pointer movement followed by the
same virtual steps must then change that fixed region. This isolates pointer
input from ambient clock progression. It does not measure frame rate or imply
that every image pixel responds to the pointer.

## Captured results

All captures use a 1440×1000 screenshot at frozen phase 7. The retained capture
JSON records normal motion (`pointerProofReduced=false`, paused=false), virtual
frames, clock writes, canvas readiness and pointer position. The paper ROIs are
Home `(100,350)–(650,550)`, other portrait pages `(640,300)–(850,500)`, and
panoramic pages `(730,150)–(775,300)`.

| Candidate page | Stationary changed pixels | Pointer changed pixels |
| --- | ---: | ---: |
| Home | 0 | 251 |
| Company | 0 | 20343 |
| How We Work | 0 | 20425 |
| Start a conversation | 0 | 20545 |
| Training and adoption | 0 | 20343 |
| Commerce Command Centre | 0 | 5006 |
| Creator Intelligence | 0 | 5057 |
| Full Commerce MMM | 0 | 5071 |
| Agentic Consumer Intelligence | 0 | 5006 |

The reference Company paper changes 0 pixels for both its stationary pair and
pointer pair. This is consistent with the original nonwhite `paperTone`
implementation: its background does not read the pointer. The candidate extends
that original paper with the existing V1 Gaussian disturbance while retaining
its resting print values. That extension is explicit rather than falsely
claimed as exact reference behavior.

`reduced-company-{stationary0,stationary1,pointer}.png` repeats the Company case
with the browser's real `prefers-reduced-motion:reduce` setting. The capture JSON
records the preference before it was restored. Both pixel comparisons must be
zero, demonstrating that pointer input does not bypass the motion preference.
Normal Company captures were refreshed after restoring normal motion.

Run `python3 scripts/check-safari-hero-proof.py` to regenerate
`pixel-results.json` and the parent `verification-results.json`. The script
requires zero stationary changes, nonzero pointer changes for all nine
candidates, zero reference Company changes and zero reduced-motion Company
changes. These PNG results establish the captured desktop behavior only.
Actual iPhone Safari feedback remains a separate release checkpoint.
