# -*- coding: utf-8 -*-
"""Markdown emitters for the computed parts of cv.qmd.

Each function prints Pandoc markdown; the chunks that call them use
`#| output: asis`. Everything here is either derived from the website's data or
too repetitive to hand-write. Static content lives in cv.qmd itself.
"""
import re
from datetime import date

# Kenneth's contact details and profile links.
CONTACT = ["kenotieno@hotmail.com", "+254 722 620075", "18436–00100 GPO, Nairobi, Kenya"]
LINKS = [("okennott.github.io", "https://okennott.github.io/"),
         ("ORCID 0000-0003-4034-6818", "https://orcid.org/0000-0003-4034-6818"),
         ("Google Scholar", "https://scholar.google.com/citations?user=qnHYvIIAAAAJ&hl=en")]

# Referees. Set to False to publish a variant without their email addresses.
SHOW_REFEREE_EMAILS = True
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

# Genus-group names appearing in the titles, so they can be italicised. Families
# and tribes are deliberately absent: only genus and below are italicised.
GENERA = ["Anourosorex", "Chodsigoa", "Episoriculus", "Graphiurus", "Lemniscomys",
          "Lophuromys", "Mesechinus", "Micromys", "Neodon", "Uropsilus"]
EPITHETS = ["flavopunctatus", "hypsibia", "squamipes", "aquilus"]
TAXON = re.compile(r"\b(?:(?:%s)\s+(?:%s)|(?:%s))\b"
                   % ("|".join(GENERA), "|".join(EPITHETS), "|".join(GENERA)))

NB = "\u00a0"
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


def header():
    _div("CVName", "Kenneth Otieno Onditi")
    _div("CVTitle", "Mammal Ecologist & Evolutionary Biologist")
    _div("CVAffil", "Kunming Institute of Zoology, Chinese Academy of Sciences · "
                    "National Museums of Kenya")
    _div("CVContact", SEP.join(CONTACT))
    _div("CVLinks", SEP.join(f"[{t}]({u})" for t, u in LINKS))


def metrics(M, P):
    arts = [p for p in P if not p["preprint"]]
    figures = [
        ("Peer-reviewed articles", len(arts)),
        ("First-author", sum(1 for p in arts if p["npos"] == 1)),
        ("Preprints", len(P) - len(arts)),
        ("Citations", M["citations"]),
        ("h-index", M["h_index"]),
        ("i10-index", M["i10_index"]),
        ("Manuscripts reviewed", M["peer_reviews"]),
    ]
    _div("CVMetrics", SEP.join(f'[{v}{NB}]{{custom-style="CVBig"}}{k}' for k, v in figures))

    def month(iso):
        y, m, d = (int(x) for x in iso.split("-"))
        return date(y, m, d).strftime("%B %Y")

    source = "Google Scholar" if M["citation_source"] == "scholar" else "OpenAlex"
    _div("CVNote",
         f"Citation metrics from {source}, {month(M['citation_as_of'])}; peer-review "
         f"record from ORCID, {month(M['last_updated'])}. Publication list below is "
         f"complete and verified against Crossref and the journal of record.")


def _citation(rec, number):
    names = []
    for i, a in enumerate(rec["authors"]):
        if i:
            names.append(", " if i < len(rec["authors"]) - 1 else " & ")
        names.append(f"**{esc(a['text'])}**" if a["me"] else esc(a["text"]))
    line = [f'[{number}.]{{custom-style="CVNum"}}[]{{.tab}}',
            "".join(names), f" ({rec['year']}). ", italicise_taxa(rec["title"]), ". "]

    if rec["preprint"]:
        line.append("*Preprint*. ")
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
    _div("CVPubNote", "Name in bold. Reverse chronological; numbered from earliest. "
                   "All entries verified against Crossref and the journal of record.")
    articles = [p for p in P if not p["preprint"]]
    preprints = [p for p in P if p["preprint"]]

    _div("CVSubhead", f"Peer-reviewed journal articles ({len(articles)})")
    for i, rec in enumerate(articles):
        _citation(rec, len(articles) - i)

    _div("CVSubhead", f"Preprints and manuscripts under review ({len(preprints)})")
    for i, rec in enumerate(preprints):
        _citation(rec, len(preprints) - i)


def peer_review(M):
    print(f'\n::: {{.labelled date="Peer review"}}\n'
          f"{M['peer_reviews']} manuscripts reviewed for {M['peer_review_journals']} "
          f"journals, {M['peer_review_first_year']}–{M['peer_review_latest_year']} "
          f"(verified via ORCID).\n:::\n")
    listing = sorted(M["peer_review_breakdown"], key=lambda j: (-j["reviews"], j["name"]))
    _div("CVLabelNote", (NB * 2 + " ").join(f"{esc(j['name'])} ({j['reviews']})"
                                            for j in listing))


def labelled(rows):
    for label, text in rows:
        print(f'\n::: {{.labelled date="{label}"}}\n{text}\n:::\n')


def referees():
    for name, role, institution, email in REFEREES:
        _div("CVRefName", f'{esc(name)}[{NB*2}·{NB*2}{esc(role)}]{{custom-style="CVMuted"}}')
        _div("CVRefOrg", esc(institution))
        if SHOW_REFEREE_EMAILS:
            _div("CVContact", f"[{email}](mailto:{email})")
