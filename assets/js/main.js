/* ═══════════════════════════════════════════════════════
   SHARED JS — K.O. Onditi Academic Website
   ═══════════════════════════════════════════════════════ */

/* ─── NAV ACTIVE STATE ─── */
(function() {
  const path = window.location.pathname;
  const page = path.split('/').pop().replace('.html','') || 'index';
  const map = {
    'index':        'nav-home',
    '':             'nav-home',
    'research':     'nav-research',
    'publications': 'nav-pubs',
    'fieldwork':    'nav-field',
    'cv':           'nav-cv',
    'contact':      'nav-contact'
  };
  const id = map[page];
  if (id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('active');
  }
})();

/* ─── HAMBURGER MENU ─── */
const toggle = document.getElementById('nav-toggle');
const navLinks = document.querySelector('.nav-links');
if (toggle && navLinks) {
  toggle.addEventListener('click', () => {
    navLinks.classList.toggle('open');
    const spans = toggle.querySelectorAll('span');
    if (navLinks.classList.contains('open')) {
      spans[0].style.transform = 'rotate(45deg) translateY(6px)';
      spans[1].style.opacity = '0';
      spans[2].style.transform = 'rotate(-45deg) translateY(-6px)';
    } else {
      spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    }
  });
  // Close on nav link click
  navLinks.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      navLinks.classList.remove('open');
      const spans = toggle.querySelectorAll('span');
      spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
    });
  });
}

/* ─── REVEAL ON SCROLL ─── */
function initReveal() {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.classList.add('visible');
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('.reveal, .reveal-stagger').forEach(el => {
    io.observe(el);
  });
}

window.addEventListener('DOMContentLoaded', () => {
  initReveal();
});

/* ─── CITATION FETCHER ───────────────────────────────────────────────
   One batched request for every DOI on the page instead of one request per
   paper. The old per-paper approach fired ~40 parallel calls at Semantic
   Scholar on every page load, which reliably tripped its anonymous rate limit
   (HTTP 429) and left most badges blank. OpenAlex answers the whole set in a
   single call, has no anonymous rate limit, and returns open-access status in
   the same payload. Semantic Scholar stays as a batched fallback.
   ------------------------------------------------------------------- */
const OPENALEX_MAILTO = 'kenotieno08@gmail.com';   // polite pool: faster, higher limits
const OPENALEX_BATCH  = 45;                        // OpenAlex caps an OR filter at 50

function chunk(list, size) {
  const out = [];
  for (let i = 0; i < list.length; i += size) out.push(list.slice(i, i + size));
  return out;
}

async function fetchCitationsFromOpenAlex(dois) {
  const found = new Map();
  await Promise.all(chunk(dois, OPENALEX_BATCH).map(async group => {
    const url = 'https://api.openalex.org/works'
      + `?filter=doi:${group.map(encodeURIComponent).join('|')}`
      + '&per-page=' + OPENALEX_BATCH
      + '&select=doi,cited_by_count,open_access'
      + `&mailto=${OPENALEX_MAILTO}`;
    const res = await fetch(url, { signal: AbortSignal.timeout(10000) });
    if (!res.ok) throw new Error('OpenAlex ' + res.status);
    const data = await res.json();
    (data.results || []).forEach(work => {
      const doi = cleanDoi(work.doi).toLowerCase();
      if (!doi) return;
      found.set(doi, {
        citations: work.cited_by_count,
        isOpenAccess: work.open_access?.is_oa === true,
        oaStatus: work.open_access?.oa_status || ''
      });
    });
  }));
  return found;
}

async function fetchCitationsFromSemanticScholar(dois) {
  const found = new Map();
  await Promise.all(chunk(dois, 100).map(async group => {
    const res = await fetch(
      'https://api.semanticscholar.org/graph/v1/paper/batch?fields=citationCount,externalIds',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ids: group.map(d => 'DOI:' + d) }),
        signal: AbortSignal.timeout(12000)
      }
    );
    if (!res.ok) throw new Error('Semantic Scholar ' + res.status);
    const data = await res.json();
    (data || []).forEach((paper, index) => {
      if (!paper || typeof paper.citationCount !== 'number') return;
      const doi = cleanDoi(paper.externalIds?.DOI || group[index]).toLowerCase();
      if (doi) found.set(doi, { citations: paper.citationCount });
    });
  }));
  return found;
}

function applyCitationCounts(found) {
  let shown = 0;
  document.querySelectorAll('.cite-badge[data-doi]').forEach(el => {
    const hit = found.get(cleanDoi(el.dataset.doi).toLowerCase());
    if (!hit || typeof hit.citations !== 'number') return;
    // A brand-new paper legitimately has 0 citations; showing "0 cit." is noise.
    if (hit.citations < 1) return;
    el.textContent = `${hit.citations} cit.`;
    el.style.display = 'inline-flex';
    el.classList.add('loaded');
    shown++;
  });
  return shown;
}

async function hydrateCitationBadges(root = document) {
  const badges = [...root.querySelectorAll('.cite-badge[data-doi]')];
  const dois = [...new Set(
    badges.map(el => cleanDoi(el.dataset.doi)).filter(Boolean)
  )];
  if (!dois.length) return;

  for (const source of [fetchCitationsFromOpenAlex, fetchCitationsFromSemanticScholar]) {
    try {
      const found = await source(dois);
      if (applyCitationCounts(found) > 0) return;
    } catch (e) { /* try the next source */ }
  }
  // Both sources unavailable: badges stay hidden rather than showing a stale 0.
}

/* ─── ABSTRACT FETCHER (CrossRef) ─── */
async function fetchAbstract(doi, elementId) {
  if (!doi || !elementId) return;
  const el = document.getElementById(elementId);
  if (!el) return;
  // Only fetch if marked as needing fetch
  if (!el.dataset.fetch) return;
  try {
    const res = await fetch(
      `https://api.crossref.org/works/${encodeURIComponent(doi)}`,
      { signal: AbortSignal.timeout(8000) }
    );
    if (!res.ok) return;
    const data = await res.json();
    const abstract = data.message?.abstract;
    if (abstract) {
      // Strip JATS XML tags
      const clean = abstract.replace(/<[^>]+>/g, '').trim();
      if (clean.length > 40) {
        el.innerHTML = `<p>${clean}</p>`;
        el.removeAttribute('data-fetch');
      }
    }
  } catch(e) { /* fail silently */ }
}

/* ─── PUBLICATIONS DATA SOURCE (Zotero CSL JSON) ─── */
const PUBLICATIONS_DATA_URL = 'OKOs_Library.json';

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function cleanDoi(value) {
  if (!value) return '';
  return String(value)
    .trim()
    .replace(/^https?:\/\/(dx\.)?doi\.org\//i, '')
    .replace(/^https?:\/doi\.org\//i, '')
    .replace(/^doi:\s*/i, '')
    .trim();
}

function normalizeTitle(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/<[^>]+>/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function publicationYear(item) {
  return Number(item?.issued?.['date-parts']?.[0]?.[0]) || 0;
}

function dateSortKey(item, index) {
  const parts = item?.issued?.['date-parts']?.[0] || [];
  const y = Number(parts[0]) || 0;
  const m = Number(parts[1]) || 0;
  const d = Number(parts[2]) || 0;
  return y * 100000000 + m * 1000000 + d * 10000 - index;
}

function authorInitials(given) {
  if (!given) return '';
  return String(given)
    .replace(/\./g, '')
    .split(/[\s-]+/)
    .filter(Boolean)
    .map(part => part[0]?.toUpperCase() + '.')
    .join(' ');
}

function formatAuthors(authors = []) {
  return authors.map(author => {
    const family = author.family || '';
    const initials = authorInitials(author.given);
    const text = `${family}${initials ? ', ' + initials : ''}`;
    const escaped = escapeHtml(text);
    return /onditi/i.test(family) ? `<strong>${escaped}</strong>` : escaped;
  }).join(', ');
}

function formatTitle(title) {
  const taxa = [
    'Anourosorex', 'Blarinella', 'Blarinellini', 'Chodsigoa', 'Episoriculus',
    'Graphiurus', 'Lemniscomys', 'Lophuromys', 'Mesechinus', 'Micromys',
    'Neodon', 'Parablarinella', 'Soriculus', 'Uropsilinae', 'Uropsilus'
  ];
  let out = escapeHtml(title || 'Untitled');
  taxa.forEach(name => {
    out = out.replace(new RegExp(`\\b${name}\\b`, 'g'), `<em>${name}</em>`);
  });
  return out;
}

function formatVenue(item) {
  const journal = item['container-title'] || '';
  const bits = [];
  if (item.volume) {
    bits.push(item.issue ? `${item.volume}(${item.issue})` : item.volume);
  } else if (item.issue) {
    bits.push(`(${item.issue})`);
  }
  if (item.page) bits.push(item.page);
  return [journal, bits.join(', ')].filter(Boolean).join(', ');
}

function inferTags(item, fallbackTags = '') {
  const text = `${item.title || ''} ${item['container-title'] || ''}`.toLowerCase();
  const tags = new Set((fallbackTags || '').split(/\s+/).filter(Boolean));
  const firstAuthor = item.author?.[0]?.family || '';
  if (/onditi/i.test(firstAuthor)) tags.add('first');
  if (/systematic|phylogeograph|phylogen|taxonomy|taxonomic|new species|diversification|genomic|introgression|mitochondrial|ultraconserved|shrew|mole|vole|dormice|rodent|hedgehog|micromys|graphiurus|lemniscomys|lophuromys|mesechinus|neodon|chodsigoa/.test(text)) {
    tags.add('systematics');
  }
  if (/diversity|distribution|richness|turnover|beta|community|niche|elevational|ecoregion|habitat|edna|assemblage|spatial|macroecolog/.test(text)) {
    tags.add('macroecology');
  }
  if (/conservation|protected|human|wildlife|vehicle|pressure|disturbance|climate|elephant|management|coexistence|fragmentation|homogenization/.test(text)) {
    tags.add('conservation');
  }
  return [...tags].join(' ');
}

function collectFallbackPublicationMetadata() {
  const byDoi = new Map();
  const byTitle = new Map();
  document.querySelectorAll('#pubs-list .pub-card').forEach(card => {
    const doi = cleanDoi(card.querySelector('.cite-badge')?.dataset.doi ||
      card.querySelector('a[href*="doi.org"]')?.getAttribute('href'));
    const title = normalizeTitle(card.querySelector('.pub-title')?.textContent);
    const pdfLinks = [...card.querySelectorAll('.pub-link.pdf')].map(link => ({
      href: link.getAttribute('href'),
      label: link.textContent.trim()
    })).filter(link => link.href);
    const meta = {
      isOpenAccess: card.classList.contains('oa'),
      pdfLinks,
      tags: card.dataset.tags || ''
    };
    if (doi) byDoi.set(doi.toLowerCase(), meta);
    if (title) byTitle.set(title, meta);
  });
  return { byDoi, byTitle };
}

function fallbackForItem(item, fallback) {
  const doi = cleanDoi(item.DOI).toLowerCase();
  const title = normalizeTitle(item.title);
  return fallback.byDoi.get(doi) || fallback.byTitle.get(title) || {};
}

function isPreprint(item) {
  return item?.type === 'preprint' ||
    /preprint|research square|biorxiv|ecoevorxiv|ssrn/i.test(item?.['container-title'] || '') ||
    /preprint/i.test(item?.note || '');
}

function isOpenAccess(item, fallbackMeta) {
  if (isPreprint(item)) return true;                 // preprint servers are always open
  if (typeof fallbackMeta.isOpenAccess === 'boolean') return fallbackMeta.isOpenAccess;
  const journal = String(item['container-title'] || '').toLowerCase();
  return /bmc|frontiers|mdpi|scientific reports|zookeys|zoological research|ecosphere|global change biology|global ecology and conservation|ecology and evolution|life\b|diversity\b|animals\b/.test(journal);
}

/* A card's number is its position in a reverse-chronological list, so it shifts
   every time a paper is added. Anchors built from the DOI are stable forever,
   and are what other pages should link to. */
function doiSlug(doi) {
  const clean = cleanDoi(doi).toLowerCase();
  return clean ? 'p-' + clean.replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') : '';
}

function scholarUrl(title) {
  return `https://scholar.google.com/scholar?q=${encodeURIComponent(title || '')}`;
}

function renderPublicationCard(pub, number) {
  const item = pub.item;
  const doi = cleanDoi(item.DOI);
  const doiUrl = doi ? `https://doi.org/${doi}` : '';
  const venue = formatVenue(item);
  const oa = pub.isOpenAccess;
  const tags = pub.tags;
  const pdfLinks = (pub.fallback.pdfLinks || [])
    .map(link => `<a href="${escapeHtml(link.href)}" class="pub-link pdf">${escapeHtml(link.label)}</a>`)
    .join('');

  return `
    <div class="pub-card ${oa ? 'oa' : 'restricted'}${pub.isPreprint ? ' preprint' : ''}" id="pub-${number}" data-tags="${escapeHtml(tags)}" data-doi="${escapeHtml(doi)}">
      ${doi ? `<span class="pub-anchor" id="${doiSlug(doi)}" aria-hidden="true"></span>` : ''}
      <div class="pub-card-header" onclick="toggleAbstract(${number})">
        <span class="pub-num">${number}</span>
        <div class="pub-body">
          <div class="pub-authors">${formatAuthors(item.author)}</div>
          <div class="pub-title">${formatTitle(item.title)}</div>
          <div class="pub-venue-row">
            <span class="pub-venue">${escapeHtml(venue)}${doiUrl ? ` · <a href="${doiUrl}" target="_blank" rel="noopener">doi:${escapeHtml(doi)}</a>` : ''}</span>
            ${pub.isPreprint ? '<span class="badge badge-preprint">📄 Preprint · not peer reviewed</span>' : ''}
            <span class="badge ${oa ? 'badge-oa' : 'badge-restricted'}">${oa ? '🔓 OA' : '🔒 Subscription'}</span>
            ${doi ? `<span class="badge badge-citations cite-badge" id="cit-${number}" data-doi="${escapeHtml(doi)}" style="display:none;"></span>` : ''}
          </div>
        </div>
        <div class="pub-card-actions">
          <button class="abstract-toggle" aria-expanded="false" onclick="event.stopPropagation();toggleAbstract(${number})">
            <span class="toggle-label">Abstract</span> <span class="toggle-icon">▾</span>
          </button>
        </div>
      </div>
      <div class="pub-abstract-body" id="abs-${number}">
        <div class="pub-abstract-text" id="abs-text-${number}">
          ${item.abstract ? `<p>${escapeHtml(item.abstract)}</p>` : '<p style="color:var(--faint);font-style:italic;">Abstract not available. Please visit the journal page.</p>'}
        </div>
        <div class="pub-links-row">
          ${doiUrl ? `<a href="${doiUrl}" target="_blank" rel="noopener" class="pub-link">📄 View at Journal ↗</a>` : ''}
          <a href="${scholarUrl(item.title)}" target="_blank" rel="noopener" class="pub-link scholar">🎓 Google Scholar ↗</a>
          ${pdfLinks}
        </div>
      </div>
    </div>`;
}

function renderPublicationsPage(items, fallback) {
  const list = document.getElementById('pubs-list');
  if (!list) return;

  const pubs = items
    .map((item, index) => {
      const meta = fallbackForItem(item, fallback);
      const oa = isOpenAccess(item, meta);
      const preprint = isPreprint(item);
      // Deduplicate: inferTags may already carry 'oa' through from a legacy card.
      const tags = [...new Set(
        [inferTags(item, meta.tags), oa ? 'oa' : '', preprint ? 'preprint' : 'peer-reviewed']
          .join(' ').split(/\s+/).filter(Boolean)
      )].join(' ');
      return { item, index, fallback: meta, isOpenAccess: oa, isPreprint: preprint, tags };
    })
    .sort((a, b) => dateSortKey(b.item, b.index) - dateSortKey(a.item, a.index));

  const groups = new Map();
  pubs.forEach((pub, index) => {
    pub.number = pubs.length - index;
    const year = publicationYear(pub.item) || 'Undated';
    if (!groups.has(year)) groups.set(year, []);
    groups.get(year).push(pub);
  });

  list.innerHTML = [...groups.entries()].map(([year, group]) => `
    <div class="pub-year-group" id="year-${year}">
      <div class="pub-year-heading">${year}</div>
      ${group.map(pub => renderPublicationCard(pub, pub.number)).join('')}
    </div>
  `).join('');

  const years = pubs.map(pub => publicationYear(pub.item)).filter(Boolean);
  const minYear = Math.min(...years);
  const maxYear = Math.max(...years);

  // Counts that come from the rendered list itself, bound the same way as the
  // remote metrics so every tracker on the page has one update path.
  applyMetrics({
    open_access_count: pubs.filter(pub => pub.isOpenAccess).length,
    year_range_label: Number.isFinite(minYear) && Number.isFinite(maxYear)
      ? `Years ${minYear}\u2013${maxYear}` : ''
  });

  document.querySelectorAll('.pub-filter-btn[data-filter]').forEach(btn => {
    const filter = btn.dataset.filter;
    const count = filter === 'all'
      ? pubs.length
      : pubs.filter(pub => (pub.tags || '').split(/\s+/).includes(filter)).length;
    const label = btn.dataset.label || btn.textContent.replace(/\s*\(\d+\)\s*$/, '').trim();
    btn.dataset.label = label;
    btn.textContent = `${label} (${count})`;
  });
}

function renderHomePublications(items) {
  const list = document.getElementById('home-publications') || document.querySelector('.pub-preview-list');
  if (!list) return;

  const pubs = items
    .map((item, index) => ({ item, index }))
    .sort((a, b) => dateSortKey(b.item, b.index) - dateSortKey(a.item, a.index))
    .slice(0, 4);

  list.innerHTML = pubs.map((pub, index) => {
    const item = pub.item;
    const doi = cleanDoi(item.DOI);
    const doiUrl = doi ? `https://doi.org/${doi}` : '';
    return `
      <div class="pub-preview${isPreprint(item) ? ' preprint' : ''}">
        <span class="pub-year-badge">${publicationYear(item) || ''}</span>
        <div>
          <div class="pub-preview-title">${formatTitle(item.title)}</div>
          <div class="pub-preview-journal">${escapeHtml(formatVenue(item))}${isPreprint(item) ? ' <span class="badge badge-preprint">Preprint</span>' : ''}</div>
          ${doiUrl ? `<a class="pub-preview-doi" href="${doiUrl}" target="_blank" rel="noopener">doi: ${escapeHtml(doi)} ↗</a>` : ''}
        </div>
        <div class="pub-preview-cit">
          ${doi ? `<span class="badge badge-citations cite-badge" id="cit-home-${index + 1}" data-doi="${escapeHtml(doi)}" style="display:none;"></span>` : ''}
        </div>
      </div>`;
  }).join('');

  const allLink = document.getElementById('home-all-publications-link') ||
    [...document.querySelectorAll('a[href="publications.html"]')].find(link => /View all/i.test(link.textContent));
  if (allLink) allLink.textContent = `View all ${items.length} publications \u2192`;
}

async function initPublicationsData() {
  const needsData = document.getElementById('pubs-list') ||
    document.getElementById('home-publications') ||
    document.querySelector('[data-metric^="library_"]');
  if (!needsData) return null;

  const fallback = collectFallbackPublicationMetadata();
  try {
    const res = await fetch(PUBLICATIONS_DATA_URL, { cache: 'no-store' });
    if (!res.ok) throw new Error('Publication data unavailable');
    const items = (await res.json()).filter(item => item && item.title);
    renderPublicationsPage(items, fallback);
    renderHomePublications(items);
    return items;
  } catch (e) {
    // Keep the static fallback when opened as file:// or if the JSON is unavailable.
    return null;
  }
}

function hydrateAbstracts(root = document) {
  root.querySelectorAll('.pub-abstract-text[data-fetch][data-doi]').forEach(el => {
    fetchAbstract(el.dataset.doi, el.id);
  });
}

/* ─── METRICS TRACKERS ───────────────────────────────────────────────
   Every live number on the site is bound declaratively:

     <span data-metric="citations">357</span>

   The text already in the element is the fallback, so the page is correct
   before any network call and stays correct if every call fails. Values come
   from assets/data/scholar-stats.json, refreshed weekly by the metrics
   workflow from ORCID (works), OpenAlex, and — when it is reachable —
   Google Scholar.

   Peer-reviewed work counts are sourced from ORCID, the authoritative record
   of what has actually been published, rather than from a citation index.
   ------------------------------------------------------------------- */
const METRICS_URL = 'assets/data/scholar-stats.json';

const SOURCE_LABELS = {
  scholar:  { name: 'Google Scholar', url: 'https://scholar.google.com/citations?user=qnHYvIIAAAAJ&hl=en' },
  openalex: { name: 'OpenAlex',       url: 'https://openalex.org/A5086398996' },
  orcid:    { name: 'ORCID',          url: 'https://orcid.org/0000-0003-4034-6818' }
};

function formatMetricDate(iso) {
  if (!iso) return '';
  const d = new Date(iso + 'T00:00:00Z');
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' });
}

/* Numbers the site derives itself, so a tracker can bind to them the same way. */
function derivedMetrics(items) {
  if (!Array.isArray(items) || !items.length) return {};
  const peerReviewed = items.filter(i => i.type !== 'preprint');
  const years = items.map(publicationYear).filter(Boolean);
  return {
    library_records:       items.length,
    library_peer_reviewed: peerReviewed.length,
    library_preprints:     items.length - peerReviewed.length,
    year_span:             new Set(years).size,
    first_year:            years.length ? Math.min(...years) : null,
    latest_year:           years.length ? Math.max(...years) : null
  };
}

/* Journals reviewed for, from the ORCID peer-review record. The static list in
   the CV markup is the fallback; it was hand-maintained and had drifted well
   behind the real total, which is exactly what this replaces. */
function renderPeerReviews(breakdown) {
  const host = document.getElementById('review-tags');
  if (!host || !Array.isArray(breakdown) || !breakdown.length) return;

  const SHORTEN = [
    [/^Journal of /, 'J. '],
    [/^Proceedings of the /, 'Proc. '],
    [/ & Evolutionary Research$/, ' & Evol. Res.'],
  ];
  const label = name => SHORTEN.reduce((acc, [re, to]) => acc.replace(re, to), name);

  host.innerHTML = breakdown
    .filter(j => j && j.name && j.reviews > 0)
    .map(j => `<span class="review-tag">${escapeHtml(label(j.name))} (${j.reviews})</span>`)
    .join('\n');
}

function applyMetrics(values, root = document) {
  root.querySelectorAll('[data-metric]').forEach(el => {
    const value = values[el.dataset.metric];
    if (value == null || value === '') return;
    el.textContent = typeof value === 'number' ? value.toLocaleString() : value;
    el.classList.add('metric-live');
  });
  root.querySelectorAll('[data-metric-href]').forEach(el => {
    const href = values[el.dataset.metricHref];
    if (href) el.setAttribute('href', href);
  });
}

let metricsCache = null;
async function loadMetrics() {
  if (metricsCache) return metricsCache;
  try {
    const res = await fetch(METRICS_URL, { cache: 'no-cache', signal: AbortSignal.timeout(8000) });
    if (!res.ok) throw new Error('metrics ' + res.status);
    metricsCache = await res.json();
  } catch (e) {
    metricsCache = {};   // keep the values already rendered in the HTML
  }
  return metricsCache;
}

async function initMetrics(derived = {}) {
  const d = await loadMetrics();
  const source = SOURCE_LABELS[d.citation_source] || SOURCE_LABELS.scholar;

  // `derived` is a fallback only: the metrics file already reconciles the ORCID
  // count against this same bibliography, so every page shows one figure whether
  // or not it happens to render a publication list.
  applyMetrics({
    ...derived,
    ...d,
    citation_source_name: source.name,
    citation_source_url:  source.url,
    citation_as_of_label: formatMetricDate(d.citation_as_of || d.last_updated),
    last_updated_label:   formatMetricDate(d.last_updated),
    peer_review_years_label: d.peer_review_first_year && d.peer_review_latest_year
      ? `${d.peer_review_first_year}\u2013${d.peer_review_latest_year}` : ''
  });

  renderPeerReviews(d.peer_review_breakdown);
}

/* ─── STRUCTURED DATA ──────────────────────────────────────────────────
   The publication list is rendered from the bibliography, so its schema.org
   description is generated from the same data rather than maintained by hand
   in the markup, where it would silently drift out of date.
   ------------------------------------------------------------------- */
function injectPublicationSchema(items) {
  if (!Array.isArray(items) || !items.length) return;
  if (!document.getElementById('pubs-list')) return;
  if (document.getElementById('pubs-schema')) return;

  const sorted = [...items]
    .map((item, index) => ({ item, index }))
    .sort((a, b) => dateSortKey(b.item, b.index) - dateSortKey(a.item, a.index));

  const payload = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    name: 'Publications — Kenneth Otieno Onditi',
    numberOfItems: sorted.length,
    itemListElement: sorted.map(({ item }, i) => {
      const doi = cleanDoi(item.DOI);
      const work = {
        '@type': 'ScholarlyArticle',
        name: String(item.title || '').replace(/<[^>]+>/g, ''),
        author: (item.author || []).map(a => ({
          '@type': 'Person',
          name: [a.given, a.family].filter(Boolean).join(' ')
        })),
        datePublished: String(publicationYear(item) || ''),
        url: doi ? `https://doi.org/${doi}` : (item.URL || '')
      };
      if (doi) {
        work.identifier = { '@type': 'PropertyValue', propertyID: 'DOI', value: doi };
        work.sameAs = `https://doi.org/${doi}`;
      }
      if (item['container-title']) {
        work.isPartOf = { '@type': 'Periodical', name: item['container-title'] };
      }
      if (item.abstract) work.abstract = item.abstract;
      if (isPreprint(item)) work.creativeWorkStatus = 'Preprint';
      return { '@type': 'ListItem', position: i + 1, item: work };
    })
  };

  const tag = document.createElement('script');
  tag.type = 'application/ld+json';
  tag.id = 'pubs-schema';
  tag.textContent = JSON.stringify(payload);
  document.head.appendChild(tag);
}

/* ─── DEEP LINKS ───────────────────────────────────────────────────────
   Publication cards are rendered after an async fetch, so by the time they
   exist the browser has already tried and failed to resolve the URL fragment.
   Re-resolve it here, and open the abstract of whatever was linked to.
   ------------------------------------------------------------------- */
function focusHashTarget() {
  const hash = decodeURIComponent(window.location.hash || '').replace(/^#/, '');
  if (!hash) return;
  const target = document.getElementById(hash);
  if (!target) return;
  const card = target.closest('.pub-card') || target;
  card.scrollIntoView({ behavior: 'smooth', block: 'center' });
  card.classList.add('pub-card-targeted');
  const number = (card.id || '').replace('pub-', '');
  if (number && !card.querySelector('.pub-abstract-body.open')) toggleAbstract(number);
}

/* ─── BATCH LOAD ON DOMCONTENTLOADED ─── */
window.addEventListener('DOMContentLoaded', async () => {
  const items = await initPublicationsData();
  await initMetrics(derivedMetrics(items));
  injectPublicationSchema(items);
  hydrateCitationBadges();
  hydrateAbstracts();
  focusHashTarget();
});
window.addEventListener('hashchange', focusHashTarget);

/* ─── ABSTRACT TOGGLE ─── */
// Global function called by inline onclick="toggleAbstract(n)" on card headers
function toggleAbstract(n) {
  const card = document.getElementById('pub-' + n);
  if (!card) return;
  const body = card.querySelector('.pub-abstract-body');
  const btn  = card.querySelector('.abstract-toggle');
  if (!body) return;
  const open = body.classList.toggle('open');
  if (btn) {
    btn.setAttribute('aria-expanded', String(open));
    const lbl = btn.querySelector('.toggle-label');
    const ico = btn.querySelector('.toggle-icon');
    if (lbl) lbl.textContent = open ? 'Hide abstract' : 'Abstract';
    if (ico) ico.textContent = open ? '▴' : '▾';
  }
}

/* ─── PUBLICATION FILTERS ─── */
window.addEventListener('DOMContentLoaded', () => {
  const filterBtns = document.querySelectorAll('.pub-filter-btn');
  if (!filterBtns.length) return;

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update active state
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filter = btn.dataset.filter;
      const cards  = document.querySelectorAll('#pubs-list .pub-card');

      cards.forEach(card => {
        if (filter === 'all') {
          card.style.display = '';
        } else {
          const tags = (card.dataset.tags || '').split(' ');
          card.style.display = tags.includes(filter) ? '' : 'none';
        }
      });

      // Hide year-group headings that have no visible cards underneath
      document.querySelectorAll('.pub-year-group').forEach(group => {
        const anyVisible = [...group.querySelectorAll('.pub-card')]
          .some(c => c.style.display !== 'none');
        group.style.display = anyVisible ? '' : 'none';
      });
    });
  });
});

/* ─── SMOOTH BACK-TO-TOP ─── */
const backTop = document.getElementById('back-top');
if (backTop) {
  window.addEventListener('scroll', () => {
    backTop.style.opacity = window.scrollY > 400 ? '1' : '0';
    backTop.style.pointerEvents = window.scrollY > 400 ? 'auto' : 'none';
  });
  backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}
