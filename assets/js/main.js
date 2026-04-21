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

/* ─── BATCH LOAD ON DOMCONTENTLOADED ─── */
window.addEventListener('DOMContentLoaded', () => {
  // Per-paper citation badges (Semantic Scholar)
  document.querySelectorAll('.cite-badge[data-doi]').forEach(el => {
    const doi = el.dataset.doi;
    if (doi) fetchCitationCount(doi, el.id);
  });
  // Abstracts (CrossRef)
  document.querySelectorAll('.pub-abstract-text[data-fetch][data-doi]').forEach(el => {
    fetchAbstract(el.dataset.doi, el.id);
  });
  // NOTE: Author-level totals (citations, h-index) are set statically from
  // Google Scholar and are intentionally NOT overwritten at runtime.
  // Semantic Scholar uses a different methodology and returns lower figures.
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
