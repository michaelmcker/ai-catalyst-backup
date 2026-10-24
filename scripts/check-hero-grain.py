#!/usr/bin/env python3
"""Check actual screenshot pixels for visible, pale print around hero copy."""
import json
import sys
from pathlib import Path
from PIL import Image

folder = Path(sys.argv[1])
failures, results = [], []
for row in json.load(open(folder/'rendered-checks.json')):
    if row['width'] not in (390, 1440):
        continue
    name = row['url'].rsplit('/', 1)[-1].removesuffix('.html')
    im = Image.open(folder/f"{name}-{row['width']}.png").convert('RGB')
    scale = im.width / row['width']
    y = row['hero']['top'] + 8
    pixels = []
    for x in (4, round(row['hero']['width']) - 20):
        box = tuple(round(v*scale) for v in (x, y, x+16, y+10))
        pixels.extend(im.crop(box).get_flattened_data())
    blue = sum(b-r > 3 and b-g > 1 for r, g, b in pixels)/len(pixels)
    light = sum(sum(p)/3 for p in pixels)/len(pixels)
    if blue < .08 or light < 244:
        failures.append(f"{name}@{row['width']}: field is blank or too dark ({blue:.1%} blue, {light:.1f}/255 brightness)")
    results.append({'page': name, 'width': row['width'], 'blueFraction': round(blue, 3), 'meanBrightness': round(light, 2)})
(folder/'grain-checks.json').write_text(json.dumps(results, indent=2)+'\n')
if failures:
    sys.exit('\n'.join(failures))
print(f'PASS: {len(results)} screenshot checks; visible pale blue print at both hero edges.')
