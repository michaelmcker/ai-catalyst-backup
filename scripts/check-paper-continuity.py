#!/usr/bin/env python3
"""Check photographed paper contrast and opaque/transparent shader parity.

The phone sample is the empty left gutter, excluding text and illustration.
The fixture renders identical heroes with opaque white and transparent source
paper. Their artwork rectangles must resolve onto the same common field.
"""
import argparse, json
from PIL import Image, ImageChops

p=argparse.ArgumentParser()
p.add_argument('phone')
p.add_argument('--fixture')
p.add_argument('--fixture-clear')
args=p.parse_args()
im=Image.open(args.phone).convert('RGB'); scale=im.width/390
box=tuple(round(v*scale) for v in (0,100,18,380))
lum=sorted((.2126*r+.7152*g+.0722*b)/255 for r,g,b in im.crop(box).get_flattened_data())
report={'paper_mean_luminance':sum(lum)/len(lum), 'paper_darkest_percentile':lum[len(lum)//100]}
fail=[]
if report['paper_mean_luminance']<.965 or report['paper_darkest_percentile']<.84:
    fail.append('paper behind copy is too dark (mean < .965 or darkest percentile < .84)')
if args.fixture:
    fixture=Image.open(args.fixture).convert('RGB'); s=fixture.width/390
    a=fixture.crop(tuple(round(v*s) for v in (0,0,390,300)))
    b=Image.open(args.fixture_clear).convert('RGB').crop(tuple(round(v*s) for v in (0,0,390,300)))
    differences=list(ImageChops.difference(a,b).get_flattened_data())
    report['opaque_transparent_max_difference']=max(max(p) for p in differences)
    if report['opaque_transparent_max_difference']>2:
        fail.append('opaque image paper does not match the common field')
print(json.dumps(report,indent=2))
if fail:raise SystemExit('\n'.join('FAIL: '+x for x in fail))
print('PASS: light paper contrast and common-field continuity.')
