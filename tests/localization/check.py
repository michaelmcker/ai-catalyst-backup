#!/usr/bin/env python3
"""Cross-page invariants: complete localization, links, direction, discovery and media."""
import importlib.util,json,re,sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('localized',ROOT/'scripts/build-localized-site.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class Doc(HTMLParser):
 def __init__(self,s):super().__init__();self.tags=[];self.ids=set();self.feed(s)
 def handle_starttag(self,t,a):
  attrs=dict(a);self.tags.append((t,attrs))
  if 'id' in attrs:self.ids.add(attrs['id'])
urls=set();count=0
for locale,(prefix,label,direction) in mod.LOCALES.items():
 for name in mod.PAGES:
  target=ROOT/'current-site'/prefix/name;s=target.read_text();doc=Doc(s);count+=1
  assert (ROOT/prefix/name).read_bytes()==target.read_bytes(),target
  ht=next(a for t,a in doc.tags if t=='html');assert ht['lang']==locale and ht['dir']==direction
  canonical=[a['href'] for t,a in doc.tags if t=='link' and a.get('rel')=='canonical'];assert canonical==[mod.ORIGIN+mod.route(name,locale)];urls.add(canonical[0])
  alternates={a['hreflang']:a['href'] for t,a in doc.tags if t=='link' and a.get('hreflang')}
  assert alternates=={**{l:mod.ORIGIN+mod.route(name,l) for l in mod.LOCALES},'x-default':mod.ORIGIN+mod.route(name,'en')}
  assert sum(t=='script' and a.get('src','').split('?')[0]=='/analytics.js' for t,a in doc.tags)==1
  assert sum(a.get('data-show-id')=='6acba942-8926-485c-ba7a-3e794baa11ba' for _,a in doc.tags)==1
  assert 'mailto:randy@aicatalyst.biz' in s and 'tel:+14162700132' in s
  nav_paths=[urlsplit(a.get('href','')).path for t,a in doc.tags if t=='a']
  assert all(mod.route(n,locale) in nav_paths for n in ['solutions.html','training.html','company.html','platform.html'])
  assert sum('language-picker' in a.get('class','').split() for _,a in doc.tags)==1
  for t,a in doc.tags:
   for key in ('src','href','poster','data-deferred-src'):
    v=a.get(key,'');parts=urlsplit(v)
    if not v or parts.scheme or parts.netloc or v.startswith('#'):continue
    p=ROOT/'current-site'/unquote(parts.path.lstrip('/'))
    if p.is_dir():p=p/'index.html'
    assert p.exists(),(target,key,v)
assert count==len(mod.PAGES)*len(mod.LOCALES) and len(urls)==count
import xml.etree.ElementTree as ET
sitemap={e.text for e in ET.parse(ROOT/'current-site/sitemap.xml').iter() if e.tag.endswith('loc')};assert sitemap==urls
# A missing translation, changed source, or unreviewed catalog must fail generation.
mod.build(check=True)
base=mod.read_json('en.json');missing=dict(base);missing.pop(next(iter(base)))
try:mod.Renderer('Test unknown sentence', 'index.html','fr-CA',missing,base).render();raise AssertionError('unregistered text accepted')
except ValueError:pass
print('PASS: 44 page editions; complete equivalents, valid assets, telemetry/embed, RTL, discovery, mirrors and stale-source guards.')
