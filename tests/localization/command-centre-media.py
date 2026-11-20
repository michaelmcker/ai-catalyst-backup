#!/usr/bin/env python3
"""Guard the platform's visible graphics and single overview film in every edition."""
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.stack = []
        self.nodes = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'parents': self.stack.copy()}
        self.nodes.append(node)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr', 'path', 'circle', 'rect', 'image', 'mpath'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                self.stack = self.stack[:i]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

for prefix in ['', 'fr-ca/', 'fr-fr/', 'ar/']:
    source = (ROOT / 'current-site' / prefix / 'platform.html').read_text()
    doc = Document(source)
    for graphic in ['chat-scene', 'signals', 'allocation']:
        matches = [n for n in doc.nodes if n['attrs'].get('id') == graphic]
        assert len(matches) == 1, (prefix, graphic)
        assert all('hidden' not in n['attrs'] and n['attrs'].get('aria-hidden') != 'true'
                   for n in matches[0]['parents'] + matches), (prefix, graphic, 'hidden graphic')
    films = [n for n in doc.nodes if n['attrs'].get('data-youtube-id')]
    assert len(films) == 1 and films[0]['attrs']['data-youtube-id'] == 'NkQtLriHVbA', prefix
    assert any('command-introduction' in p['attrs'].get('class', '').split() for p in films[0]['parents']), prefix
    assert films[0]['attrs'].get('aria-label') and films[0]['attrs'].get('data-video-title'), prefix
    assert not any(n['tag'] == 'iframe' for n in doc.nodes), 'Player must load on demand'
    poster = [n for n in doc.nodes if n['tag'] == 'img' and 'command-centre-overview-' in n['attrs'].get('src', '')]
    assert len(poster) == 1 and poster[0]['attrs'].get('loading') == 'lazy', prefix
    assert poster[0]['attrs'].get('width') == '1280' and poster[0]['attrs'].get('height') == '720', prefix
    for route in ['marketing-investment.html', 'online-conversion.html']:
        assert 'data-youtube-id=' in (ROOT / 'current-site' / prefix / route).read_text(), route
    home = (ROOT / 'current-site' / prefix / 'index.html').read_text()
    assert all(f'id="{name}"' in home for name in ['signals', 'allocation', 'chat-scene']), prefix
print('PASS: four platform editions retain visible original graphics, one on-demand overview and service/home media.')
