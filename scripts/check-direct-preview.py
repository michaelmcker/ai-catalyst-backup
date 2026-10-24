#!/usr/bin/env python3
"""Verify captured preview responses and the explicitly requested layouts."""
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image, ImageChops
import json

ROOT=Path(__file__).resolve().parents[1]
PROOF=ROOT/'docs/direct-vercel-2026-10-23'
PANO={'platform','creator-social','marketing-investment','online-conversion'}
fail=[]
rows=[]
for filename in ('mobile-geometry.json','desktop-geometry.json','narrow-mobile-geometry.json'):
    rows.extend(json.loads((PROOF/'preview'/filename).read_text()))
for row in rows:
    name=Path(urlparse(row['url']).path).stem or 'index'
    label=f"{name}@{row['width']}"
    if not row['ready'] or row['opacity']!='1':fail.append(label+': artwork entrance incomplete')
    if row['overflow']>1 or row['headingOverflow']>1:fail.append(label+': overflow')
    if any('linkedin' in link['href'].lower() for link in row['links']):fail.append(label+': retired link')
    if not any(link['href']=='mailto:randy@aicatalyst.biz' for link in row['links']):fail.append(label+': missing email')
    if name in PANO:
        if row['paragraph']['left']<row['heading']['right']-1:fail.append(label+': support is not right of headline')
        if abs(row['art']['top']-row['copy']['bottom'])>1:fail.append(label+': image/copy gap')
        if abs(row['art']['width']-row['hero']['width'])>1:fail.append(label+': image is not full width')
    if name=='company' and row['width']<=700:
        if row['heading']['right']>row['art']['left'] or row['paragraph']['right']>row['art']['left']:
            fail.append(label+': Company text collides with knight')
        if row['art']['top']>=row['copy']['bottom']:fail.append(label+': Company is stacked')
    if name in ('company','platform') and row['width']<=700:
        if abs(row['hero']['top']-row['header']['bottom'])>1:fail.append(label+': navigation gap')
    if name=='company' and row['width']>1000:
        if abs(row['art']['width']-row['hero']['width'])>1:fail.append(label+': Company desktop stage differs from Vercel')
for f in (PROOF/'preview').glob('served-*'):
    if f.read_bytes()!=(ROOT/'current-site'/f.name.removeprefix('served-')).read_bytes():
        fail.append(f.name+': live response differs from checked source')

# A clock-frozen stationary control must remain identical. Compare only the
# paper ROI, excluding glyphs and the test controls. Require exact reference
# parity for the shared captured Home pointer passes; elapsed time cannot pass.
p=PROOF/'pointer-proof';roi=(100,375,650,407);values={}
for source in ('reference','candidate'):
    a=Image.open(p/f'{source}-index-stationary0.png').convert('RGB').crop(roi)
    b=Image.open(p/f'{source}-index-stationary1.png').convert('RGB').crop(roi)
    if ImageChops.difference(a,b).getbbox():fail.append(source+': stationary paper changed')
    changes=[]
    for i in range(3):
        b=Image.open(p/f'{source}-index-pointer{i}.png').convert('RGB').crop(roi)
        changes.append(sum(max(px)>2 for px in ImageChops.difference(a,b).get_flattened_data()))
    values[source]=changes
if values['reference']!=values['candidate'] or not max(values['candidate']):fail.append('Home causal pointer response differs from Vercel')
if fail:raise SystemExit('\n'.join('FAIL: '+s for s in fail))
print(f'PASS: {len(rows)} preview layouts, served-source equality, contact routes and exact clock-frozen Home pointer response.')
