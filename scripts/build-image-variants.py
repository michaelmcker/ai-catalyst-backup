#!/usr/bin/env python3
"""Encode delivery variants with cwebp, preserving every approved source master."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'current-site'
OUT = SITE / 'images/optimized'
OUT.mkdir(exist_ok=True)
jobs = {}

def variant(source, width):
    key = (source, width)
    digest = hashlib.sha256((SITE/source).read_bytes() + f'webp80:{width}'.encode()).hexdigest()[:10]
    target = f'images/optimized/{Path(source).stem}-{width}-{digest}.webp'
    jobs[key] = target
    return target

def attr(tag, name):
    found = re.search(r'(?<![\w-])' + re.escape(name) + r'="([^"]*)"', tag)
    return found[1] if found else None

def set_attr(tag, name, value):
    pattern = r'(?<![\w-])' + re.escape(name) + r'="[^"]*"'
    replacement = f'{name}="{value}"'
    return re.sub(pattern, replacement, tag) if re.search(pattern, tag) else tag[:-1] + ' ' + replacement + '>'

def image(tag):
    source = attr(tag, 'data-original-src') or attr(tag, 'src')
    if not source or not source.startswith('images/') or source.endswith('.svg'):
        return tag
    portrait = '/advisors/' in source
    widths = [320, 640] if portrait else [640, 1280]
    targets = [variant(source, width) for width in widths]
    tag = set_attr(tag, 'data-original-src', source)
    tag = set_attr(tag, 'src', targets[-1])
    tag = set_attr(tag, 'srcset', ', '.join(f'{target} {width}w' for target, width in zip(targets, widths)))
    if portrait:
        sizes = '(max-width:700px) 40vw, 280px'
    elif 'sword-hand' in source:
        sizes = '(max-width:700px) 72vw, 62vw'
        tag = set_attr(tag, 'fetchpriority', 'high')
    elif any(part in source for part in ['company-knight', 'kneeling-courtyard', 'briefing-arcade', 'portrait-halftone']):
        sizes = '(max-width:700px) 40vw, 52vw'
        tag = set_attr(tag, 'fetchpriority', 'high')
    elif attr(tag, 'fetchpriority') == 'high' or '/art-v4/' in source or 'bridge-halftone' in source:
        sizes = '100vw'
    else:
        sizes = '(max-width:700px) 100vw, 60vw'
    return set_attr(tag, 'sizes', sizes)

def svg_image(tag):
    source = attr(tag, 'data-original-href') or attr(tag, 'href')
    if not source or not source.startswith('images/ai-catalyst/') or source.endswith('.svg'):
        return tag
    target = variant(source, 320)
    tag = re.sub(r'(?<![\w-])href="[^"]*"\s*', '', tag)
    tag = set_attr(tag, 'data-original-href', source)
    return set_attr(tag, 'data-deferred-href', target)

for page in SITE.glob('*.html'):
    source = page.read_text()
    source = re.sub(r'<img\b[^>]*>', lambda match: image(match[0]), source)
    source = re.sub(r'<image\b[^>]*>', lambda match: svg_image(match[0]), source)
    if 'data-deferred-href=' in source and 'site-assets.js' not in source:
        source = source.replace('</body>', '<script src="site-assets.js?v=20261023-performance1" defer></script></body>')
    page.write_text(source)

def encode(job):
    (source, width), target = job
    if not (SITE/target).exists():
        subprocess.run(['cwebp', '-quiet', '-q', '80', '-m', '5', '-resize', str(width), '0', str(SITE/source), '-o', str(SITE/target)], check=True)
    return {'source': source, 'width': width, 'target': target, 'bytes': (SITE/target).stat().st_size}

with ThreadPoolExecutor(max_workers=4) as pool:
    manifest = list(pool.map(encode, jobs.items()))
(ROOT/'scripts/image-variants.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Encoded {len(manifest)} delivery variants; source masters unchanged.')
