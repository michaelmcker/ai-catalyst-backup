#!/usr/bin/env python3
"""Build the public, static case-study index and detail pages from local content."""
import argparse,html,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ARROW='<span class="arrow-icon" aria-hidden="true"><svg viewBox="0 0 20 20"><path d="M4 16 16 4M7 4h9v9"></path></svg></span>'
def escape(value):return html.escape(value,quote=True)
def build():
 studies=json.loads((ROOT/'content/case-studies.json').read_text());shell=(ROOT/'templates/case-studies-shell.html').read_text();output={};tiles=[];slugs=set()
 def page(title,description,path,main):
  result=shell
  for key,value in {'title':escape(title),'description':escape(description),'path':escape(path),'main':main}.items():result=result.replace('{{'+key+'}}',value)
  return result
 for study in studies:
  slug=study['slug'];assert re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*',slug) and slug not in slugs;slugs.add(slug)
  assert re.fullmatch(r'[\w-]{11}',study['youtubeId']);assert study['thumbnail'].startswith('/assets/')
  href='/case-studies/'+slug+'/'
  image=f'<img src="{escape(study["thumbnail"])}" alt="{escape(study["thumbnailAlt"])}" width="1280" height="720" loading="lazy" decoding="async">'
  tiles.append(f'<article><a class="study-tile" href="{href}" aria-label="View {escape(study["name"])} case study"><div class="study-cover">{image}<span class="study-duration">{escape(study["duration"])} film</span></div><h2>{escape(study["name"])}</h2><p>{escape(study["title"])}</p><span class="study-link">View case study {ARROW}</span></a></article>')
  film=f'<figure class="service-film study-film"><a class="service-film__play" href="https://youtu.be/{study["youtubeId"]}" data-youtube-id="{study["youtubeId"]}" data-video-title="{escape(study["title"])}" aria-label="Play the {escape(study["name"])} case study">{image}<span class="service-film__icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M7 3 22 12 7 21Z"/></svg></span><span class="service-film__duration" aria-hidden="true">{escape(study["duration"])}</span></a></figure>'
  sections=''.join(f'<section><h2>{escape(s["heading"])}</h2><p>{escape(s["body"])}</p></section>' for s in study['sections'])
  main=f'<a class="back-link" href="/case-studies/">All case studies</a><h1>{escape(study["title"])}</h1><p class="study-intro">{escape(study["summary"])}</p>{film}<div class="study-body">{sections}</div><div class="study-next"><a class="study-link" href="/briefing.html">Talk about your business {ARROW}</a></div>'
  output['case-studies/'+slug+'/index.html']=page(study['title'],study['summary'],href,main)
 output['case-studies/index.html']=page('Case studies','Explore AI Catalyst’s work and watch the case-study films.','/case-studies/','<h1>Case studies</h1><div class="study-grid">'+''.join(tiles)+'</div>')
 urls=['https://aicatalyst.biz/case-studies/']+['https://aicatalyst.biz/case-studies/'+s['slug']+'/' for s in studies]
 output['case-studies/sitemap.xml']='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in urls)+'</urlset>\n'
 return output
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();output=build()
 for path,source in output.items():
  for prefix in ('current-site/',''):
   target=ROOT/(prefix+path)
   if args.check:assert target.exists() and target.read_text()==source,'Static output differs: '+str(target)
   else:target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
 print(('PASS: ' if args.check else 'Built ')+str(len(output))+' static case-study pages/sitemap and exact root mirrors.')
