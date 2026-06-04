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
Publication cards are rendered from the Zotero CSL JSON export at `OKOs_Library.json`. Abstracts come from that file when present, so the page remains fast and consistent with the bibliography source. Older static fallback cards still use the CrossRef abstract fetcher when the JSON cannot be loaded, for example when opening the page directly as `file://`.

### Updating the total citation count
The hero card on `index.html` shows a static "200+" figure. Update it manually when the Google Scholar total passes a new milestone:

```html
<!-- index.html, inside .hero-stats -->
<span class="stat-num">350<sup style="font-size:18px">+</sup></span>
```

---

## Updating Publications

The live Publications page and the highlighted publications on the Home page are data-driven from `OKOs_Library.json`, a Zotero CSL JSON export stored at the site root.

1. Update the Zotero library record, including DOI, journal, year, volume/issue/pages, abstract, and URL.

2. Export the selected collection from Zotero as CSL JSON.

3. Replace `OKOs_Library.json` in the repository root with the new export.

4. If an author-copy PDF is available, place it in `pdfs/`. The renderer preserves PDF links already present in the static fallback cards; new PDFs can be added to the fallback card or linked in a future data-enrichment field.

5. Commit `OKOs_Library.json` with any changed PDFs. Counts, year groups, homepage highlights, DOI links, citation badges, and abstracts update from the JSON automatically.

The static cards in `publications.html` are retained as a no-network/no-fetch fallback, but they are no longer the primary editing surface.

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
git commit -m "Update Zotero publication data"
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
