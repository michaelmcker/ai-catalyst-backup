"""Deterministic discovery files and JSON-LD from the visible localized HTML."""
import json,re,html
from pathlib import Path
ORIGIN='https://aicatalyst.biz'
ROOT=Path(__file__).resolve().parents[1]
POSTS={p['slug']:p for p in json.loads((ROOT/'content/blog/posts.json').read_text())}
def plain(s):return html.unescape(re.sub(r'<[^>]+>',' ',s)).strip()
def text(s):return re.sub(r'\s+',' ',plain(s)).strip()
def grab(s,pattern):
 m=re.search(pattern,s,re.S);return text(m[1]) if m else ''
def parts(s):
 summary=grab(s,r'<section class="blog-summary"[^>]*>.*?<p>(.*?)</p>')
 transcript=grab(s,r'<div class="transcript-text">(.*?)</div>')
 faqs=[(text(q),text(a)) for q,a in re.findall(r'<section class="faq-item"><h3>(.*?)</h3><p>(.*?)</p></section>',s,re.S)]
 return summary,transcript,faqs
def decorate(s,name,locale,url):
 title=grab(s,r'<title>(.*?)</title>');heading=grab(s,r'<h1[^>]*>(.*?)</h1>') or title
 org=ORIGIN+'/#organization';person=ORIGIN+'/#randy';website=ORIGIN+'/#website';page=url+'#webpage'
 nodes=[{'@type':'Organization','@id':org,'name':'AI Catalyst','url':ORIGIN+'/','logo':ORIGIN+'/assets/logo.svg','email':'randy@aicatalyst.biz','telephone':'+1-416-270-0132'}, {'@type':'Person','@id':person,'name':'Randy Weyersberg','url':ORIGIN+'/company.html','worksFor':{'@id':org}}, {'@type':'WebSite','@id':website,'name':'AI Catalyst','url':ORIGIN+'/','publisher':{'@id':org}}, {'@type':'WebPage','@id':page,'url':url,'name':heading,'inLanguage':locale,'isPartOf':{'@id':website}}]
 extra=''
 if name.startswith('blog/'):
  index=url.rsplit('/blog/',1)[0]+'/blog/'
  series={'en':'Coffee Chats with Randy','fr-CA':'Cafés-discussions avec Randy','fr-FR':'Conversations café avec Randy','ar':'أحاديث القهوة مع Randy'}[locale]
  crumbs=[{'@type':'ListItem','position':1,'name':'AI Catalyst','item':ORIGIN+('/' if locale=='en' else '/'+{'fr-CA':'fr-ca','fr-FR':'fr-fr','ar':'ar'}[locale]+'/')},{'@type':'ListItem','position':2,'name':series,'item':index}]
  slug=name.split('/')[1]
  if slug in POSTS:
   p=POSTS[slug];summary,transcript,faqs=parts(s)
   nodes[-1]['@type']=['WebPage','FAQPage'];nodes[-1]['mainEntity']=[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faqs]
   image=ORIGIN+p['thumbnail'];article=url+'#article';video=url+'#video'
   nodes.extend([{'@type':'BlogPosting','@id':article,'headline':heading,'description':summary,'url':url,'mainEntityOfPage':{'@id':page},'inLanguage':locale,'author':{'@id':person},'publisher':{'@id':org},'image':[image],'datePublished':p['published'],'dateModified':p['modified'],'video':{'@id':video}}, {'@type':'VideoObject','@id':video,'name':heading,'description':summary,'thumbnailUrl':image,'embedUrl':'https://www.youtube-nocookie.com/embed/'+p['video'],'url':'https://www.youtube.com/watch?v='+p['video'],'inLanguage':'en','transcript':POSTS[slug]['text'],'isPartOf':{'@id':article}}])
   crumbs.append({'@type':'ListItem','position':3,'name':heading,'item':url})
   extra='<meta property="og:type" content="article"><meta property="og:image" content="'+image+'"><meta property="og:image:alt" content="'+html.escape(heading,quote=True)+'">'
  else:
   nodes[-1]['@type']='CollectionPage'
  nodes.append({'@type':'BreadcrumbList','@id':url+'#breadcrumbs','itemListElement':crumbs})
  extra+='<link rel="alternate" type="text/markdown" href="'+url+'index.md">'
 payload=json.dumps({'@context':'https://schema.org','@graph':nodes},ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
 return s.replace('</head>',extra+'<script type="application/ld+json">'+payload+'</script></head>')
def exports(outputs):
 result={'robots.txt':'User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /_emdash/\nDisallow: /docs/\nDisallow: /templates/\nDisallow: /content/\n\nSitemap: '+ORIGIN+'/sitemap.xml\n'}
 lines=['# AI Catalyst','', '> Senior commercial judgment, AI capabilities and practical workflows, with Coffee Chats by Randy Weyersberg.','', 'Canonical website: '+ORIGIN+'/. English, Quebec French, France French and Arabic editions are linked below. Videos remain English.','', '## Main pages']
 for name in ['index.html','solutions.html','training.html','platform.html','company.html','briefing.html','case-studies/index.html']:
  path='/' if name=='index.html' else '/'+name.replace('index.html','');s=outputs[name];lines.append('- ['+grab(s,r'<title>(.*?)</title>')+']('+ORIGIN+path+')')
 lines+=['','## Coffee Chats and language editions']
 full=['# AI Catalyst Coffee Chats','', 'Public summaries, transcripts and FAQs. Each section links to its canonical HTML source. Video statements remain attributed to Randy Weyersberg.','']
 for name,s in outputs.items():
  if '/blog/' not in '/'+name or not name.endswith('.html'):continue
  path='/'+name.replace('index.html','');url=ORIGIN+path;heading=grab(s,r'<h1[^>]*>(.*?)</h1>');summary,transcript,faqs=parts(s)
  lines.append('- ['+heading+']('+url+'index.md): '+url)
  md=['# '+heading,'','Source: '+url,'']
  if summary:md+=['## Summary','',summary,'','## Transcript','',transcript,'','## FAQ','']+[f'### {q}\n\n{a}\n' for q,a in faqs]
  else:md+=['Coffee Chats by Randy Weyersberg.']+['- ['+text(t)+']('+ORIGIN+h+')' for h,t in re.findall(r'<h2><a href="([^"]+)">(.*?)</a></h2>',s,re.S)]
  result[name.replace('index.html','index.md')]='\n'.join(md)+'\n'
  full.extend(md+['','---',''])
 lines+=['','## Full Coffee Chats text','- [Full text of all Coffee Chat language editions]('+ORIGIN+'/llms-full.txt)','', 'For the complete public URL list, use '+ORIGIN+'/sitemap.xml.']
 result['llms.txt']='\n'.join(lines)+'\n';result['llms-full.txt']='\n'.join(full)+'\n';return result
