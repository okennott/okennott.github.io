const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const list = {};
const context = vm.createContext({
  window: { location: { pathname: '/', hash: '#%E0%A4%A' }, addEventListener() {} },
  document: {
    getElementById(id) { return id === 'pubs-list' ? list : null; },
    querySelector() { return null; }, querySelectorAll() { return []; }
  }
});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../assets/js/main.js'), 'utf8'), context);
const items = JSON.parse(fs.readFileSync(path.join(__dirname, '../OKOs_Library.json')));
const doi = '10.1016/j.ympev.2026.108749';
const paper = items.find(p => context.cleanDoi(p.DOI) === doi);
assert.ok(paper);
assert.equal(paper.author.length, 12);
assert.equal(paper.author[2].family, 'Onditi');
assert.equal(items.filter(p => context.cleanDoi(p.DOI) === doi).length, 1);
assert.equal(paper.volume, '226');
assert.deepEqual(paper.issued['date-parts'][0], [2027, 1]);
assert.deepEqual(paper['available-date']['date-parts'][0], [2026, 10, 10]);
assert.equal(context.isOpenAccess(paper, {}), false);
assert.equal(context.isOpenAccess(paper, { isOpenAccess: true }), false);
const openPaper = items.find(p => context.cleanDoi(p.DOI) === '10.3897/vz.76.e188776');
assert.equal(context.isOpenAccess(openPaper, {}), true);
assert.equal(context.isOpenAccess(openPaper, { isOpenAccess: false }), true);
assert.match(context.formatTitle(paper.title), /<em>Nectogale<\/em>/);
assert.equal(context.acceptedInfo({ DOI: doi, note: 'status: accepted' }), null);
assert.doesNotThrow(() => context.focusHashTarget());
const examples = [paper, { type: 'article-journal', title: 'Working paper', 'container-title': 'SSRN' },
  { type: 'article-journal', title: 'Correction: An earlier paper' }];
assert.equal(context.derivedMetrics(examples).library_peer_reviewed, 1);
assert.equal(context.derivedMetrics(examples).library_preprints, 1);
context.renderPublicationsPage(examples, { byDoi: new Map(), byTitle: new Map() });
assert.match(list.innerHTML, /id="p-10-1016-j-ympev-2026-108749"/);
assert.match(list.innerHTML, /data-tags="correction"/);
assert.doesNotMatch(list.innerHTML, /Access unverified/);
assert.match(list.innerHTML, /https:\/\/pubmed\.ncbi\.nlm\.nih\.gov\/42858910\//);
assert.match(list.innerHTML, /Read the abstract on/);
assert.match(list.innerHTML, /Online 10 Oct 2026/);
assert.match(list.innerHTML, /Subscription · author copy available/);
assert.match(list.innerHTML, /href="contact.html" class="pub-link author-copy-request"/);
// The copy request is also visible on the card, beside the abstract toggle.
assert.match(list.innerHTML, /<a href="contact.html" class="pub-action"[^>]*>Request copy<\/a>/);
context.renderPublicationsPage([paper], {
  byDoi: new Map([[doi, { isOpenAccess: false, pdfLinks: [{ href: 'pdfs/Pei_2026.pdf', label: 'PDF' }] }]]), byTitle: new Map()
});
assert.match(list.innerHTML, /<a href="pdfs\/Pei_2026.pdf" class="pub-action"[^>]*>PDF ↓<\/a>/);
assert.doesNotMatch(list.innerHTML, /Request copy/);
// Homepage highlights: flagged records first, never preprints or corrections.
const pick = (title, y, extra = {}) => ({ type: 'article-journal', title, issued: { 'date-parts': [[y]] }, ...extra });
const titles = context.homeHighlights([
  pick('Old favourite', 2019, { highlight: true }), pick('Newest preprint', 2026, { type: 'preprint' }),
  pick('Correction: Something', 2026), pick('Recent A', 2025), pick('Recent B', 2024), pick('Recent C', 2023),
  pick('Older', 2020),
]).map(p => p.item.title);
assert.deepEqual(titles, ['Old favourite', 'Recent A', 'Recent B', 'Recent C']);
// Library access decisions also override stale static card metadata and filter tags.
context.renderPublicationsPage([paper, openPaper], {
  byDoi: new Map([[doi, { isOpenAccess: true, tags: 'oa' }]]), byTitle: new Map()
});
assert.match(list.innerHTML, /class="pub-card restricted"[^>]+data-tags="systematics peer-reviewed"[^>]+data-doi="10\.1016\/j\.ympev\.2026\.108749"/);
assert.match(list.innerHTML, /class="pub-card oa"[^>]+data-tags="[^"]*oa[^"]*"[^>]+data-doi="10\.3897\/vz\.76\.e188776"/);
assert.ok(context.newsItemsFromPublications(items).some(p => p.href.endsWith(context.doiSlug(doi))));
context.renderPublicationsPage([paper,
  { type: 'article-journal', title: 'Accepted work', note: 'status: accepted; accepted: 2026-06-01', issued: { 'date-parts': [[2026]] } },
  { type: 'article-journal', title: 'Published work', issued: { 'date-parts': [[2026]] } },
], { byDoi: new Map(), byTitle: new Map() });
assert.ok(list.innerHTML.indexOf('id="year-in-press"') < list.innerHTML.indexOf('id="year-2027"'));
assert.ok(list.innerHTML.indexOf('id="year-2027"') < list.innerHTML.indexOf('id="year-2026"'));
console.log('Publication checks passed: metadata, classification, access status and stable links.');
