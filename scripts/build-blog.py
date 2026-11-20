#!/usr/bin/env python3
"""Render blog source templates from content/blog/posts.json; then run localization."""
from pathlib import Path
import json,re,html,argparse
R=Path(__file__).resolve().parents[1]
posts=json.loads((R/'content/blog/posts.json').read_text())
base=(R/'templates/i18n/case-studies/index.html').read_text()
base=re.sub(r'<main\b.*?</main>','BLOG_MAIN',base,flags=re.S)
base=base.replace('<title>Case studies | AI Catalyst</title>','<title>BLOG_TITLE | AI Catalyst</title>').replace('Explore AI Catalyst’s work and watch the case-study films.','BLOG_DESCRIPTION')
base=base.replace('</head>','<link rel="stylesheet" href="/blog.css?v=20261119-aeo1"></head>')
base=re.sub(r'<link rel="canonical"[^>]*>','',base)
intro='Practical conversations with Randy Weyersberg on marketing investment, measurement and agentic commerce.'
main='<main class="blog wrap" id="main"><h1>Coffee Chats with Randy</h1><p class="blog-intro">'+intro+'</p><div class="blog-list">'
for p in posts:
 main+=f'<article><a class="coffee-cover" href="/blog/{p["slug"]}/"><img src="{p["thumbnail"]}" alt="{p["thumbnailAlt"]}" width="1280" height="720" loading="lazy" decoding="async"></a><h2><a href="/blog/{p["slug"]}/">{p["title"]}</a></h2><p>{p["summary"]}</p><a class="blog-link" href="/blog/{p["slug"]}/">Watch and read</a></article>'
main+='</div></main>'
folder=R/'templates/i18n/blog';folder.mkdir(parents=True,exist_ok=True)
outputs={'blog/index.html': base.replace('BLOG_MAIN',main).replace('BLOG_TITLE','Coffee Chats with Randy').replace('BLOG_DESCRIPTION',intro)}
for p in posts:
 faq=''.join('<section class="faq-item"><h3>'+html.escape(f['question'])+'</h3><p>'+html.escape(f['answer'])+'</p></section>' for f in p['faq'])
 main=f'''<main class="blog blog-post wrap" id="main"><a class="blog-back" href="/blog/">Back to Coffee Chats</a><header class="blog-heading"><h1>{p['title']}</h1><section class="blog-summary" id="summary"><h2>Summary</h2><p>{html.escape(p['takeaway'])}</p></section><p class="blog-byline">Randy Weyersberg · AI Catalyst</p><p class="blog-dates"><span>Published</span> <time datetime="{p['published']}">{p['published']}</time> · <span>Updated</span> <time datetime="{p['modified']}">{p['modified']}</time></p></header><div class="blog-video"><iframe src="https://www.youtube-nocookie.com/embed/{p['video']}" title="{p['title']}" loading="lazy" allow="accelerometer; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe></div><p><a href="https://www.youtube.com/watch?v={p['video']}" target="_blank" rel="noopener">Watch on YouTube</a></p><section class="blog-transcript" aria-labelledby="transcript-title"><h2 id="transcript-title">Transcript</h2><div class="transcript-text">{html.escape(p['text'])}</div></section><section class="blog-faq" id="faq"><h2>Frequently asked questions</h2>{faq}</section><p class="blog-cta"><a href="/briefing.html">Start a conversation</a></p></main>'''
 (folder/p['slug']).mkdir(exist_ok=True)
 outputs['blog/'+p['slug']+'/index.html']=base.replace('BLOG_MAIN',main).replace('BLOG_TITLE',p['title']).replace('BLOG_DESCRIPTION',p['summary'])

parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
for name,source in outputs.items():
 p=R/'templates/i18n'/name
 if args.check:assert p.read_text()==source,'Stale blog source: '+name
 else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source)
print(f'{len(outputs)} Coffee Chat source templates checked.' if args.check else f'Built {len(outputs)} Coffee Chat source templates.')
