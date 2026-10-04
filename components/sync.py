"""Keep the nine V3 pages on the same header and footer. Run after fragment edits."""
from pathlib import Path
import re

SITE = Path(__file__).resolve().parents[1]
PAGES = ['index', 'platform', 'creator-social', 'online-conversion',
         'marketing-investment', 'solutions', 'company', 'training', 'briefing']
header = (SITE / 'components/site-header.html').read_text().strip()
footer = (SITE / 'components/site-footer.html').read_text().strip()
for slug in PAGES:
    path = SITE / f'{slug}.html'
    text = path.read_text()
    text, headers = re.subn(r'<header class="masthead".*?</header>', lambda m: header, text, flags=re.S)
    text, footers = re.subn(r'<footer class="site-footer(?: site-footer--shared)?">.*?</footer>', lambda m: footer, text, flags=re.S)
    assert headers == footers == 1, (slug, headers, footers)
    if 'client-layout-v3.css' not in text:
        text = text.replace('</head>', '<link rel="stylesheet" href="client-layout-v3.css?v=20261003-shared1">\n</head>')
    text = re.sub(r'site-shell\.js\?v=[^"\s]+', 'site-shell.js?v=20261003-shared1', text)
    path.write_text(text)
print('Synced one header and one bridge footer across all nine V3 pages.')
