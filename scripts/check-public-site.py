"""Check the approved public contact routes and shared navigation."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1] / 'current-site'
EMAIL = 'mailto:randy@aicatalyst.biz'
PHONE = 'tel:+14162700132'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.refs = []
        self.current = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a':
            self.current = {'href': attrs.get('href', ''), 'text': ''}
            self.links.append(self.current)
        for key in ('href', 'src', 'poster'):
            if attrs.get(key):
                self.refs.append(attrs[key])
    def handle_endtag(self, tag):
        if tag == 'a':
            self.current = None
    def handle_data(self, data):
        if self.current is not None:
            self.current['text'] += data

failures = []
pages = sorted(ROOT.glob('*.html'))
assert len(pages) == 9
for page in pages:
    source = page.read_text()
    doc = Links()
    doc.feed(source)
    if re.search(r'linkedin|catalyst\s*retail\s*solutions', source, re.I):
        failures.append(f'{page.name}: retired contact route remains')
    if EMAIL not in [a['href'] for a in doc.links] or PHONE not in [a['href'] for a in doc.links]:
        failures.append(f'{page.name}: missing email or phone')
    footer = re.search(r'<nav aria-label="Connect">(.*?)</nav>', source, re.S)
    if not footer or EMAIL not in footer[1] or PHONE not in footer[1] or 'Toronto, Canada' not in source:
        failures.append(f'{page.name}: footer contact details incomplete')
    menu = re.search(r'<nav aria-label="Expanded navigation">(.*?)</nav>', source, re.S)
    menu_doc = Links()
    menu_doc.feed(menu[1] if menu else '')
    routes = [a['href'] for a in menu_doc.links]
    if 'solutions.html' not in routes or routes[routes.index('solutions.html') + 1:][:1] != ['training.html']:
        failures.append(f'{page.name}: Training must follow How We Work')
    if sum(a['text'].strip() == 'Training and adoption' for a in menu_doc.links) != 1:
        failures.append(f'{page.name}: Training menu label/count differs')
    for ref in doc.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc or not url.path:
            continue
        target = ROOT / unquote(url.path).lstrip('/') if url.path.startswith('/') else page.parent / unquote(url.path)
        if not target.exists():
            failures.append(f'{page.name}: missing {ref}')
for script in ROOT.glob('*.js'):
    if re.search(r'linkedin|catalyst\s*retail\s*solutions', script.read_text(), re.I):
        failures.append(f'{script.name}: retired contact fallback remains')
    if subprocess.run(['node', '--check', str(script)], capture_output=True).returncode:
        failures.append(f'{script.name}: JavaScript syntax error')
if failures:
    raise SystemExit('\n'.join(failures))
print(f'PASS: {len(pages)} pages; email/phone, footer, menu order, retired links, local references and JavaScript syntax.')
