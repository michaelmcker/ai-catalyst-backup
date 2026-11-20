import importlib.util,json,re
from pathlib import Path
from html import unescape
R=Path(__file__).resolve().parents[2];base=R/'current-site'
spec=importlib.util.spec_from_file_location('discovery',R/'scripts/site-discovery.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
count=0
for p in base.rglob('*.html'):
 s=p.read_text();schemas=re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S);assert len(schemas)==1,p
 graph=json.loads(schemas[0])['@graph'];types=[n['@type'] for n in graph];assert 'Organization' in types and 'Person' in types and 'WebSite' in types
 summary,transcript,faqs=m.parts(s)
 if 'blog-post wrap' not in s:continue
 count+=1;assert summary and len(faqs)==3 and transcript
 article=next(n for n in graph if n['@type']=='BlogPosting');page=next(n for n in graph if n['@type']==['WebPage','FAQPage'])
 assert article['description']==summary
 assert [(q['name'],q['acceptedAnswer']['text']) for q in page['mainEntity']]==faqs
 assert article['headline']==m.grab(s,r'<h1[^>]*>(.*?)</h1>')
 for date in ['datePublished','dateModified']:assert 'datetime="'+article[date]+'"' in s
 assert s.index('id="summary"')<s.index('<iframe')<s.index('class="transcript-text"')<s.index('id="faq"')
 assert 'class="transcript-note"' not in s
 md=p.with_suffix('.md');assert md.exists() and summary in md.read_text()
 assert (R/md.relative_to(base)).read_text()==md.read_text()
assert count==12,count
for f in ['robots.txt','llms.txt','llms-full.txt']:
 t=(base/f).read_text();assert not t.lstrip().startswith('<');assert (R/f).read_text()==t
assert 'Sitemap: https://aicatalyst.biz/sitemap.xml' in (base/'robots.txt').read_text()
llms=(base/'llms.txt').read_text();assert 'ai-training/index.md' in llms and 'fr-ca/blog/' in llms and 'ar/blog/' in llms
assert 'ILDErIfscsk' in (base/'blog/ai-training/index.html').read_text()
print('PASS: 60 entity graphs; 12 answer-first articles with matching FAQ/schema/dates/Markdown; real crawler files and training video.')
