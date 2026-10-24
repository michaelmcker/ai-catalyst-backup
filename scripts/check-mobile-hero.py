#!/usr/bin/env python3
"""Validate browser-captured hero composition and physical texture resolution.
Usage: python3 scripts/check-mobile-hero.py docs/visual-repair-2026-10-23/rendered-checks.json
The old compact-home checks were superseded by Michael's subsequent correction.
"""
import json
import sys
from pathlib import PurePosixPath
from urllib.parse import urlparse

PANORAMAS = {'platform', 'creator-social', 'marketing-investment', 'online-conversion'}
failures = []
rows = json.load(open(sys.argv[1]))
for row in rows:
    name = PurePosixPath(urlparse(row['url']).path).stem or 'index'
    hero, art, heading, copy = (row[key] for key in ('hero', 'art', 'heading', 'copy'))
    label = f"{name}@{row['width']}"
    def require(condition, message):
        if not condition:
            failures.append(f'{label}: {message}')
    require(row['ready'], 'image enhancement did not finish')
    require(row['overflow'] <= 1, 'horizontal overflow')
    require(heading['bottom'] <= hero['bottom'] + 1, 'headline leaves hero')
    require(abs(hero['top'] - row['header']['bottom']) <= 1, 'gap below navigation')
    selected = next((value.strip().split() for value in row['srcset'].split(',')
                     if row['src'].endswith(value.strip().split()[0])), None)
    require(selected is not None and row['textureWidth'] == float(selected[1][:-1]),
            'texture sampling does not use physical source pixels')
    if name in PANORAMAS:
        require(art['top'] >= heading['bottom'], 'image is above the headline')
        require(abs(art['top'] - copy['bottom']) <= 1, 'space between copy and panoramic image')
        require(abs(art['width'] - hero['width']) <= 1 and abs(art['left'] - hero['left']) <= 1,
                'panoramic image is not full width')
        require(row['sizes'] == '100vw', 'panoramic image has an undersized delivery hint')
        if row['width'] > 700:
            support = row['support']
            require(support['left'] >= heading['right'] and abs(support['top'] - heading['top']) < 12,
                    'headline and support are not left/right')
    elif name == 'index' and row['width'] <= 700:
        require(art['width'] >= hero['width'] * .65, 'homepage figure was reduced to a thumbnail')
        require(heading['width'] >= hero['width'] * .85, 'homepage headline squeezed into a narrow column')
        require(art['left'] > hero['width'] * .4 and art['top'] < copy['bottom'], 'figure is not beside copy')
    else:
        require(art['left'] >= hero['width'] * .4 and art['top'] < copy['bottom'], 'side artwork is not beside copy')
if failures:
    sys.exit('\n'.join('FAIL: ' + failure for failure in failures))
print(f'PASS: {len(rows)} rendered hero checks; full-width copy-first panoramas, substantial Home artwork, physical texture sampling, header joins and no overflow.')
