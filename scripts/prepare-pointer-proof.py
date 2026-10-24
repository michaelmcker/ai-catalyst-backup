#!/usr/bin/env python3
"""Prepare local-only, causal pointer fixtures without editing either site source.

The preview server must mount --reference-url at --reference-source and serve
--candidate-url from current-site. Fixture URLs and asset bases are absolute
server-relative paths, so neither source is accidentally loaded from the other.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re


REPO = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = REPO / "docs/direct-vercel-2026-10-23/pointer-proof"

BOOTSTRAP = r"""
<script data-pointer-proof-bootstrap>
(() => {
  'use strict';
  const params = new URLSearchParams(location.search);
  const requestedPhase = Number(params.get('phase') || '7');
  const phase = Number.isFinite(requestedPhase) ? requestedPhase : 7;
  const uniformNames = new WeakMap();
  let clockWrites = 0;
  const contexts = [window.WebGLRenderingContext, window.WebGL2RenderingContext]
    .filter(Boolean);
  for (const Context of contexts) {
    const proto = Context.prototype;
    const getUniformLocation = proto.getUniformLocation;
    const uniform1f = proto.uniform1f;
    proto.getUniformLocation = function(program, name) {
      const location = getUniformLocation.call(this, program, name);
      if (location) uniformNames.set(location, name);
      return location;
    };
    proto.uniform1f = function(location, value) {
      if (location && uniformNames.get(location) === 'clock') {
        value = phase;
        clockWrites++;
      }
      return uniform1f.call(this, location, value);
    };
  }
  let nextId = 1;
  let virtualTime = 1000;
  let frameCount = 0;
  let pending = new Map();
  window.requestAnimationFrame = callback => {
    const id = nextId++;
    pending.set(id, callback);
    return id;
  };
  window.cancelAnimationFrame = id => pending.delete(id);

  function status() {
    const root = document.documentElement;
    root.dataset.pointerProofFrames = String(frameCount);
    root.dataset.pointerProofPhase = String(phase);
    root.dataset.pointerProofClockWrites = String(clockWrites);
    root.dataset.pointerProofReduced = String(
      matchMedia('(prefers-reduced-motion: reduce)').matches);
    root.dataset.pointerProofPaused = String(
      document.body?.classList.contains('motion-paused') || false);
    const output = document.getElementById('pointer-proof-status');
    if (output) output.textContent =
      `Frozen clock ${phase}s; virtual frames ${frameCount}; ` +
      `clock writes ${clockWrites}; reduced ${root.dataset.pointerProofReduced}; ` +
      `paused ${root.dataset.pointerProofPaused}`;
  }
  function step() {
    // Two nominal 24fps frames let the original 18fps trail update run once.
    // A 0.001ms epsilon avoids its strict elapsed-time threshold rounding down.
    for (let i = 0; i < 2; i++) {
      virtualTime += 1000 / 24 + 0.001;
      const callbacks = pending;
      pending = new Map();
      for (const callback of callbacks.values()) callback(virtualTime);
      frameCount++;
    }
    status();
  }
  document.addEventListener('DOMContentLoaded', () => {
    const controls = document.createElement('aside');
    controls.id = 'pointer-proof-controls';
    controls.setAttribute('aria-label', 'Local pointer proof controls');
    controls.innerHTML =
      '<strong>__SOURCE_LABEL__ / __PAGE__ — local diagnostic fixture</strong>' +
      '<button type="button" id="pointer-proof-step">Step frames</button>' +
      '<span>Move the pointer over paper, then press N to step without moving it away.</span>' +
      '<output id="pointer-proof-status" aria-live="polite"></output>';
    document.body.append(controls);
    controls.querySelector('button').addEventListener('click', step);
    document.addEventListener('keydown', event => {
      if (event.code === 'KeyN' && !event.altKey && !event.ctrlKey &&
          !event.metaKey && !event.repeat &&
          !event.target.matches('input,textarea,select,[contenteditable]')) {
        event.preventDefault();
        step();
      }
    });
    status();
  });
})();
</script>
<style data-pointer-proof-controls>
#pointer-proof-controls{position:fixed!important;inset:auto 10px 10px auto!important;
 z-index:2147483647!important;display:grid!important;gap:6px!important;
 width:min(560px,calc(100vw - 20px))!important;padding:12px!important;
 color:#111!important;background:#fff!important;border:1px solid #444!important;
 font:12px/1.4 system-ui,sans-serif!important;box-shadow:0 2px 12px #0003!important}
#pointer-proof-controls button{justify-self:start!important;padding:6px 12px!important;
 color:#fff!important;background:#12347a!important;font:14px system-ui,sans-serif!important}
#pointer-proof-controls output{font-variant-numeric:tabular-nums!important}
</style>
"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def server_path(value: str) -> str:
    if not value.startswith("/") or value.startswith("//") or "?" in value or "#" in value:
        raise argparse.ArgumentTypeError("Use a server-relative absolute URL, e.g. /current-site/")
    return value.rstrip("/") + "/"


def prepare(args: argparse.Namespace) -> dict:
    args.output.mkdir(parents=True, exist_ok=True)
    sources = [
        ("reference", "Exact Vercel source", args.reference_source, args.reference_url),
        ("candidate", "Current site source", args.candidate_source, args.candidate_url),
    ]
    manifest = {
        "testOnly": True,
        "clockUniformFrozen": True,
        "virtualFrameMilliseconds": 1000 / 24 + 0.001,
        "framesPerStep": 2,
        "defaultPhaseSeconds": 7,
        "sourceFilesModified": False,
        "fixtures": [],
    }
    for key, label, source, base in sources:
        renderer = source / "halftone-rendering.js"
        renderer_bytes = renderer.read_bytes()
        for page in args.pages:
            original = (source / f"{page}.html").read_bytes()
            text = original.decode("utf-8")
            if re.search(r"<base\b", text, re.I):
                raise ValueError(f"Unexpected existing base element in {source / (page + '.html')}")
            bootstrap = BOOTSTRAP.replace("__SOURCE_LABEL__", html.escape(label)).replace("__PAGE__", page)
            injection = f'<base href="{html.escape(base, quote=True)}">\n' + bootstrap
            text, count = re.subn(r"(<head\b[^>]*>)", lambda m: m[1] + injection, text, count=1, flags=re.I)
            if count != 1:
                raise ValueError(f"Missing head in {source / (page + '.html')}")
            output = args.output / f"{key}-{page}.html"
            output.write_text(text, encoding="utf-8")
            manifest["fixtures"].append({
                "source": key,
                "page": page,
                "sourceHtml": str(source / f"{page}.html"),
                "sourceHtmlSha256": digest(original),
                "rendererSha256": digest(renderer_bytes),
                "rendererUrl": base + "halftone-rendering.js",
                "assetBase": base,
                "fixture": str(output.relative_to(REPO)) if output.is_relative_to(REPO) else str(output),
                "fixtureSha256": digest(text.encode("utf-8")),
            })
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (args.output / "README.md").write_text(README)
    return manifest


README = """# Local causal pointer proof

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
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-source", type=Path, default=Path("/tmp/ai-catalyst-direct-vercel"))
    parser.add_argument("--candidate-source", type=Path, default=REPO / "current-site")
    parser.add_argument("--reference-url", type=server_path, default="/__vercel/")
    parser.add_argument("--candidate-url", type=server_path, default="/current-site/")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--pages", nargs="+", choices=("index","company","solutions","briefing","training","platform","creator-social","marketing-investment","online-conversion"), default=("index","company"))
    args = parser.parse_args()
    manifest = prepare(args)
    print(json.dumps({"output": str(args.output), "fixtures": len(manifest["fixtures"]),
                      "rendererHashes": {x["source"]: x["rendererSha256"] for x in manifest["fixtures"]}}, indent=2))


if __name__ == "__main__":
    main()
