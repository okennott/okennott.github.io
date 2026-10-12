#!/usr/bin/env python3
"""Check static page links, IDs and bibliography coverage without external APIs."""
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
from bs4 import BeautifulSoup
from fetch_metrics import from_library

root = Path(__file__).absolute().parent.parent
errors = []
for path in root.glob('*.html'):
    soup = BeautifulSoup(path.read_text(), 'html.parser')
    ids = [tag['id'] for tag in soup.select('[id]')]
    if len(ids) != len(set(ids)):
        errors.append(f'{path.name}: duplicate IDs')
    for tag in soup.select('[href], [src]'):
        for attr in ('href', 'src'):
            value = tag.get(attr, '')
            url = urlsplit(value)
            if not value or url.scheme or url.netloc:
                continue
            target = path.parent / unquote(url.path) if url.path else path
            if not target.exists():
                errors.append(f'{path.name}: missing {value}')
            elif url.fragment and target.suffix == '.html':
                target_soup = soup if target == path else BeautifulSoup(target.read_text(), 'html.parser')
                if not target_soup.find(id=unquote(url.fragment)):
                    errors.append(f'{path.name}: unresolved {value}')
    toggle = soup.select_one('#nav-toggle')
    if toggle and not soup.find(id=toggle.get('aria-controls')):
        errors.append(f'{path.name}: navigation controls target missing')

items = json.loads((root / 'OKOs_Library.json').read_text())
soup = BeautifulSoup((root / 'publications.html').read_text(), 'html.parser')
cards = soup.select('#pubs-list .pub-card')
if len(cards) != len(items):
    errors.append('Publication fallback count differs from the library')
dois = [item.get('DOI', '').lower().removeprefix('https://doi.org/') for item in items if item.get('DOI')]
if len(dois) != len(set(dois)):
    errors.append('Duplicate library DOI')
if {card.get('data-doi', '').lower() for card in cards} - {''} != set(dois):
    errors.append('Publication fallback DOIs differ from the library')
stats = json.loads((root / 'assets/data/scholar-stats.json').read_text())
for key, value in from_library().items():
    if stats.get(key) != value:
        errors.append(f'Metrics disagree with library: {key}')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'Checked local links, fragments, IDs and {len(cards)} publication cards.')
