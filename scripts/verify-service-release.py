"""Verify production source and delivered bytes over HTTP, without browser control."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
RELEASE = sys.argv[1]
PAGES = ['index.html', 'creator-social.html', 'online-conversion.html', 'marketing-investment.html', 'platform.html', 'training.html', 'solutions.html', 'company.html', 'briefing.html', 'case-studies/index.html', 'case-studies/analucia-sofia/index.html']
ASSETS = ['service-suite.css', 'footer-refinement.css', 'site-system.css', 'halftone-rendering.js', 'platform-motion.js', 'quality-motion.js', 'service-films.js', 'engine-film-modal.js', 'assets/video-posters/mmm-preview-20261030.jpg', 'assets/video-posters/agentic-live-selling-preview-20261030.jpg', 'assets/logo.svg', 'images/delivery-v1/bridge-halftone-2619ec40e2c1.webp']


def fetch(name):
    route = '/' if name == 'index.html' else '/' + name.replace('/index.html', '/')
    if name.endswith('.html') and '/index.html' not in name and name != 'index.html':
        route = route[:-5]
    request = urllib.request.Request('https://aicatalyst.biz' + route + '?release=' + RELEASE, headers={'Cache-Control': 'no-cache', 'User-Agent': 'AI-Catalyst-release-verification'})
    with urllib.request.urlopen(request, timeout=30) as response:
        data, status = response.read(), response.status
    if name in PAGES:
        source = data.decode()
        assert 'footer-refinement.css?v=20261030-footer2' in source, name
        assert 'data-art-print="0.20"' in source, name
        assert 'agentic consumer intelligence' not in source.lower(), name
        if name in ['creator-social.html', 'online-conversion.html', 'marketing-investment.html']:
            assert 'service-suite.css?v=20261030-clean1' in source and 'question-stack' in source and 'benefit-grid' in source, name
        if name == 'marketing-investment.html':
            assert 'mmm-preview-20261030.jpg' in source and 'coverage-proof' in source, name
        if name == 'platform.html':
            assert 'mmm-preview-20261030.jpg' in source and 'agentic-live-selling-preview-20261030.jpg' in source, name
            assert 'Dvc4KLY2ma4' in source and 'VMMg0PrHeC4' in source, name
        if name == 'index.html':
            assert source.count('class="engine-film-link"') == 3, name
            assert all('id="' + marker + '"' in source for marker in ['signals', 'allocation', 'chat-scene']), name
        return {'path': route, 'status': status, 'contentChecks': 'pass'}
    assert data == (ROOT / 'current-site' / name).read_bytes(), name + ': live bytes differ'
    return {'path': route, 'status': status, 'sha256': hashlib.sha256(data).hexdigest(), 'exactBytes': 'pass'}


with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    checks = list(pool.map(fetch, PAGES + ASSETS))
report = {'deployment': RELEASE, 'baseUrl': 'https://aicatalyst.biz', 'checks': checks, 'renderedVisualReview': False, 'browserControlUsed': False}
(ROOT / 'docs/service-cleanup-2026-10-30/live-verification.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'deployment': RELEASE, 'pages': len(PAGES), 'exactAssets': len(ASSETS), 'result': 'pass', 'renderedVisualReview': False}))
