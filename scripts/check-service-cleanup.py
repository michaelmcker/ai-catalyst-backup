"""Static layout/content invariants; this is not rendered viewport proof."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'current-site'
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.stack = []
        self.elements = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        node = {'tag': tag, 'attrs': dict(attrs), 'parents': self.stack.copy(), 'text': ''}
        self.elements.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                self.stack = self.stack[:index]
                break

    def handle_data(self, data):
        for node in self.stack:
            node['text'] += data

    def select(self, name):
        return [n for n in self.elements if name in n['attrs'].get('class', '').split()]


for name, count in [('creator-social.html', 3), ('online-conversion.html', 3), ('marketing-investment.html', 4)]:
    source = (PUBLIC / name).read_text()
    doc = Document(source)
    previous = Document(subprocess.check_output(['git', 'show', f'3e9cf9c:current-site/{name}'], cwd=ROOT, text=True))
    opening, = doc.select('art-opening')
    inside = [n for n in doc.elements if opening in n['parents'] and n['tag'] == 'section']
    assert len(inside) == 1 and 'page-hero' in inside[0]['attrs']['class'], name + ': hero field leaks into body'
    cards = doc.select('question-card')
    old_list, = previous.select('commercial-questions')
    old_questions = [n['text'] for n in previous.elements if n['tag'] == 'li' and old_list in n['parents']]
    assert len(cards) == count and [n['text'] for n in cards] == old_questions, name + ': questions changed'
    assert len(doc.select('benefit-card')) == 3, name + ': missing benefit cards'
    assert [n['text'] for n in doc.select('quality-detail-row')] == [n['text'] for n in previous.select('quality-detail-row')], name + ': benefits changed'
    ids = [n['attrs']['id'] for n in doc.elements if 'id' in n['attrs']]
    assert len(ids) == len(set(ids)), name + ': duplicate IDs'
    assert 'service-suite.css?v=20261030-clean1' in source
    if name == 'marketing-investment.html':
        proof, = doc.select('coverage-proof')
        allocation, = [n for n in doc.elements if n['attrs'].get('id') == 'allocation']
        assert proof in allocation['parents'] and proof['attrs']['id'] == 'measurement'
        assert 'mmm-preview-20261030.jpg' in source

for page in PUBLIC.rglob('*.html'):
    doc = Document(page.read_text())
    footer, = doc.select('footer-art')
    assert footer['attrs']['data-art-print'] == '0.20', str(page)
    assert any(n['attrs'].get('data-deferred-src', '').endswith('bridge-halftone-2619ec40e2c1.webp') for n in doc.elements if footer in n['parents'])
    assert page.read_bytes() == (ROOT / page.relative_to(PUBLIC)).read_bytes(), str(page) + ': mirror differs'

for name in ['service-suite.css', 'footer-refinement.css', 'assets/video-posters/mmm-preview-20261030.jpg']:
    assert (PUBLIC / name).read_bytes() == (ROOT / name).read_bytes(), name + ': mirror differs'
css = (PUBLIC / 'service-suite.css').read_text()
assert '.service-suite .service-film{max-width:880px;' in css
assert '@media(max-width:800px)' in css and 'grid-template-columns:minmax(0,1fr);gap:28px' in css
footer_css = (PUBLIC / 'footer-refinement.css').read_text()
assert 'max-width:none;height:clamp(240px,29vw,450px);margin:0!important' in footer_css
assert 'object-position:0% 48%' in footer_css
home = Document((PUBLIC / 'index.html').read_text())
prior_home = Document(subprocess.check_output(['git', 'show', '3e9cf9c:current-site/index.html'], cwd=ROOT, text=True))
assert [n['text'] for n in home.select('solution-card')] == [n['text'] for n in prior_home.select('solution-card')]
for name in ['halftone-rendering.js', 'platform-motion.js', 'quality-motion.js', 'service-films.js']:
    assert (PUBLIC / name).read_bytes() == subprocess.check_output(['git', 'show', f'3e9cf9c:current-site/{name}'], cwd=ROOT), name + ': renderer or interaction changed'
print('PASS: hero-only dither boundary, original questions/benefits, three card sections, retained MMM graphic, smaller film, footer profile/alignment, mirrors and unchanged motion scripts. Rendered layout not verified.')
