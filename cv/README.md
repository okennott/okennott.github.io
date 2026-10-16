# Curriculum vitae

A Quarto document that renders to `OKOnditi_CV_2026.docx` and `OKOnditi_CV_2026.pdf`.
The publication list and every figure are read from the website's own data, so the CV
and okennott.github.io cannot drift apart.

## Build

```bash
cd cv
python build.py            # both formats
python build.py --no-pdf   # Word only
```

Needs [Quarto](https://quarto.org), `python-docx`, a Python Jupyter kernel (`jupyter`), and LibreOffice (or Word) for the
PDF step. Output goes next to the source.

## How it fits together

| File | Role |
| --- | --- |
| `cv.qmd` | The document. Static sections are plain markdown; the computed ones are Python chunks. **Edit this.** |
| `design.py` | Every font, size, colour and indent, in one place. |
| `make_reference.py` | Turns `design.py` into `reference.docx`, the Word style sheet Pandoc applies. |
| `render_helpers.py` | Emits the computed sections — header, key-figures band, publications, peer review, referees. |
| `cvdata.py` | Reads `../OKOs_Library.json` and `../assets/data/scholar-stats.json`, cross-checks against Crossref. |
| `filters/cvstyle.lua` | Maps the `::: {.entry}` syntax onto the named Word styles. |
| `crossref-cache.json` | Cached Crossref metadata, so a render works offline and is reproducible. |

The PDF is converted from the Word file rather than rendered through LaTeX. That way
there is one design and one layout engine, and the two outputs cannot disagree.

## Editing

Most sections are ordinary markdown. An entry is a date in the left gutter, a bold
title, an italic affiliation line, then body text and optional bullets:

```markdown
::: {.entry date="Jul 2022 – Present"}
Special Research Assistant

*Kunming Institute of Zoology, Chinese Academy of Sciences · Kunming, China*

- Lead integrative research on ...
:::
```

Use `.labelled` instead of `.entry` for a label/value row whose value is not a bold
title (skills, societies, peer review). `## A Heading` becomes a bronze ruled section.

To change how something *looks*, edit `design.py`, not the .qmd.

## After publishing a paper

1. Add it to `../OKOs_Library.json` (export from Zotero).
2. `python cvdata.py --refresh` to pull its Crossref record into the cache.
3. `python build.py`.
4. From the repository root, `python scripts/refresh_static.py` to refresh the website fallbacks.

Cache refresh preserves previously verified metadata if Crossref is temporarily
unavailable, and reports failures. Missing new records still need a successful lookup
or a verified cache entry before they can appear in the downloadable CV.

Numbering, counts, the first-author tally and the metrics strip all follow
automatically. Errata and duplicate preprint postings are excluded by the lists at the
top of `cvdata.py`; a paper whose DOI is not in Crossref goes in `MANUAL` there.

## Accepted papers that have no DOI yet

A library record with no DOI and `status: accepted; accepted: YYYY-MM-DD` in its Zotero
note is read by `accepted_records()` in `cvdata.py`. It prints first in the article list
as "(in press)" with the acceptance date, and it is included in the article count (the
note under the key figures says how many are in press). Nothing is looked up for it, so
it shows no volume, pages or DOI. When the paper appears, add its DOI to Zotero, remove
the `status:` line, export the library, and follow "After publishing a paper"; it then
takes its place in the dated list.

## Refreshing the citation figures

Google Scholar often blocks GitHub Actions runners. The daily workflow attempts
Scholar and OpenAlex, retaining the last verified snapshot when a source is blocked.
Scholar's public table is read without extra dependencies; `scholarly` is an optional fallback.
To update the Scholar numbers, run this from a home connection:

```bash
python ../scripts/fetch_metrics.py
```

Commit `assets/data/scholar-stats.json`, then rebuild. If the Scholar snapshot goes
more than 60 days stale the site — and this CV — fall back to OpenAlex's lower figures
and say so in the provenance line.

## Fonts

The CV uses Cambria (headings) and Calibri (text). Linux has neither, but Caladea and
Carlito are metric-compatible, so a Linux LibreOffice paginates the PDF exactly as Word
does; only glyph shapes differ. `build.py` prefers the Windows LibreOffice when it finds
one, for the real fonts, and says which it used.

## What the CV states, and where it comes from

The generated parts say only what their source supports:

- **Article counts** are computed from the publication list. The list itself is built from
  Crossref records and the Zotero library; the CV does not call it "complete" or
  "verified", because nothing checks the list against every possible source.
- **Citations, h-index, i10-index** come from `assets/data/scholar-stats.json` and are dated
  in the note under the key-figures band.
- **Peer review** is reported as ORCID *review records*. ORCID stores one record per review
  event, which is not necessarily one per manuscript. If every record is a distinct
  manuscript, change `REVIEW_NOUN` and `REVIEW_LABEL` in `render_helpers.py`.
- **Titles** are as published, except six that Crossref holds in Title Case; `CASE_ONLY` in
  `cvdata.py` sets those in sentence case and asserts that only capitalisation changed.

The audit of the 2026-10-04 revision, with the points still needing the author's
confirmation, is in `_review/CV_review_2026-10-04.md`; the pre-revision files are in
`_review/before/`.

## A note on the referees

This is a public repository, so `SHOW_REFEREE_EMAILS` in `render_helpers.py` is `False`:
the CV prints names, titles and institutions and "contact details are available on
request". Set it to `True` to build a private copy that includes the addresses (the
addresses stay listed in `REFEREES`).
