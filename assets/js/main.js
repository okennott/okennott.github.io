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

/* ─── CITATION FETCHER (Semantic Scholar — per-paper only) ─── */
async function fetchCitationCount(doi, elementId) {
  if (!doi || !elementId) return;
  const el = document.getElementById(elementId);
  if (!el) return;
  try {
    const res = await fetch(
      `https://api.semanticscholar.org/graph/v1/paper/DOI:${encodeURIComponent(doi)}?fields=citationCount`,
      { signal: AbortSignal.timeout(6000) }
    );
    if (!res.ok) return;
    const data = await res.json();
    if (typeof data.citationCount === 'number') {
      el.textContent = data.citationCount + ' cit.';
      el.style.display = 'inline-flex';
      el.classList.add('loaded');
    }
  } catch(e) { /* fail silently */ }
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
    'Anourosorex', 'Blarinella', 'Chodsigoa', 'Graphiurus', 'Lemniscomys',
    'Lophuromys', 'Mesechinus', 'Micromys', 'Neodon', 'Parablarinella'
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

function isOpenAccess(item, fallbackMeta) {
  if (typeof fallbackMeta.isOpenAccess === 'boolean') return fallbackMeta.isOpenAccess;
  const journal = String(item['container-title'] || '').toLowerCase();
  return /bmc|frontiers|mdpi|scientific reports|zookeys|zoological research|ecosphere|global change biology|global ecology and conservation|ecology and evolution|life\b|diversity\b|animals\b/.test(journal);
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
  const tags = inferTags(item, pub.fallback.tags);
  const pdfLinks = (pub.fallback.pdfLinks || [])
    .map(link => `<a href="${escapeHtml(link.href)}" class="pub-link pdf">${escapeHtml(link.label)}</a>`)
    .join('');

  return `
    <div class="pub-card ${oa ? 'oa' : 'restricted'}" id="pub-${number}" data-tags="${escapeHtml(tags + (oa ? ' oa' : ''))}">
      <div class="pub-card-header" onclick="toggleAbstract(${number})">
        <span class="pub-num">${number}</span>
        <div class="pub-body">
          <div class="pub-authors">${formatAuthors(item.author)}</div>
          <div class="pub-title">${formatTitle(item.title)}</div>
          <div class="pub-venue-row">
            <span class="pub-venue">${escapeHtml(venue)}${doiUrl ? ` · <a href="${doiUrl}" target="_blank" rel="noopener">doi:${escapeHtml(doi)}</a>` : ''}</span>
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
      return { item, index, fallback: meta, isOpenAccess: isOpenAccess(item, meta) };
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
  const oaCount = pubs.filter(pub => pub.isOpenAccess).length;

  const statNums = document.querySelectorAll('.pub-stats-bar .pub-stat-box .num');
  if (statNums[0]) statNums[0].textContent = pubs.length;
  if (statNums[2]) statNums[2].textContent = new Set(years).size;
  if (statNums[3]) statNums[3].textContent = oaCount;
  const yearsLabel = document.querySelectorAll('.pub-stats-bar .pub-stat-box .lbl')[2];
  if (yearsLabel && Number.isFinite(minYear) && Number.isFinite(maxYear)) yearsLabel.textContent = `Years ${minYear}-${maxYear}`;

  const allBtn = document.querySelector('.pub-filter-btn[data-filter="all"]');
  if (allBtn) allBtn.textContent = `All (${pubs.length})`;
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
      <div class="pub-preview">
        <span class="pub-year-badge">${publicationYear(item) || ''}</span>
        <div>
          <div class="pub-preview-title">${formatTitle(item.title)}</div>
          <div class="pub-preview-journal">${escapeHtml(formatVenue(item))}</div>
          ${doiUrl ? `<a class="pub-preview-doi" href="${doiUrl}" target="_blank" rel="noopener">doi: ${escapeHtml(doi)} ↗</a>` : ''}
        </div>
        <div class="pub-preview-cit">
          ${doi ? `<span class="badge badge-citations cite-badge" id="cit-home-${index + 1}" data-doi="${escapeHtml(doi)}" style="display:none;"></span>` : ''}
        </div>
      </div>`;
  }).join('');

  const counter = document.getElementById('counter-pubs');
  if (counter) counter.textContent = items.length;
  const allLink = document.getElementById('home-all-publications-link') ||
    [...document.querySelectorAll('a[href="publications.html"]')].find(link => /View all/i.test(link.textContent));
  if (allLink) allLink.textContent = `View all ${items.length} publications →`;
}

async function initPublicationsData() {
  const needsData = document.getElementById('pubs-list') || document.getElementById('home-publications') || document.getElementById('counter-pubs');
  if (!needsData) return;

  const fallback = collectFallbackPublicationMetadata();
  try {
    const res = await fetch(PUBLICATIONS_DATA_URL, { cache: 'no-store' });
    if (!res.ok) throw new Error('Publication data unavailable');
    const items = (await res.json()).filter(item => item && item.title);
    renderPublicationsPage(items, fallback);
    renderHomePublications(items);
    hydrateCitationBadges();
    hydrateAbstracts();
  } catch (e) {
    // Keep the static fallback when opened directly as file:// or if the JSON is unavailable.
  }
}

function hydrateCitationBadges(root = document) {
  root.querySelectorAll('.cite-badge[data-doi]').forEach(el => {
    const doi = el.dataset.doi;
    if (doi && !el.dataset.citationRequested) {
      el.dataset.citationRequested = '1';
      fetchCitationCount(doi, el.id);
    }
  });
}

function hydrateAbstracts(root = document) {
  root.querySelectorAll('.pub-abstract-text[data-fetch][data-doi]').forEach(el => {
    fetchAbstract(el.dataset.doi, el.id);
  });
}

/* ─── SCHOLAR STATS LOADER (from assets/data/scholar-stats.json) ─── */
async function loadScholarStats() {
  try {
    const res = await fetch('assets/data/scholar-stats.json', {
      cache: 'no-cache',
      signal: AbortSignal.timeout(6000)
    });
    if (!res.ok) return;
    const d = await res.json();

    const set = (id, val) => {
      if (val == null) return;
      const el = document.getElementById(id);
      if (el) el.textContent = typeof val === 'number' ? val.toLocaleString() : val;
    };

    if (d.citations) {
      set('stat-citations',        d.citations);
      set('total-citations-badge', d.citations);   // publications page
    }
    if (d.h_index != null)   set('stat-hindex',     d.h_index);
    if (d.i10_index != null) set('stat-i10',        d.i10_index);
    if (d.last_updated)      set('scholar-updated', d.last_updated);
  } catch(e) { /* fall back to static values in HTML */ }
}

/* ─── BATCH LOAD ON DOMCONTENTLOADED ─── */
window.addEventListener('DOMContentLoaded', () => {
  initPublicationsData();
  hydrateCitationBadges();
  hydrateAbstracts();
  loadScholarStats();
});

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
