"""Check rendered hero geometry and print at both edges, including the bottom.
Usage: python3 scripts/check-hero-pattern.py evidence_directory before|after
Screenshots and geometry are captured through the browser tool, not synthesized.
"""
import json, sys
from pathlib import Path
from PIL import Image
folder, prefix = Path(sys.argv[1]), sys.argv[2]
checks = json.loads((folder / (prefix + '.json')).read_text())
failures = []
for item in checks:
    page = item['page'].strip('/').removesuffix('.html')
    im = Image.open(folder / (prefix + '-' + page + '.png')).convert('RGB')
    hero = item['hero']
    scale = im.width / item['viewport']['width']
    bands = {}
    for name, top, bottom in [('top', hero['top'] + 8, hero['top'] + 28),
                               ('bottom', hero['bottom'] - 28, hero['bottom'] - 8)]:
        if bottom > item['viewport']['height']:
            continue
        pixels = []
        for left, right in [(4, 28), (hero['width'] - 28, hero['width'] - 4)]:
            pixels.extend(im.crop(tuple(round(x * scale) for x in (left, top, right, bottom))).get_flattened_data())
        blue = sum(b - r > 3 and b - g > 1 for r, g, b in pixels) / len(pixels)
        bands[name] = round(blue, 3)
        if blue < .10:
            failures.append(f'{page}: {name} hero edge is blank ({blue:.1%} blue pixels)')
    if not item['sideBySide']:
        failures.append(f'{page}: artwork is below the copy instead of beside it')
    print(json.dumps({'page': page, 'sideBySide': item['sideBySide'], 'pattern': bands}))
if failures:
    print('\n'.join(failures))
    sys.exit(1)
