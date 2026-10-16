# okennott.github.io

Personal academic website of **Kenneth Otieno Onditi** — mammal ecologist and evolutionary biologist specialising in the systematics, phylogeography, and conservation biology of small mammals.

🌐 **Live site:** [okennott.github.io](https://okennott.github.io).

---

## Site Overview

A fully static, multi-page academic website built with vanilla HTML, CSS, and JavaScript — no frameworks or runtime build step. Optional maintenance scripts refresh static fallbacks and build the downloadable CV. Google Fonts and public APIs supply live enhancements.

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
okennott.github.io/
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
│   │   └── main.js             # Nav, scroll reveals, publication rendering, metric trackers,
│   │                               #   batched citation fetch, deep-link resolution
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
Per-paper citation badges are fetched in **one batched request** covering every DOI on the page, from the [OpenAlex API](https://docs.openalex.org/) (best-effort; availability and quotas depend on the service), with the [Semantic Scholar batch endpoint](https://api.semanticscholar.org/api-docs/) as a fallback. Counts display as gold badges next to each entry, on both the Publications and Home pages.

Batching matters: the earlier implementation issued one request per paper, which fired ~40 parallel calls on every page load and reliably tripped Semantic Scholar's anonymous rate limit (HTTP 429), leaving most badges blank.

If OpenAlex returns only part of the batch, Semantic Scholar is queried only for unresolved DOIs. An indexed zero is a valid result and stays hidden; it does not trigger another lookup or replace a positive count from the preferred source.

### Site-wide metric trackers
Every live number is bound declaratively, and the text already in the HTML is the offline fallback:

```html
<span data-metric="peer_reviewed_works">39</span>
<span data-metric="citations">358</span>
<a data-metric-href="citation_source_url" href="...">…</a>
```

Values come from `assets/data/scholar-stats.json`, refreshed daily by `.github/workflows/update-metrics.yml`. Available keys include `peer_reviewed_works`, `preprints`, `works_total`, `citations`, `h_index`, `i10_index`, `peer_reviews`, `peer_review_journals`, `peer_review_years_label`, `citation_source_name`, `citation_source_url`, `citation_as_of_label`, `last_updated_label`, plus counts the page derives from the bibliography itself (`library_records`, `open_access_count`, `year_span`, `year_range_label`).

The homepage names the source and shows the exact date of each snapshot. Publication totals reconcile ORCID with the curated bibliography, so a count that includes papers awaiting ORCID deposit is labelled **ORCID + library**. `orcid_as_of` and `peer_review_as_of` change only when those figures are accepted; `last_checked` records the refresh attempt. A blocked Scholar refresh retains the last complete Scholar snapshot and displays its saved date. After 60 days, the browser and updater select the complete OpenAlex snapshot instead, including its source link, citations, h-index, and i10-index together.

On pages that load the bibliography, its current counts take precedence over a saved metrics file until the next scheduled refresh. Article totals are still reconciled with ORCID, without changing the dates of the external snapshots.

Note the two distinct "peer review" metrics: `peer_reviewed_works` is **articles Kenneth has published**; `peer_reviews` is **manuscripts he has reviewed for journals**. They are unrelated numbers from two different ORCID endpoints.

### Peer review service
The CV's "Peer Review Activity" list is generated from ORCID's `/peer-reviews` endpoint. ORCID groups reviews by the journal's ISSN and names only the reporting aggregator (Clarivate/Web of Science, Springer Nature) rather than the journal, so journal names are resolved from the ISSN via OpenAlex and cached into `peer_review_breakdown` — the page itself does no lookups. The static list in `cv.html` is the no-JavaScript fallback and is refreshed whenever the data is.

**Sources, and why each one:**

| Metric | Source | Rationale |
|---|---|---|
| Peer-reviewed articles | [ORCID](https://orcid.org/0000-0003-4034-6818) | The authoritative record of what has actually been published, rather than whatever a citation index happens to have indexed. |
| Peer review service | [ORCID](https://orcid.org/0000-0003-4034-6818) peer-review record | Manuscripts reviewed for journals. ORCID is the only place this is tracked at all, and it stays current because Web of Science and Springer Nature report into it automatically. |
| Citations, h-index, i10 | Google Scholar, else OpenAlex | Broadest coverage first; OpenAlex takes over automatically once a Scholar snapshot goes stale. |
| Per-paper citations | OpenAlex | Batched requests; returns open-access status in the same payload. |

Scholar and OpenAlex index different corpora, so their numbers never agree. Each is therefore stored as a **complete, self-consistent snapshot** under `citation_profiles`, and the site displays one snapshot at a time with its source named next to the number — never a citation count from one index beside an h-index from another.

### Deep-linking to a publication
Card numbers (`#pub-12`) are positions in a reverse-chronological list, so they shift whenever a paper is added. Link to the **DOI-derived anchor** instead, which never moves:

```
publications.html#p-10-1111-cobi-70214     ← doi:10.1111/cobi.70214
```

The slug is the DOI lowercased with every run of non-alphanumeric characters replaced by `-`, prefixed with `p-`. Because cards render after an async fetch, `main.js` re-resolves the fragment once the list exists and opens the linked paper's abstract.

### Paper abstracts
Publication cards are rendered from the Zotero CSL JSON export at `OKOs_Library.json`. Abstracts come from that file when present and are included in the generated HTML fallbacks. Missing abstracts link readers to the journal; no abstract is inferred from a title.

### Updating the metrics
Nothing to do by hand. `.github/workflows/update-metrics.yml` runs every day at 05:00 UTC and commits `assets/data/scholar-stats.json` and refreshed HTML fallbacks. To refresh immediately, run the workflow from the Actions tab, or locally:

```bash
python scripts/fetch_metrics.py          # all sources
SKIP_SCHOLAR=1 python scripts/fetch_metrics.py   # skip the Scholar scrape
```

The script is designed never to destroy good data:

- ORCID and OpenAlex are fetched with the **standard library only**, so the metrics that drive the site cannot be broken by a failed `pip install`.
- Google Scholar's labelled public profile table is read with the standard library, with `scholarly` as an optional fallback. CAPTCHA pages and incomplete tables are rejected. This remains **best-effort** and time-limited; a blocked refresh preserves the dated snapshot separately from OpenAlex.
- A metric that arrives as `0`, or that collapses by more than 15% against the same source's previous reading, is **rejected** as a failed fetch and the stored value is kept.
- If every source fails, the existing file is left untouched and the run still succeeds.

---

## Updating Publications

The live Publications page and the highlighted publications on the Home page are data-driven from `OKOs_Library.json`, a Zotero CSL JSON export stored at the site root.

1. Update the Zotero library record, including DOI, journal, year, volume/issue/pages, abstract, and URL.

2. Export the selected collection from Zotero as CSL JSON.

3. Replace `OKOs_Library.json` in the repository root with the new export.

4. If an author-copy PDF is available, place it in `pdfs/`. The renderer preserves PDF links already present in the static fallback cards; new PDFs can be added to the fallback card or linked in a future data-enrichment field.

5. Run `python scripts/refresh_static.py` to synchronize static cards, homepage highlights and saved metric labels. Run the checks below, then commit the library, generated HTML, and any changed PDFs. Rebuild the CV as described in `cv/README.md`.

The static cards in `publications.html` are generated fallbacks. Their existing author-copy links and curated topic/access metadata are preserved during refresh; edit the library for bibliographic changes. The October 2026 DOI extraction is documented in [Pei_2026_Nectogale.md](publications/Pei_2026_Nectogale.md). Retain that record in the next Zotero export.

### Accepted papers that have no DOI yet

Add the record to Zotero without a DOI and put this in its Extra/Note field:

```
status: accepted; accepted: YYYY-MM-DD
```

The site then shows an "Accepted · in press" badge and lists the record first, the CV lists it as "(in press)" at the top of the article list, and the counts include it. Only what the library holds is shown, so do not invent a DOI, volume or pages. When the paper is published, add the DOI and volume/pages in Zotero, delete the `status:` line, export the library again, run `python cvdata.py --refresh` and `python build.py` in `cv/`. Run `python scripts/refresh_static.py` from the repository root to synchronize the HTML fallbacks too.

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
4. Add a `pub-link pdf` link to the matching fallback card in `publications.html`, then run `python scripts/refresh_static.py`. Merely adding a PDF file does not create a download link.

Open-access papers (BMC, Frontiers, MDPI, Scientific Reports, ZooKeys, Zoological Research, Ecosphere) are freely available at the publisher DOI and do not strictly require an author copy, though including one keeps everything in one place.

---

## Deployment

The site is fully static — push to `oko` and GitHub Pages deploys automatically (typically within 1–2 minutes).

```bash
git add .
git commit -m "Update Zotero publication data"
git push origin oko
```

Make sure GitHub Pages is configured to deploy from:
**Settings → Pages → Source → Deploy from a branch → `oko` / root**

---

## GitHub Pages URL

The repository is `okennott/okennott.github.io` and the canonical site URL is
https://okennott.github.io/. Page links are relative so local previews also work.

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
| Live citations | [OpenAlex API](https://api.openalex.org/) (batched), Semantic Scholar fallback |
| Live abstracts | Zotero CSL JSON, [CrossRef REST API](https://api.crossref.org/works/) fallback |
| Works / metrics | [ORCID Public API](https://pub.orcid.org/) + OpenAlex, refreshed daily by GitHub Actions |
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

## Maintenance checks

Requires Python and Node.js; the optional HTML maintenance dependency is isolated from the deployed site.

```bash
python -m pip install -r scripts/requirements.txt
python scripts/refresh_static.py
python -m unittest discover -s scripts -p 'test_*.py'
node scripts/test_homepage_metrics.cjs
node scripts/test_publications.cjs
node scripts/test_citations.cjs
python scripts/check_site.py
python scripts/refresh_static.py --check
```

`check-site.yml` runs these checks on pushes and pull requests. `refresh_static.py` uses
the same JavaScript renderers as the browser, preserves author-copy links, reconciles local library totals without changing remote snapshot dates, and uses the
saved metrics check date for reproducible fallback labels. The browser evaluates citation
freshness at page load. See [TODO.md](TODO.md) for the October 2026 review and validation.
