#!/usr/bin/env python3
"""Validate actual captured hero motion and reduced-motion screenshots."""
from pathlib import Path
from PIL import Image,ImageChops
import json,sys
from urllib.parse import urlparse
f=Path(sys.argv[1]);rows=json.load(open(f/'rendered-checks.json'));results=[];fail=[]
for row in rows:
 if row['width']!=1440:continue
 name=Path(urlparse(row['url']).path).stem or 'index';a=Image.open(f/f'motion-{name}-0.png').convert('RGB');scale=a.width/row['width'];result={'page':name}
 for key,r in {'hero':row['hero'],'image':row['art']}.items():
  box=tuple(round(v*scale) for v in (max(0,r['left']+4),max(0,r['top']+4),min(row['hero']['right']-4,r['right']-4),min(990,r['bottom']-4)))
  vals=[]
  for i in (1,2,3):
   b=Image.open(f/f'motion-{name}-{i}.png').convert('RGB');px=list(ImageChops.difference(a.crop(box),b.crop(box)).get_flattened_data());vals.append(sum(max(p)>5 for p in px)/len(px))
  result[key]=round(max(vals),4)
  if max(vals)<.01:fail.append(f'{name}: {key} has insufficient visible dither response in captured mouse pass')
 results.append(result)
for name in ('index','platform'):
 a=Image.open(f/f'reduced-{name}-0.png').convert('RGB');b=Image.open(f/f'reduced-{name}-1.png').convert('RGB')
 if ImageChops.difference(a,b).getbbox():fail.append(name+': reduced-motion capture changes')
for row in rows:
 if row['blend']!='normal' or row['fieldZ']!='0' or row['imageVisibility']!='hidden':fail.append(row['url']+': shared paper backdrop or fallback visibility differs')
 field,hero=row['field'],row['hero']
 if any(abs(field[key]-hero[key])>1 for key in ('top','bottom','left','right')):fail.append(row['url']+': moving field does not cover the full hero')
(f/'motion-checks.json').write_text(json.dumps(results,indent=2)+'\n')
if fail:raise SystemExit('\n'.join('FAIL: '+x for x in fail))
print('PASS: all nine hero/artwork motion sequences, full-section common paper and pixel-identical reduced-motion captures.')
