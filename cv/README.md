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

Needs [Quarto](https://quarto.org), `python-docx`, and LibreOffice (or Word) for the
PDF step. Output goes next to the source.

## How it fits together

| File | Role |
| --- | --- |
| `cv.qmd` | The document. Static sections are plain markdown; the computed ones are Python chunks. **Edit this.** |
| `design.py` | Every font, size, colour and indent, in one place. |
| `make_reference.py` | Turns `design.py` into `reference.docx`, the Word style sheet Pandoc applies. |
| `render_helpers.py` | Emits the computed sections — header, metrics, publications, peer review, referees. |
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

Numbering, counts, the first-author tally and the metrics strip all follow
automatically. Errata and duplicate preprint postings are excluded by the lists at the
top of `cvdata.py`; a paper whose DOI is not in Crossref goes in `MANUAL` there.

## Refreshing the citation figures

Google Scholar blocks GitHub Actions runners, so the weekly workflow only refreshes
OpenAlex. To update the Scholar numbers, run this from a home connection:

```bash
pip install scholarly
python ../scripts/fetch_metrics.py
```

Commit `assets/data/scholar-stats.json`, then rebuild. If the Scholar snapshot goes
more than 60 days stale the site — and this CV — fall back to OpenAlex's lower figures
and say so in the provenance line.

## Fonts

The CV asks for Georgia and Calibri. Linux has neither, so a Linux LibreOffice quietly
substitutes Noto Serif and Carlito and the PDF will not match what Word shows.
`build.py` prefers the Windows LibreOffice for that reason and warns if it falls back.

## A note on the referees

`render_helpers.py` lists four referees with their email addresses, and this is a
public repository. Set `SHOW_REFEREE_EMAILS = False` there to render a variant that
keeps the names, titles and institutions but drops the addresses.
