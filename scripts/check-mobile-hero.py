#!/usr/bin/env python3
"""Check captured browser geometry for the compact mobile portrait heroes."""
import json
import sys

failures = []
for page in json.load(open(sys.argv[1])):
    hero = page['hero']
    image = next(item['rect'] for item in page['art'] if item['tag'] == 'IMG')
    name = page['url'].rsplit('/', 1)[-1] or 'home'
    if image['width'] > hero['width'] * 0.55:
        failures.append(f"{name}: artwork is {image['width'] / hero['width']:.0%} of the hero; expected <=55%")
    if image['x'] < hero['x'] + hero['width'] * 0.45:
        failures.append(f'{name}: artwork does not sit on the right')
    if page['heading']['y'] > image['bottom']:
        failures.append(f'{name}: copy is stacked below the artwork')
    if page['heading']['bottom'] > hero['bottom'] or page['overflow'] > 1:
        failures.append(f'{name}: headline or page overflows')
if failures:
    print('\n'.join('FAIL: ' + failure for failure in failures))
    sys.exit(1)
print('PASS: compact right-hand artwork, copy beside image, contained headline and no overflow.')
