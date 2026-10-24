#!/usr/bin/env python3
"""Check a paired controlled-network first-artwork probe; not a field LCP score."""
import argparse,json
from pathlib import Path

def check(before,after):
 failures=[]
 if before['network']!=after['network']:failures.append('network/cache conditions differ')
 if before['page']!=after['page']:failures.append('different page')
 if after['elapsedToArtwork']>before['elapsedToArtwork']*.65:failures.append('first rendered artwork improved by less than35%')
 if after['heroResource']['bytes']>before['heroResource']['bytes']*.8:failures.append('hero payload improved by less than20%')
 if after['deferred']<1:failures.append('no offscreen artwork is deferred')
 return failures

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--output',type=Path);a=p.parse_args()
 before=json.loads(a.before.read_text());after=json.loads(a.after.read_text());failures=check(before,after)
 assert check(before,before),'baseline must fail the loading improvement gate'
 result={'measurement':'local Chromium iframe first-artwork readiness; not physical iPhone or field LCP','network':before['network'],'before_ms':before['elapsedToArtwork'],'after_ms':after['elapsedToArtwork'],'improvement_percent':(1-after['elapsedToArtwork']/before['elapsedToArtwork'])*100,'before_hero_bytes':before['heroResource']['bytes'],'after_hero_bytes':after['heroResource']['bytes'],'red_control':'baseline as candidate rejected','failures':failures,'passed':not failures}
 if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
 if failures:raise SystemExit('FAIL: '+'; '.join(failures))
 print(f"PASS: first artwork {result['before_ms']:.0f}ms → {result['after_ms']:.0f}ms under identical controlled network; baseline-as-candidate rejects.")
