const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

function setup(dois) {
  const badges = dois.map(doi => ({ dataset: { doi }, style: { display: 'none' },
    textContent: '', classList: { add() {} } }));
  const context = vm.createContext({
    window: { location: { pathname: '/' }, addEventListener() {} },
    document: { getElementById() { return null; }, querySelector() { return null; },
      querySelectorAll() { return badges; } },
    AbortSignal,
  });
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../assets/js/main.js'), 'utf8'), context);
  return { context, badges };
}

async function main() {
  const { context, badges } = setup(['10.test/A', 'https://doi.org/10.test/a', '10.test/b', '10.test/c']);
  let fallbackCalls = 0;
  context.fetchCitationsFromOpenAlex = async dois => {
    assert.deepEqual(Array.from(dois), ['10.test/a', '10.test/b', '10.test/c']);
    return new Map([['10.test/a', { citations: 12 }], ['10.test/b', { citations: 0 }]]);
  };
  context.fetchCitationsFromSemanticScholar = async dois => {
    fallbackCalls++;
    assert.deepEqual(Array.from(dois), ['10.test/c']);
    return new Map([['10.test/c', { citations: 7 }]]);
  };
  await context.hydrateCitationBadges();
  assert.equal(fallbackCalls, 1);
  assert.deepEqual(badges.map(b => b.textContent), ['12 cit.', '12 cit.', '', '7 cit.']);
  assert.equal(badges[2].style.display, 'none');

  const zero = setup(['10.test/zero']);
  zero.context.fetchCitationsFromOpenAlex = async () => new Map([['10.test/zero', { citations: 0 }]]);
  zero.context.fetchCitationsFromSemanticScholar = async () => assert.fail('Zero is not a failed lookup');
  await zero.context.hydrateCitationBadges();
  assert.equal(zero.badges[0].style.display, 'none');

  const outage = setup(['10.test/a']);
  outage.context.fetchCitationsFromOpenAlex = async () => { throw new Error('OpenAlex 429'); };
  outage.context.fetchCitationsFromSemanticScholar = async () => new Map([['10.test/a', { citations: 4 }]]);
  await outage.context.hydrateCitationBadges();
  assert.equal(outage.badges[0].textContent, '4 cit.');
  outage.badges[0].style.display = 'none';
  outage.context.fetchCitationsFromSemanticScholar = async () => { throw new Error('Offline'); };
  await assert.doesNotReject(outage.context.hydrateCitationBadges());
  assert.equal(outage.badges[0].style.display, 'none');

  const invalid = setup(['10.test/a']);
  invalid.context.fetchCitationsFromOpenAlex = async () => new Map([['10.test/a', { citations: NaN }]]);
  invalid.context.fetchCitationsFromSemanticScholar = async () => new Map([['10.test/a', { citations: 5 }]]);
  await invalid.context.hydrateCitationBadges();
  assert.equal(invalid.badges[0].textContent, '5 cit.');

  // Exercise the actual provider adapters, including batch boundaries and DOI matching.
  const api = setup([]).context;
  const calls = [];
  api.fetch = async (url, options) => {
    calls.push({ url, options });
    if (url.includes('openalex')) return { ok: true, json: async () => ({ results: [
      { doi: 'https://doi.org/10.TEST/A', cited_by_count: 0, open_access: { is_oa: true } },
    ] }) };
    return { ok: true, json: async () => [null, { citationCount: 8, externalIds: {} }] };
  };
  const dois = Array.from({ length: 46 }, (_, i) => `10.test/${i}`);
  let found = await api.fetchCitationsFromOpenAlex(dois);
  assert.equal(calls.length, 2);
  assert.ok(calls.every(c => new URL(c.url).searchParams.get('filter').startsWith('doi:')));
  assert.equal(found.get('10.test/a').citations, 0);
  found = await api.fetchCitationsFromSemanticScholar(['10.test/a', '10.test/b']);
  assert.equal(found.has('10.test/a'), false);
  assert.equal(found.get('10.test/b').citations, 8);
  assert.deepEqual(JSON.parse(calls[2].options.body), { ids: ['DOI:10.test/a', 'DOI:10.test/b'] });
  console.log('Citation checks passed: batching, partial fallback, zero counts, invalid data and provider outages.');
}
main().catch(error => { console.error(error); process.exitCode = 1; });
