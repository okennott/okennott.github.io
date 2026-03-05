# kennott.github.io

Personal academic website of **Kenneth Otieno Onditi** — mammal ecologist and evolutionary biologist specialising in the systematics, phylogeography, and conservation biology of small mammals.

🌐 **Live site:** [okennott.github.io](https://okennott.github.io).

---

## Site Overview

A fully static, multi-page academic website built with vanilla HTML, CSS, and JavaScript — no frameworks, no build tools, no dependencies beyond Google Fonts and two public APIs for live data.

| Page | File | Accent colour | Key features |
|---|---|---|---|
| **Home** | `index.html` | Gold | Live news ticker, animated stats card, SVG research icons, selected publications with live citation badges |
| **Research** | `research.html` | Green | Reading-progress bar, sticky numbered themes, collaborator network grid |
| **Publications** | `publications.html` | Green | Filter by topic/OA, expandable abstracts (live API), per-paper citation counts (live API), author-copy PDF links |
| **Fieldwork** | `fieldwork.html` | Terra/earth | Custom SVG Kenya map with expedition markers, vertical timeline, field methods panel |
| **CV** | `cv.html` | Gold | Animated skill bars, print/save-PDF button, print-clean CSS |
| **Contact** | `contact.html` | Blue | Social link cards, collaboration interest chips, collaborator directory |

---

## Repository Structure

```
kennott.github.io/
│
├── index.html                  # Home page
├── research.html               # Research programme
├── publications.html           # Full publications list
├── fieldwork.html              # Fieldwork & expeditions
├── cv.html                     # Curriculum vitae
├── contact.html                # Contact & collaborations
├── 404.html                    # Custom 404 page
│
├── assets/
│   ├── css/
│   │   └── shared.css          # All shared variables, nav, footer, utilities
│   ├── js/
│   │   └── main.js             # Nav active state, scroll reveals, citation & abstract fetchers
│   └── icons/
│       └── logo-mark.svg       # Rodent-skull / DNA nav logo mark
│
├── pdfs/
│   ├── README.txt                                          # Naming guide & full inventory
│   │
│   │   ── Individual PDF files ─────────────────────
│   ├── Author copies for non-open access publications
│   ├── 
├── publications/               # Original link files (legacy)
│   ├── github_link.txt
│   ├── googlescholar_link.txt
│   └── orcid_link.txt
│
└── README.md                   # This file
```

---

## Live Data Features

### Citation counts
Per-paper citation badges on the Publications page are fetched live from the [Semantic Scholar API](https://www.semanticscholar.org/product/api) using each paper's DOI. No API key required. Counts load asynchronously and display as gold badges next to each entry. The same badges appear on the Home page for the four highlighted papers.

### Paper abstracts
Clicking "Abstract ▾" on any publication card fetches the abstract live from the [CrossRef API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/), with [Semantic Scholar](https://api.semanticscholar.org/) as a fallback. Abstracts are fetched lazily on first open, so page load is not affected. If neither API returns content, a graceful message directs the reader to the DOI link.

### Updating the total citation count
The hero card on `index.html` shows a static "200+" figure. Update it manually when the Google Scholar total passes a new milestone:

```html
<!-- index.html, inside .hero-stats -->
<span class="stat-num">350<sup style="font-size:18px">+</sup></span>
```

---

## Adding a New Publication

1. Open `publications.html` and locate the correct year group (or create a new `<div class="pub-year-group" id="year-YYYY">` block at the top of `#pubs-list`).

2. Copy a `.pub-card` block and fill in the new entry. Use `oa` class for open-access papers, `restricted` for subscription journals:

```html
<div class="pub-card oa" id="pub-33" data-tags="first systematics oa">
  <div class="pub-card-header" onclick="toggleAbstract(33)">
    <span class="pub-num">33</span>
    <div class="pub-body">
      <div class="pub-authors"><strong>Onditi, K. O.</strong>, Co-author, A. B. ...</div>
      <div class="pub-title">Title of the paper</div>
      <div class="pub-venue-row">
        <span class="pub-venue">Journal Name, Vol(Issue), pages ·
          <a href="https://doi.org/10.xxxx/xxxxx" target="_blank" rel="noopener">doi:10.xxxx/xxxxx</a>
        </span>
        <span class="badge badge-oa">🔓 OA</span>
        <span class="badge badge-citations cite-badge" id="cit-33"
              data-doi="10.xxxx/xxxxx" style="display:none;"></span>
      </div>
    </div>
    <div class="pub-card-actions">
      <button class="abstract-toggle" aria-expanded="false"
              onclick="event.stopPropagation();toggleAbstract(33)">
        <span class="toggle-label">Abstract</span>
        <span class="toggle-icon">▾</span>
      </button>
    </div>
  </div>
  <div class="pub-abstract-body" id="abs-33">
    <div class="pub-abstract-text" id="abs-text-33"
         data-doi="10.xxxx/xxxxx" data-fetch="1">
      <span class="pub-abstract-loading">Loading abstract…</span>
    </div>
    <div class="pub-links-row">
      <a href="https://doi.org/10.xxxx/xxxxx" target="_blank" rel="noopener"
         class="pub-link">📄 View at Journal ↗</a>
      <a href="pdfs/Onditi_YYYY_ShortTitle.pdf" class="pub-link pdf">⬇ Author Copy (PDF)</a>
    </div>
  </div>
</div>
```

3. Add the `data-tags` values relevant to the paper from: `first`, `systematics`, `macroecology`, `conservation`, `oa`.

4. Update the publication count in three places:
   - `index.html` hero stats: `<span class="stat-num">33</span>`
   - `index.html` "View all" button: `View all 33 publications →`
   - `publications.html` stats bar: `<span class="num">33</span>`

5. Place the author-copy PDF in `pdfs/` following the naming convention in `pdfs/README.txt`.

6. Add a brief entry to the news ticker in `index.html` for visibility.

---

## PDF Inventory & Naming Convention

All 39 PDFs have been renamed from opaque numeric identifiers to human-readable names using the scheme `Lastname_YYYY_ShortTitle[_qualifier].pdf`. The qualifiers used are:

| Qualifier | Meaning |
|---|---|
| *(none)* | Single file for this paper, or primary published version |
| `_v2` | Second copy of the published version (different resolution/layout) |
| `_manuscript` | Peer-review manuscript submitted to the journal |
| `_accepted` | Accepted manuscript (post-peer-review, pre-copyedit) |
| `_preprint` | Posted preprint (Research Square or equivalent) |
| `_correction` | Published erratum / correction notice |
| `_duplicate` | Byte-for-byte duplicate of another file in this folder |

**Papers with multiple files (6 papers, 13 files across them):**

| Paper | Files |
|---|---|
| Sambaya et al. 2025 (*Lemniscomys*) | `Sambaya_2025_Lemniscomys.pdf` + `_manuscript.pdf` |
| Yu et al. 2023 (Asian elephants) | `Yu_2023_Asian_elephants_habitat.pdf` + `_accepted.pdf` + `_preprint.pdf` |
| Onditi et al. 2021 (*Lophuromys* BMC) | `Onditi_2021_Lophuromys_biogeography.pdf` + `_v2.pdf` + `_preprint.pdf` |
| Onditi et al. 2020 (Mount Kenya *Lophuromys*) | `Onditi_2020_MountKenya_Lophuromys.pdf` + `_correction.pdf` |
| Chen et al. 2020 (Yulong Mountain) | `Chen_2020_Yulong_mammals.pdf` + `_duplicate.pdf` (identical files) |

**Note:** `Song_2022_Niche_theory_review.pdf` (pub #22 — Acta Theriologica Sinica Chinese-language review) has no PDF available. The download button is hidden for that entry.

**Note:** `Onditi_2018_MSc_thesis_Lophuromys_aquilus.pdf` is Kenneth's MSc thesis (154 pp., University of Chinese Academy of Sciences) on the *Lophuromys aquilus* species complex. It is not linked from the publications page as it is not a peer-reviewed journal article.

### Adding a new PDF

1. Export the paper PDF from your reference manager (or use the publisher's accepted-manuscript version).
2. Rename it: `Lastname_YYYY_ShortTitle.pdf` (add a qualifier suffix if a second copy is warranted).
3. Drop it into `pdfs/`.
4. Commit and push — the download button on the publications page activates immediately.

Open-access papers (BMC, Frontiers, MDPI, Scientific Reports, ZooKeys, Zoological Research, Ecosphere) are freely available at the publisher DOI and do not strictly require an author copy, though including one keeps everything in one place.

---

## Deployment

The site is fully static — push to `main` and GitHub Pages deploys automatically (typically within 1–2 minutes).

```bash
git add .
git commit -m "Add pub #33: Onditi et al. YYYY — Journal Name"
git push origin main
```

Make sure GitHub Pages is configured to deploy from:
**Settings → Pages → Source → Deploy from a branch → `main` / root**

---

## GitHub Pages URL

The current live path is `https://okennott.github.io/kennott.github.io/` because the GitHub username (`okennott`) does not match the repository name (`kennott.github.io`). See **[`GITHUB_PAGES_SETUP.md`](GITHUB_PAGES_SETUP.md)** for three options to resolve this:

| Option | Result URL | Effort |
|---|---|---|
| Rename GitHub username to `kennott` | `https://kennott.github.io/` ✅ | Low — one settings change |
| Rename repo to `okennott.github.io` | `https://okennott.github.io/` ✅ | Low — one settings change |
| Custom domain (e.g. `kennetonditi.com`) | `https://kennetonditi.com/` ✅ | Medium — DNS + CNAME file |

All relative links (`href="research.html"` etc.) work correctly regardless of which option is chosen, because no absolute base path is hardcoded.

---

## Local Preview

No build step required. Serve locally to avoid CORS issues with the citation/abstract APIs:

```bash
# Python 3
python3 -m http.server 8000
# then open http://localhost:8000

# Node (if installed)
npx serve .
```

Opening `index.html` directly as a `file://` URL will work for layout review but the live citation and abstract fetches will be blocked by CORS in most browsers.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Markup | HTML5 (semantic) |
| Styling | CSS3 — custom properties, Grid, Flexbox; no framework |
| Scripts | Vanilla ES2020 JavaScript; no bundler |
| Fonts | EB Garamond, DM Mono, Bitter (Google Fonts CDN) |
| Live citations | [Semantic Scholar Graph API](https://api.semanticscholar.org/graph/v1/) |
| Live abstracts | [CrossRef REST API](https://api.crossref.org/works/) + Semantic Scholar fallback |
| Hosting | GitHub Pages (static, free tier) |

---

## Colour Palette

```
--bg:       #0f0c07   Background
--surface:  #171209   Elevated surface
--panel:    #1e1710   Card / panel
--border:   #2e2618   Dividers
--text:     #e8dfc8   Body text
--muted:    #8a7d62   Secondary text
--gold:     #c8943a   Primary accent (home, CV)
--gold2:    #e8b860   Highlight gold
--green:    #5a8c6a   Research / publications accent
--terra:    #b85c38   Fieldwork accent
--blue:     #4a7a9b   Contact accent
--cream:    #f2e8d0   Headings
```

---

## Contact

**Kenneth Otieno Onditi**
kenotieno@hotmail.com · kenotieno08@gmail.com
+254 722 620075
Nairobi, Kenya

[Google Scholar](https://scholar.google.com/citations?user=qnHYvIIAAAAJ&hl=en) · [ResearchGate](https://www.researchgate.net/profile/Kenneth-Onditi) · [ORCID 0000-0003-4034-6818](https://orcid.org/0000-0003-4034-6818) · [GitHub @okennott](https://github.com/okennott)
