#!/usr/bin/env python3
"""Refresh offline HTML using the site's actual JS renderers. Requires Node and bs4.

Run after a library or metrics change; --check checks without writing files.
PDF links and curated publication tags are retained from existing fallback cards.
"""
import argparse
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path
import re
import subprocess

from bs4 import BeautifulSoup
from fetch_metrics import from_library

ROOT = Path(__file__).absolute().parent.parent
BRIDGE = r"""
const fs = require('node:fs'), vm = require('node:vm');
const data = JSON.parse(fs.readFileSync(0, 'utf8'));
const nodes = { 'pubs-list': {}, 'home-publications': {}, 'home-all-publications-link': {} };
const filters = data.filters.map(f => ({ dataset: { filter: f.filter, label: f.label }, textContent: f.label }));
let values = {};
const context = vm.createContext({
  window: { location: { pathname: '/' }, addEventListener() {} },
  document: {
    getElementById(id) { return nodes[id] || null; },
    querySelector() { return null; },
    querySelectorAll(selector) { return selector === '.pub-filter-btn[data-filter]' ? filters : []; }
  }
});
vm.runInContext(fs.readFileSync(data.script, 'utf8'), context);
context.applyMetrics = v => { Object.assign(values, v); };
const fallback = { byDoi: new Map(data.byDoi), byTitle: new Map(data.byTitle) };
context.renderPublicationsPage(data.items, fallback);
context.renderHomePublications(data.items);
Object.assign(values, context.metricsValues(data.stats, context.derivedMetrics(data.items),
  Date.parse(data.stats.last_checked + 'T00:00:00Z')));
process.stdout.write(JSON.stringify({ nodes, values, filters }));
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    originals = {p: p.read_text(encoding='utf-8') for p in ROOT.glob('*.html')}
    pub_path = ROOT / 'publications.html'
    soup = BeautifulSoup(originals[pub_path], 'html.parser')
    by_doi, by_title = [], []
    for card in soup.select('#pubs-list .pub-card'):
        badge = card.select_one('.cite-badge[data-doi]')
        link = card.select_one('a[href*="doi.org"]')
        doi = badge.get('data-doi', '') if badge else ''
        doi = doi or (link['href'] if link else '')
        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi, flags=re.I).lower()
        title = card.select_one('.pub-title').get_text()
        title = re.sub(r'[^a-z0-9]+', ' ', title.lower()).strip()
        meta = {
            'isOpenAccess': 'oa' in card.get('class', []),
            'tags': card.get('data-tags', ''),
            'pdfLinks': [{'href': a['href'], 'label': a.get_text().strip()}
                         for a in card.select('.pub-link.pdf[href]')],
        }
        if doi:
            by_doi.append([doi, meta])
        by_title.append([title, meta])
    filters = [{'filter': b['data-filter'], 'label': re.sub(r'\s*\(\d+\)$', '', b.get_text()).strip()}
               for b in soup.select('.pub-filter-btn')]
    payload = dict(items=json.loads((ROOT / 'OKOs_Library.json').read_text()),
                   stats=json.loads((ROOT / 'assets/data/scholar-stats.json').read_text()),
                   script=str(ROOT / 'assets/js/main.js'), byDoi=by_doi, byTitle=by_title, filters=filters)
    # A library edit must update totals even before the next scheduled API run.
    # Only the local snapshot changes; citation/ORCID observation dates stay intact.
    stats_path = ROOT / 'assets/data/scholar-stats.json'
    original_stats = stats_path.read_text(encoding='utf-8')
    library = from_library()
    stats = payload['stats']
    if any(stats.get(key) != value for key, value in library.items()):
        stats['library_as_of'] = datetime.now(timezone.utc).date().isoformat()
    stats.update(library)
    orcid_count = stats.get('orcid_peer_reviewed', 0)
    stats['peer_reviewed_works'] = max(orcid_count, library['library_peer_reviewed'])
    stats['works_pending_in_orcid'] = max(0, library['library_peer_reviewed'] - orcid_count)
    stats['works_total'] = max(stats.get('works_total', 0), library['library_records'])
    result = subprocess.run(['node', '-e', BRIDGE], input=json.dumps(payload),
                            text=True, capture_output=True, check=True)
    rendered = json.loads(result.stdout)
    updated = dict(originals)
    for name, start, end in [
        ('publications.html', '<div id="pubs-list">', '</div><!-- /pubs-list -->'),
        ('index.html', '<div class="pub-preview-list reveal" id="home-publications">', '</div><!-- /home-publications -->'),
    ]:
        path = ROOT / name
        text = updated[path]
        node_id = 'pubs-list' if name == 'publications.html' else 'home-publications'
        left = text.index(start) + len(start)
        right = text.index(end, left)
        updated[path] = text[:left] + rendered['nodes'][node_id]['innerHTML'] + '\n  ' + text[right:]
    # Preserve surrounding markup; only replace the simple metric text nodes.
    metric = re.compile(r'(<(?P<tag>[a-z][\w-]*)\b[^>]*\bdata-metric="(?P<key>[^"]+)"[^>]*>).*?(</(?P=tag)>)', re.S)
    for path, text in updated.items():
        def replace_metric(match):
            value = rendered['values'].get(match['key'])
            if value is None:
                return match[0]
            return match[1] + escape(str(value)) + match[4]
        def replace_metric_href(match):
            value = rendered['values'].get(match['key'])
            if not value:
                return match[0]
            return re.sub(r'(?<![\w-])href="[^"]*"', lambda _: 'href="' + escape(str(value), quote=True) + '"', match[0])
        text = metric.sub(replace_metric, text)
        text = re.sub(r'<[a-z][\w-]*\b[^>]*\bdata-metric-href="(?P<key>[^"]+)"[^>]*>', replace_metric_href, text)
        updated[path] = re.sub(r'[ \t]+$', '', text, flags=re.M)
    for button in rendered['filters']:
        pattern = r'(<button\b[^>]*data-filter="' + re.escape(button['dataset']['filter']) + r'"[^>]*>)[^<]*'
        updated[pub_path] = re.sub(pattern, lambda m: m[1] + button['textContent'], updated[pub_path])
    home = ROOT / 'index.html'
    updated[home] = re.sub(r'(id="home-all-publications-link">)[^<]*',
                          lambda m: m[1] + rendered['nodes']['home-all-publications-link']['textContent'], updated[home])
    changed = [p for p in originals if originals[p] != updated[p]]
    updated_stats = json.dumps(stats, ensure_ascii=False, indent=2, sort_keys=True) + '\n'
    if original_stats != updated_stats:
        changed.append(stats_path)
        updated[stats_path] = updated_stats
    if args.check and changed:
        raise SystemExit('Stale fallback HTML: ' + ', '.join(p.name for p in changed))
    for path in changed:
        path.write_text(updated[path], encoding='utf-8')
        print('Refreshed', path.name)
    print(f"Verified {len(payload['items'])} publication fallback records.")


if __name__ == '__main__':
    main()
