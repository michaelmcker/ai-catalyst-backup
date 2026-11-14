#!/usr/bin/env python3
"""Build complete static language editions from scoped HTML translation slots.
Edit templates/i18n and catalogs together; --check detects stale output or source.
"""
import argparse, hashlib, html, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
ROOT=Path(__file__).resolve().parents[1]
ORIGIN='https://aicatalyst.biz'
LOCALES={'en':('','English','ltr'),'fr-CA':('fr-ca','Français (Québec)','ltr'),'fr-FR':('fr-fr','Français (France)','ltr'),'ar':('ar','العربية','rtl')}
SHORT_LABELS={'en':'CAN EN','fr-CA':'CAN FR','fr-FR':'FRA FR','ar':'AR'}
LANGUAGE_NAMES={'en':'English (Canada)','fr-CA':'Français (Québec, Canada)','fr-FR':'Français (France)','ar':'العربية'}
UI={
'en':('Language','Choose language','Close','Read this page in English','Video and the external twin may remain in English.'),
'fr-CA':('Langue','Choisir la langue','Fermer','Lire cette page en français québécois','Les vidéos et le jumeau numérique externe peuvent rester en anglais.'),
'fr-FR':('Langue','Choisir la langue','Fermer','Lire cette page en français','Les vidéos et le jumeau numérique externe peuvent rester en anglais.'),
'ar':('اللغة','اختر اللغة','إغلاق','اقرأ هذه الصفحة بالعربية','قد تبقى مقاطع الفيديو والتوأم الرقمي الخارجي باللغة الإنجليزية.')}
def key(s):return hashlib.sha256(s.strip().encode()).hexdigest()[:12]
def route(name,locale):
 prefix=LOCALES[locale][0];p='' if name=='index.html' else name[:-10] if name.endswith('/index.html') else name
 return '/'+('/'.join(x for x in (prefix,p) if x)) + ('/' if prefix and not p else '')
def read_json(name):return json.loads((ROOT/'content/i18n'/name).read_text())
class Renderer(HTMLParser):
 def __init__(self,source,name,locale,catalog,known):
  super().__init__(convert_charrefs=True);self.source=source;self.name=name;self.locale=locale;self.catalog=catalog;self.known=known;self.edits=[];self.skip=[];self.starts=[0]
  self.starts += [m.end() for m in re.finditer('\n',source)]
 def pos(self):line,col=self.getpos();return self.starts[line-1]+col
 def translate(self,s):
  stripped=s.strip();k=key(stripped)
  if k not in self.known:
   if re.search('[A-Za-z]',stripped) and '@' not in stripped and not re.fullmatch(r'(?:https?://|mailto:|tel:).*',stripped):raise ValueError('Uncatalogued text: '+stripped)
   return s
  if k not in self.catalog:raise ValueError(f'{self.locale} missing {k}: {stripped}')
  return s[:len(s)-len(s.lstrip())]+self.catalog[k]+s[len(s.rstrip()):]
 def asset(self,v,islink=False):
  if not v or v.startswith(('#','data:','mailto:','tel:','javascript:')):return v
  parsed=urlsplit(urljoin(ORIGIN+'/'+self.name,v))
  if parsed.netloc!='aicatalyst.biz':return v
  path=parsed.path
  if islink:
   target=path.lstrip('/') or 'index.html'
   if target.endswith('/'):target+='index.html'
   if target in PAGES:path=route(target,self.locale)
  return urlunsplit(('', '',path,parsed.query,parsed.fragment))
 def handle_starttag(self,t,attrs):
  start=self.pos();raw=self.get_starttag_text();pairs=dict(attrs)
  if t in ('script','style'):self.skip.append(t)
  def replace(m):
   name=m.group(1).lower();value=html.unescape(m.group(3));new=value
   if name in ('alt','aria-label','placeholder','title','data-video-title') or (t=='meta' and name=='content' and (pairs.get('name') in ('description','twitter:title','twitter:description') or pairs.get('property') in ('og:title','og:description'))):new=self.translate(value)
   if name in ('href','src','poster','data-deferred-src'):new=self.asset(value,name=='href')
   if new==value:return m.group(0)
   return m.group(1)+'='+m.group(2)+html.escape(new,quote=True)+m.group(2)
  new=re.sub(r'([\w:-]+)\s*=\s*([\"\'])(.*?)\2',replace,raw,flags=re.S)
  if t=='html':new=re.sub(r'lang=[\"\'][^\"\']*[\"\']',f'lang="{self.locale}" dir="{LOCALES[self.locale][2]}"',new)
  if new!=raw:self.edits.append((start,start+len(raw),new))
 def handle_endtag(self,t):
  if self.skip and self.skip[-1]==t:self.skip.pop()
 def handle_data(self,d):
  if self.skip:return
  start=self.pos();end=self.source.find('<',start)
  if end<0:end=len(self.source)
  raw=self.source[start:end];value=html.unescape(raw);new=self.translate(value)
  if new!=value:self.edits.append((start,end,html.escape(new,quote=False)))
 def render(self):
  self.feed(self.source);s=self.source
  for a,b,v in sorted(self.edits,reverse=True):s=s[:a]+v+s[b:]
  # Normalize discovery metadata, without touching the authored page layout.
  s=re.sub(r'<link\b[^>]*rel=[\"\'](?:canonical|alternate)[\"\'][^>]*>','',s)
  discovery=f'<link rel="canonical" href="{ORIGIN}{route(self.name,self.locale)}">'
  for loc in LOCALES:discovery+=f'<link rel="alternate" hreflang="{loc}" href="{ORIGIN}{route(self.name,loc)}">'
  discovery+=f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{route(self.name,"en")}">'
  s=s.replace('</head>',discovery+'<link rel="stylesheet" href="/localization.css?v=20261114-2"><script src="/language-switcher.js?v=20261113-1" defer></script></head>')
  if self.locale=='ar':s=s.replace('halftone-rendering.js?v=20261024-direct9','halftone-rendering.js?v=20261114-ar1')
  label,choose,close,_,notice=UI[self.locale]
  links=''.join(f'<a href="{route(self.name,l)}" lang="{l}" hreflang="{l}" data-language="{l}" title="{html.escape(LANGUAGE_NAMES[l],quote=True)}" aria-label="{SHORT_LABELS[l]} — {html.escape(LANGUAGE_NAMES[l],quote=True)}"'+(' aria-current="true"' if l==self.locale else '')+f'>{SHORT_LABELS[l]}</a>' for l in LOCALES)
  current_name=html.escape(LANGUAGE_NAMES[self.locale],quote=True)
  switch=f'<details class="language-picker"><summary title="{current_name}" aria-label="{choose}: {SHORT_LABELS[self.locale]} — {current_name}">{SHORT_LABELS[self.locale]}</summary><nav aria-label="{choose}">{links}</nav></details>'
  s=s.replace('<div class="masthead-actions">','<div class="masthead-actions">'+switch,1)
  if self.locale!='en':s=s.replace('<footer class="site-footer',f'<p class="locale-media-note wrap">{notice}</p><footer class="site-footer',1)
  # CSS-generated content must be localized as well.
  if self.locale!='en':
   labels={'fr-CA':'Intelligence des créateurs\\A Vente en direct agentique\\A Modélisation du mix commercial\\A\\A Votre plan de mise en marché + les initiatives de la concurrence\\A\\A Moteur de décision de mise en marché','fr-FR':'Intelligence des créateurs\\A Vente en direct agentique\\A Modélisation du mix commercial\\A\\A Votre plan de commercialisation + les initiatives concurrentes\\A\\A Moteur de décision de commercialisation','ar':'تحليل نشاط صناع المحتوى\\A البيع المباشر بالوكلاء الذكيين\\A نمذجة المزيج التجاري\\A\\A خطتك لدخول السوق وتحركات المنافسين\\A\\A محرك قرارات دخول السوق'}
   s=s.replace('</head>','<style>.operating-layer:after{content:"'+labels[self.locale]+'"}</style></head>')
  return s
PAGES=sorted(read_json('source-manifest.json'))
def build(check=False,record_review=False):
 known=read_json('en.json');outputs={};reviews={}
 for locale in LOCALES:
  catalog=read_json(locale+'.json')
  if set(catalog)!=set(known):raise ValueError(f'{locale}: catalog keys differ')
  if any(not isinstance(v,str) or not v.strip() for v in catalog.values()):raise ValueError(f'{locale}: empty translations')
  for name in PAGES:
   source=(ROOT/'templates/i18n'/name).read_text();expected=read_json('source-manifest.json')[name]
   if hashlib.sha256(source.encode()).hexdigest()!=expected:raise ValueError('Source changed; refresh catalogs and translation review: '+name)
   target=('/'.join(filter(None,(LOCALES[locale][0],name))))
   outputs[target]=Renderer(source,name,locale,catalog,known).render()
  reviews[locale]={'catalog_sha256':hashlib.sha256(json.dumps(catalog,ensure_ascii=False,sort_keys=True).encode()).hexdigest(),'source_sha256':hashlib.sha256(json.dumps(read_json('source-manifest.json'),sort_keys=True).encode()).hexdigest(),'review':'source-completeness and model editorial review; not certified native-speaker review'}
 urls=[ORIGIN+route(n,l) for l in LOCALES for n in PAGES]
 outputs['sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>\n'
 outputs['case-studies/sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+ORIGIN+route(n,l)+'</loc></url>' for l in LOCALES for n in PAGES if n.startswith('case-studies/'))+'</urlset>\n'
 if not record_review:
  if read_json('review.json')!=reviews:raise ValueError('Translation/source review hashes changed. Review all affected copy, then record with --record-review.')
 for name,s in outputs.items():
  for prefix in ('current-site/',''):
   p=ROOT/(prefix+name)
   if check:
    if not p.exists() or p.read_text()!=s:raise ValueError('Stale output: '+str(p))
   else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
 metadata={'locales':LOCALES,'routes':{n:{l:route(n,l) for l in LOCALES} for n in PAGES},'review':reviews}
 for name,obj in [('locales.json',LOCALES),('routes.json',metadata['routes']),('review.json',reviews)]:
  p=ROOT/'content/i18n'/name;s=json.dumps(obj,ensure_ascii=False,indent=2)+'\n'
  if not check and (name!='review.json' or record_review):p.write_text(s)
 print(('PASS: ' if check else 'Built ')+str(len(urls))+' page editions with complete catalogs, route equivalents and root mirrors.')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--record-review',action='store_true',help='Record the completed source/model editorial review; not native certification');args=p.parse_args();build(args.check,args.record_review)
