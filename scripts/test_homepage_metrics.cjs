// Run: node scripts/test_homepage_metrics.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const context = vm.createContext({
  window: { location: { pathname: '/' }, addEventListener() {} },
  document: { getElementById() { return null; }, querySelector() { return null; } },
});
vm.runInContext(fs.readFileSync(path.join(__dirname, '../assets/js/main.js'), 'utf8'), context);
const values = (data, date) => context.metricsValues(data, {}, Date.parse(date + 'T00:00:00Z'));
const data = {
  peer_reviewed_works: 38, orcid_peer_reviewed: 36, works_pending_in_orcid: 2,
  peer_reviews: 76, peer_review_journals: 24, last_checked: '2026-10-04',
  orcid_as_of: '2026-10-04', peer_review_as_of: '2026-09-28',
  sources: { scholar: 'unavailable', openalex: 'ok', orcid: 'ok', orcid_peer_reviews: 'unavailable' },
  citation_profiles: {
    scholar: { as_of: '2026-09-07', citations: 388, h_index: 12, i10_index: 12 },
    openalex: { as_of: '2026-10-04', citations: 290, h_index: 10, i10_index: 10 },
  },
};
let result = values(data, '2026-10-04');
assert.equal(result.citations, 388);
assert.equal(result.h_index, 12);
assert.equal(result.i10_index, 12);
assert.equal(result.citation_source_name, 'Google Scholar');
assert.match(result.citation_snapshot_label, /^Saved 7 Sept 2026$/);
assert.equal(result.publication_source_name, 'ORCID + library');
assert.equal(result.peer_review_snapshot_label, 'Saved 28 Sept 2026');

result = values(data, '2026-11-07');
assert.equal(result.citations, 290);
assert.equal(result.h_index, 10);
assert.equal(result.i10_index, 10);
assert.equal(result.citation_source_name, 'OpenAlex');
assert.match(result.citation_source_url, /openalex/);
assert.equal(result.citation_snapshot_label, 'Saved 4 Oct 2026');

const incomplete = structuredClone(data);
delete incomplete.citation_profiles.scholar.h_index;
assert.equal(values(incomplete, '2026-10-04').citation_source_name, 'OpenAlex');
assert.equal(values({ ...data, works_pending_in_orcid: 0 }, '2026-10-04').publication_source_name, 'ORCID');
result = values({}, '2026-10-04');
assert.equal(result.citation_source_name, undefined);
assert.equal(result.citation_snapshot_label, '');
assert.equal(result.metrics_refresh_label, 'Saved figures · refresh unavailable');
console.log('Homepage metrics checks passed: coherent sources, dates, freshness, and offline fallback.');
