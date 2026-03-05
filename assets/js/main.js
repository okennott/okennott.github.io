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

/* ─── CITATION FETCHER (Semantic Scholar) ─── */
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

/* Batch load citations for all .cite-badge elements on page */
window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.cite-badge[data-doi]').forEach(el => {
    const doi = el.dataset.doi;
    fetchCitationCount(doi, el.id);
  });
  document.querySelectorAll('.pub-abstract-text[data-fetch][data-doi]').forEach(el => {
    fetchAbstract(el.dataset.doi, el.id);
  });
});

/* ─── ABSTRACT TOGGLE ─── */
document.addEventListener('click', function(e) {
  if (e.target.closest('.abstract-toggle')) {
    const btn = e.target.closest('.abstract-toggle');
    const card = btn.closest('.pub-card');
    const body = card.querySelector('.pub-abstract-body');
    const open = body.classList.toggle('open');
    btn.setAttribute('aria-expanded', open);
    btn.querySelector('.toggle-label').textContent = open ? 'Hide abstract' : 'Abstract';
    btn.querySelector('.toggle-icon').textContent = open ? '▴' : '▾';
  }
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
