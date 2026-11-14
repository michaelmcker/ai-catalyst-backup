#!/usr/bin/env python3
"""Refresh source catalogs/hashes after editing English templates; never approves translations."""
from html.parser import HTMLParser
from pathlib import Path
import re,html,json,hashlib
root=Path(__file__).resolve().parents[1]
strings={};pages={}
class Extract(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.skip=[]
 def add(self,s):
  s=s.strip()
  if re.search('[A-Za-z]',s) and not re.fullmatch(r'(?:https?://|mailto:|tel:).*',s) and '@' not in s:
   strings[hashlib.sha256(s.encode()).hexdigest()[:12]]=s
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip.append(t)
  for k,v in a:
   if v and (k in ('alt','aria-label','placeholder','title','data-video-title') or (t=='meta' and k=='content' and any(x in ('description','og:title','og:description','twitter:title','twitter:description') for _,x in a))):self.add(v)
 def handle_endtag(self,t):
  if self.skip and self.skip[-1]==t:self.skip.pop()
 def handle_data(self,d):
  if not self.skip:self.add(d)
for p in sorted((root/'templates/i18n').rglob('*.html')):
 name=str(p.relative_to(root/'templates/i18n'));Extract().feed(p.read_text());pages[name]=hashlib.sha256(p.read_bytes()).hexdigest()
(root/'content/i18n/en.json').write_text(json.dumps(strings,ensure_ascii=False,indent=2)+'\n')
(root/'content/i18n/source-manifest.json').write_text(json.dumps(pages,indent=2)+'\n')
print(str(len(strings))+' source strings across '+str(len(pages))+' pages. Update every locale catalog, review meaning, then run build-localized-site.py --record-review.')
