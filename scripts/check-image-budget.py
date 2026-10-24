"""Public portrait hero delivery must use small responsive variants."""
from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1] / 'current-site'
class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
    def handle_starttag(self, tag, attrs):
        if tag == 'img': self.images.append(dict(attrs))

failures = []
for name in ['index', 'company', 'solutions', 'briefing']:
    doc = Images()
    doc.feed((ROOT/(name+'.html')).read_text())
    hero = next(image for image in doc.images if image.get('src', '').startswith('images/'))
    if not hero.get('srcset'):
        failures.append(name + ': no responsive hero variants')
        continue
    mobile = hero['srcset'].split(',')[0].strip().split(' ')[0]
    if (ROOT/mobile).stat().st_size > 100_000:
        failures.append(name + ': mobile hero exceeds 100 KB')
    if (ROOT/hero['src']).stat().st_size > 300_000:
        failures.append(name + ': desktop hero exceeds 300 KB')
source = (ROOT/'index.html').read_text()
if '<image href="images/ai-catalyst/' in source:
    failures.append('home: lower-page product images still load eagerly')
if failures:
    sys.exit('\n'.join('FAIL: ' + message for message in failures))
print('PASS: responsive hero budgets and deferred product images.')
