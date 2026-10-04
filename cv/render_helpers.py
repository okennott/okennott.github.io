# -*- coding: utf-8 -*-
"""Markdown emitters for the computed parts of cv.qmd.

Each function prints Pandoc markdown; the chunks that call them use
`#| output: asis`. Everything here is either derived from the website's data or
too repetitive to hand-write. Static content lives in cv.qmd itself.
"""
import re
from datetime import date
from xml.sax.saxutils import escape as xml_escape

import design as D

# Kenneth's contact details and profile links.
CONTACT = ["kenotieno@hotmail.com", "+254 722 620075", "18436–00100 GPO, Nairobi, Kenya"]
LINKS = [("okennott.github.io", "https://okennott.github.io/"),
         ("ORCID 0000-0003-4034-6818", "https://orcid.org/0000-0003-4034-6818"),
         ("Google Scholar", "https://scholar.google.com/citations?user=qnHYvIIAAAAJ&hl=en")]

# Referees. The CV is published, so the default is names, titles and institutions
# only. Set to True to add their email addresses for a private copy.
SHOW_REFEREE_EMAILS = False
REFEREES = [
    ("Prof. Jiang Xuelong", "Principal Investigator",
     "Kunming Institute of Zoology, Chinese Academy of Sciences · Kunming, China",
     "jiangxl@mail.kiz.ac.cn"),
    ("Dr. Esther Kioko", "Senior Research Scientist",
     "National Museums of Kenya · Nairobi, Kenya", "ekioko@museums.or.ke"),
    ("Dr. Julian Kerbis Peterhans", "Curator",
     "Field Museum of Natural History · Chicago, USA", "jkerbis@fieldmuseum.org"),
    ("Dr. Simon Musila", "Senior Research Scientist & Head, Mammalogy Section",
     "National Museums of Kenya · Nairobi, Kenya", "smusila@museums.or.ke"),
]

# What the ORCID peer-review count counts. ORCID stores one record per review
# event, which is not necessarily one per manuscript, so the CV says "records".
# Change both to "manuscripts reviewed" only if every record is a distinct manuscript.
REVIEW_NOUN = "review records"
REVIEW_LABEL = "Peer-review records"      # label in the key-figures band

# Preprint servers, from the DOI prefix.
PREPRINT_SERVERS = {"10.2139": "SSRN", "10.21203": "Research Square"}

# Genus-group names appearing in the titles, so they can be italicised. Families
# and tribes are deliberately absent: only genus and below are italicised.
GENERA = ["Anourosorex", "Chodsigoa", "Episoriculus", "Graphiurus", "Lemniscomys",
          "Lophuromys", "Mesechinus", "Micromys", "Neodon", "Uropsilus"]
EPITHETS = ["flavopunctatus", "hypsibia", "squamipes", "aquilus"]
TAXON = re.compile(r"\b(?:(?:%s)\s+(?:%s)|(?:%s))\b"
                   % ("|".join(GENERA), "|".join(EPITHETS), "|".join(GENERA)))

NB = " "
SEP = f'[{NB*3}·{NB*3}]{{custom-style="CVSep"}}'


def _div(style, body):
    print(f'\n::: {{custom-style="{style}"}}\n{body}\n:::\n')


def esc(text):
    """Escape the few characters Pandoc would otherwise read as markup."""
    return re.sub(r"([*_\[\]])", r"\\\1", text)


def italicise_taxa(text):
    out, pos = [], 0
    for m in TAXON.finditer(text):
        out.append(esc(text[pos:m.start()]))
        out.append(f"*{m.group(0)}*")
        pos = m.end()
    out.append(esc(text[pos:]))
    return "".join(out)


def long_date(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {date(y, m, d).strftime('%B %Y')}"


def header():
    _div("CVName", "Kenneth Otieno Onditi")
    _div("CVTitle", "Mammal Ecologist & Evolutionary Biologist")
    _div("CVAffil", "Kunming Institute of Zoology, Chinese Academy of Sciences · "
                    "National Museums of Kenya")
    _div("CVContact", SEP.join(CONTACT))
    _div("CVLinks", SEP.join(f"[{t}]({u})" for t, u in LINKS))


# --- key figures -------------------------------------------------------------

def _figure_table(figures):
    """A one-row, shaded table: the number above its label, in each cell."""
    n = len(figures)
    total = int(round(D.TEXT_WIDTH * 1440))
    width = total // n
    rule = f'w:val="single" w:sz="4" w:space="0" w:color="{D.RULE}"'

    def run(text, font, half_points, color, bold=False, caps=False, spacing=0):
        rpr = (f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}"/>'
               + ("<w:b/>" if bold else "") + ("<w:caps/>" if caps else "")
               + f'<w:color w:val="{color}"/>'
               + (f'<w:spacing w:val="{spacing}"/>' if spacing else "")
               + f'<w:sz w:val="{half_points}"/>')
        return f'<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{xml_escape(text)}</w:t></w:r>'

    def para(inner, before, after):
        return (f'<w:p><w:pPr><w:keepNext/><w:spacing w:before="{before}" w:after="{after}"/>'
                f'<w:jc w:val="center"/></w:pPr>{inner}</w:p>')

    cells = []
    for i, (label, value) in enumerate(figures):
        left = f'<w:left {rule}/>' if i else ""
        cells.append(
            f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/>'
            f'<w:tcBorders>{left}</w:tcBorders><w:vAlign w:val="center"/></w:tcPr>'
            + para(run(str(value), D.SERIF, 34, D.BRONZE, bold=True), 60, 0)
            + para(run(label, D.SANS, 15, D.MUTED, caps=True, spacing=6), 0, 60)
            + '</w:tc>')
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for _ in figures)
    return (f'<w:tbl><w:tblPr><w:tblW w:w="{width * n}" w:type="dxa"/>'
            f'<w:tblBorders><w:top {rule}/><w:bottom {rule}/></w:tblBorders>'
            f'<w:shd w:val="clear" w:color="auto" w:fill="{D.BAND}"/>'
            '<w:tblLayout w:type="fixed"/>'
            '<w:tblCellMar><w:left w:w="40" w:type="dxa"/><w:right w:w="40" w:type="dxa"/></w:tblCellMar>'
            f'</w:tblPr><w:tblGrid>{grid}</w:tblGrid><w:tr><w:trPr><w:cantSplit/></w:trPr>'
            f'{"".join(cells)}</w:tr></w:tbl>')


def metrics(M, P):
    arts = [p for p in P if not p["preprint"]]
    inpress = sum(1 for p in arts if p["year"] is None)
    figures = [
        ("Peer-reviewed articles", len(arts)),
        ("First-author articles", sum(1 for p in arts if p["npos"] == 1)),
        ("Citations", M["citations"]),
        ("h-index", M["h_index"]),
        ("i10-index", M["i10_index"]),
        (REVIEW_LABEL, M["peer_reviews"]),
    ]
    print("\n```{=openxml}\n" + _figure_table(figures) + "\n```\n")

    source = "Google Scholar" if M["citation_source"] == "scholar" else "OpenAlex"
    review_date = M.get("peer_review_as_of") or M["last_updated"]
    _div("CVNote",
         f"Citation figures: {source}, {long_date(M['citation_as_of'])}. "
         f"Review records: ORCID, {long_date(review_date)}. "
         "Articles: publication list below"
         + (f" ({inpress} in press)." if inpress else "."))


# --- publications ------------------------------------------------------------

def _citation(rec, number):
    names = []
    for i, a in enumerate(rec["authors"]):
        if i:
            names.append(", " if i < len(rec["authors"]) - 1 else " & ")
        names.append(f"**{esc(a['text'])}**" if a["me"] else esc(a["text"]))
    in_press = rec["year"] is None
    line = [f'[{number}.]{{custom-style="CVNum"}}[]{{.tab}}',
            "".join(names), " (in press). " if in_press else f" ({rec['year']}). ",
            italicise_taxa(rec["title"]), ". "]

    if in_press:
        line.append(f"*{esc(rec['journal'])}*. ")
        if rec["accepted"]:
            line.append(f"Accepted for publication {long_date(rec['accepted'])}. ")
        _div("CVPub", "".join(line).rstrip())
        return
    if rec["preprint"]:
        server = PREPRINT_SERVERS.get(rec["doi"].split("/")[0])
        line.append(f"*{server}* (preprint). " if server else "*Preprint*. ")
    else:
        line.append(f"*{esc(rec['journal'])}*")
        volume = rec["volume"] if rec["volume"] not in (None, "0") else None
        where = ""
        if volume:
            where = ", " + volume
            if rec["issue"] and rec["issue"] != "0":
                where += f"({rec['issue']})"
        pages = rec["page"] if rec["page"] not in (None, "0-0") else rec["artno"]
        if pages:
            where += ", " + pages.replace("-", "–")
        line.append(where + ". ")
        if not volume:
            line.append("*Advance online publication*. ")
    line.append(f"[doi:{rec['doi']}](https://doi.org/{rec['doi']})")
    _div("CVPub", "".join(line))


def publications(P):
    _div("CVPubNote", "Author's name in bold. Reverse chronological, numbered from the "
                      "earliest. Bibliographic details are taken from Crossref records and "
                      "the author's reference library; titles are as published. Accepted articles "
                      "that have no DOI yet are listed from the library alone.")
    articles = [p for p in P if not p["preprint"]]
    preprints = [p for p in P if p["preprint"]]

    _div("CVSubhead", f"Peer-reviewed journal articles ({len(articles)})")
    for i, rec in enumerate(articles):
        _citation(rec, len(articles) - i)

    _div("CVSubhead", f"Preprints ({len(preprints)})")
    for i, rec in enumerate(preprints):
        _citation(rec, len(preprints) - i)


# --- service -----------------------------------------------------------------

def _journal_groups(breakdown):
    """Journals grouped by number of reviews: 'A (15); B (12)', then 'Three each: ...'."""
    by_count = {}
    for j in breakdown:
        by_count.setdefault(j["reviews"], []).append(j["name"])
    words = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}
    singles = [(n, sorted(names)) for n, names in by_count.items() if n >= 4]
    lines = []
    if singles:
        items = [f"{esc(name)} ({n})" for n, names in sorted(singles, reverse=True)
                 for name in names]
        lines.append("; ".join(items))
    for n in sorted((n for n in by_count if n < 4), reverse=True):
        lines.append(f"{words[n]} each: " + "; ".join(esc(x) for x in sorted(by_count[n])))
    return lines


def peer_review(M):
    review_date = M.get("peer_review_as_of") or M["last_updated"]
    print(f'\n::: {{.labelled date="Peer review"}}\n'
          f"{M['peer_reviews']} {REVIEW_NOUN} for {M['peer_review_journals']} journals, "
          f"{M['peer_review_first_year']}–{M['peer_review_latest_year']} "
          f"(ORCID, {long_date(review_date)}).\n:::\n")
    for line in _journal_groups(M["peer_review_breakdown"]):
        _div("CVLabelNote", line)


def labelled(rows):
    for label, text in rows:
        print(f'\n::: {{.labelled date="{label}"}}\n{text}\n:::\n')


def referees():
    for name, role, institution, email in REFEREES:
        _div("CVRefName", f'{esc(name)}[{NB*2}·{NB*2}{esc(role)}]{{custom-style="CVMuted"}}')
        _div("CVRefOrg", esc(institution))
        if SHOW_REFEREE_EMAILS:
            _div("CVContact", f"[{email}](mailto:{email})")
    if not SHOW_REFEREE_EMAILS:
        _div("CVNote", "Referee contact details are available on request.")
