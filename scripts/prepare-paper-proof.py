#!/usr/bin/env python3
"""Generate local-only paper/compositor fixtures, never public-site files.

Serve the repository at /, the downloaded Vercel snapshot at /__vercel/,
and current-site/ at /current-site/. Browser capture remains a separate step.
"""
from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'docs/safari-paper-2026-10-23/proof'
STAGE = {'left': 180.375, 'top': 64.625, 'width': 208.25, 'height': 339.75}
PAPER = {'home': (214, 235, 252), 'company': (234, 247, 254)}
VARIANTS = ('tinted', 'grain', 'transparent')
RENDERERS = ('original', 'candidate')
ROIS = {
    'interior': [224, 110, 364, 350],
    'left_boundary': [175, 85, 214, 365],
}


def make_texture(path, color, variant):
    im = Image.new('RGBA', (384, 512), (*color, 0 if variant == 'transparent' else 255))
    if variant == 'grain':
        pixels = im.load()
        for y in range(im.height):
            for x in range(im.width):
                delta = 2 if (x + y) % 2 else -2
                pixels[x, y] = (*[max(0, min(255, c + delta)) for c in color], 255)
    im.save(path)


def fixture(renderer, scene, variant):
    base = '/__vercel/' if renderer == 'original' else '/current-site/'
    asset = 'sword-hand' if scene == 'home' else 'knight'
    art_class = 'hero-art' if scene == 'home' else 'page-hero__art'
    profile = 'data-mobile-art-print=".90" data-art-feather=".26 .04 .24 .22"' if scene == 'home' else 'data-art-profile="close"'
    art = f'''<div class="{art_class}" data-site-art="hero" data-art-asset="{asset}" {profile}><img src="paper-{scene}-{variant}.png" alt="" width="384" height="512" decoding="sync"></div>'''
    composition = f'<div class="hero-scene" data-art-surface="white-flow"><section class="hero">{art}</section></div>' if scene == 'home' else f'<section class="page-hero">{art}</section>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Paper proof: {renderer} / {scene} / {variant}</title>
<style>
*{{box-sizing:border-box}}html,body{{margin:0;padding:0;background:#fff}}
body{{overflow:hidden}}#main{{padding:0!important}}
.hero-scene,.hero,.page-hero{{position:relative;isolation:isolate;width:100vw;height:600px;margin:0;padding:0;overflow:hidden;background:#fff}}
.hero{{background:transparent}}
.hero-art,.page-hero__art{{position:absolute;left:{STAGE['left']}px;top:{STAGE['top']}px;width:{STAGE['width']}px;height:{STAGE['height']}px;z-index:0;background:transparent}}
[data-site-art]>img,[data-site-art]>.site-art-tones{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center;display:block}}
[data-site-art].site-art-ready>img{{visibility:hidden}}
.site-art-tones{{z-index:1;pointer-events:none}}
.site-hero-field,.site-hero-composite{{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;display:block!important;pointer-events:none!important;z-index:-1!important;mix-blend-mode:normal!important}}
.hero-scene[data-art-surface="white-flow"] .site-hero-field{{z-index:1!important;mix-blend-mode:multiply!important}}
.hero-scene[data-art-surface="white-flow"] .site-hero-composite{{z-index:0!important;mix-blend-mode:normal!important}}
</style></head>
<body class="motion-paused {'restored-home' if scene == 'home' else 'subpage'}" data-proof-renderer="{renderer}" data-proof-scene="{scene}" data-proof-variant="{variant}">
<main id="main">{composition}</main><script src="{base}halftone-rendering.js?paper-proof=1"></script>
<script>
(() => {{
  const observer = new MutationObserver(record);
  function record() {{
    const art = document.querySelector('[data-site-art]');
    if (!art.classList.contains('site-art-ready')) return;
    observer.disconnect();
    const output = document.createElement('script');
    output.type = 'application/json'; output.id = 'paper-proof-capture-state';
    output.textContent = JSON.stringify({{
      userAgent:navigator.userAgent, devicePixelRatio, innerWidth, innerHeight,
      paused:document.body.classList.contains('motion-paused'),
      reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,
      canvases:Array.from(document.querySelectorAll('canvas')).map(canvas => {{
        const gl = canvas.getContext('webgl'); const r = canvas.getBoundingClientRect();
        return {{className:canvas.className, bitmap:[canvas.width,canvas.height],
          rect:{{x:r.x,y:r.y,width:r.width,height:r.height}},
          attributes:gl ? gl.getContextAttributes() : null,
          drawingBufferColorSpace:gl?.drawingBufferColorSpace ?? null}};
      }})
    }});
    document.body.append(output);
    document.documentElement.dataset.paperProofReady = 'true';
  }}
  observer.observe(document.body,{{subtree:true,attributes:true,childList:true}});
  record();
}})();
</script>
</body></html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT)
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    for scene, color in PAPER.items():
        for variant in VARIANTS:
            make_texture(output / f'paper-{scene}-{variant}.png', color, variant)
    rows = []
    relative = output.relative_to(ROOT).as_posix()
    for renderer in RENDERERS:
        for scene in PAPER:
            for variant in VARIANTS:
                stem = f'{renderer}-{scene}-{variant}'
                (output / f'{stem}.html').write_text(fixture(renderer, scene, variant))
                rows.append({
                    'name': stem, 'renderer': renderer, 'scene': scene, 'variant': variant,
                    'url_path': f'/{relative}/{stem}.html',
                    'screenshots': {str(dpr): f'{stem}-dpr{dpr}.png' for dpr in (1, 2, 3)},
                })
    sources = {}
    for renderer, path in [('original', Path('/tmp/ai-catalyst-direct-vercel/halftone-rendering.js')), ('candidate', ROOT / 'current-site/halftone-rendering.js')]:
        if path.exists():
            sources[renderer] = {'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    manifest = {'viewport': {'width': 390, 'height': 600}, 'requested_dprs': [1, 2, 3],
                'stage_css': STAGE, 'paper_rgb': PAPER, 'grain': 'alternating source pixels, RGB +/-2',
                'rois_css': ROIS, 'sources_at_generation': sources, 'fixtures': rows}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'Generated {len(rows)} fixtures and six PNG textures under {output}')
    print(f'URL prefix: /{relative}/')


if __name__ == '__main__':
    main()
