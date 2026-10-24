#!/usr/bin/env python3
"""Verify the direct Vercel transfer with the narrow approved edit allowlist."""
from pathlib import Path
import hashlib, json, re, runpy, subprocess

ROOT=Path(__file__).resolve().parents[1]
CONTENT=runpy.run_path(str(ROOT/'scripts/apply-approved-content.py'))
PANO={'platform','creator-social','marketing-investment','online-conversion'}
MANIFEST=ROOT/'docs/direct-vercel-2026-10-23/source-manifest.json'

def original(path):
    return subprocess.check_output(['git','show','68dbb96:current-site/'+path],cwd=ROOT)

def expected(path,source):
    if path in CONTENT['FILES']:
        source=CONTENT['patch'](source,path)
        CONTENT['validate_result'](source,path)
    if path.endswith('.html'):
        s=source.decode()
        if Path(path).stem in PANO:
            s=s.replace('class="subpage ','class="subpage migration-pano ',1)
            s=s.replace('class="page-hero ','class="page-hero page-hero--stacked ',1)
            s,n=re.subn(r'(<div class="page-hero__copy"><h1>[\s\S]*?</h1>)(<p>[\s\S]*?</p>)(<a class="hero-link"[\s\S]*?</a>)(</div>)',r'\1<div class="page-hero__support">\2<div class="page-hero__actions">\3</div></div>\4',s,count=1)
            assert n==1,path
        s=s.replace('</head>','<link rel="stylesheet" href="migration-changes.css?v=20261023-direct7"></head>',1)
        s=re.sub(r'(halftone-rendering.js|feedback-v3.css)(?:\?[^"\s]+)?',r'\1?v=20261023-direct7',s)
        source=s.encode()
    return source

def check():
    rows=json.loads(MANIFEST.read_text());fail=[]
    for row in rows:
        path=row['path'];source=original(path)
        if hashlib.sha256(source).hexdigest()!=row['sha256'] or not row['matches_git_reference']:
            fail.append(path+': downloaded Vercel source differs from reference')
        result=expected(path,source)
        for prefix in ('current-site/',''):
            if (ROOT/(prefix+path)).read_bytes()!=result:
                fail.append(prefix+path+': change outside approved content/panorama allowlist')
    css=(ROOT/'current-site/migration-changes.css').read_text()
    if (ROOT/'migration-changes.css').read_text()!=css:fail.append('migration CSS mirror differs')
    if any(x in css for x in ('site-hero-field','site-art-tones','mix-blend-mode','.hero-art','white-flow')):
        fail.append('migration CSS changes the original rendering system')
    for page in ('index','company','solutions','briefing','training'):
        html=(ROOT/'current-site'/f'{page}.html').read_text()
        if 'hero-layout.css' in html or 'site-assets.js' in html or 'images/optimized' in html:
            fail.append(page+': previous adaptive renderer/delivery imports remain')
    if fail:raise SystemExit('\n'.join('FAIL: '+s for s in fail))
    print(f'PASS: {len(rows)} directly downloaded Vercel files; exact original rendering/assets and Home/Company markup; approved content/navigation, panorama arrangements and scoped Company mobile layout only.')

if __name__=='__main__':check()
