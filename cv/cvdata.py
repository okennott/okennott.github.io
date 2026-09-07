# -*- coding: utf-8 -*-
"""Data layer for cv.qmd.

Publications come from the website's own bibliography (`../OKOs_Library.json`),
with every field cross-checked against Crossref; the citation and peer-review
figures come from `../assets/data/scholar-stats.json`, which is what the website
displays. So the CV cannot disagree with the site.

Crossref responses are cached in `crossref-cache.json` so a render works offline
and is reproducible. Refresh after adding a paper:

    python cvdata.py --refresh
"""
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LIBRARY = os.path.join(REPO, "OKOs_Library.json")
STATS = os.path.join(REPO, "assets", "data", "scholar-stats.json")
CACHE = os.path.join(HERE, "crossref-cache.json")

CONTACT_MAIL = "kenotieno08@gmail.com"      # Crossref polite pool
CACHE_FIELDS = ("title", "container-title", "short-container-title", "volume", "issue",
                "page", "article-number", "author", "type", "published", "issued")

# --- corrections to what the sources return ---------------------------------
# Crossref returns family/given swapped on some bilingual deposits, so these
# records take their author lists from the curated Zotero library instead.
USE_LIBRARY_AUTHORS = {
    "10.24272/j.issn.2097-3772.2023.005", "10.24272/j.issn.2095-8137.2019.004",
    "10.24272/j.issn.2097-3772.2025.030", "10.24272/j.issn.2095-8137.2020.085",
    "10.24272/j.issn.2097-3772.2024.011", "10.24272/j.issn.2095-8137.2026.291",
    "10.1007/s13364-019-00470-1",
}
# Year of the issue of record, where Crossref reports the online-first date.
YEAR_OVERRIDE = {
    "10.1093/sysbio/syaf052": 2026,          # Syst Biol 75(2), March 2026 (verified at OUP)
    "10.1007/s13364-019-00470-1": 2020,      # Mammal Res 65(2), 2020
    "10.24272/j.issn.2095-8137.2019.004": 2019,
}
TITLE_OVERRIDE = {
    # Crossref deposit typo ("mplications"); the Zotero record has it right.
    "10.1016/j.biocon.2024.110863":
        "Spatiotemporal distribution patterns of large and medium-sized mammals in a "
        "biodiversity hotspot: Implications for conservation",
    # Crossref holds only the Chinese titles for these.
    "10.24272/j.issn.2097-3772.2023.005":
        "The mammals of Gaoligong Mountain in China: diversity, distribution, and conservation",
    "10.24272/j.issn.2097-3772.2024.011":
        "A new species of mountain vole (Rodentia, Cricetidae, Neodon) from south Xizang, China",
    "10.24272/j.issn.2095-8137.2019.004":
        "Diversity and distribution patterns of non-volant small mammals along different "
        "elevation gradients on Mt. Kenya, Kenya",
}
JOURNAL_OVERRIDE = {"10.24272/j.issn.2095-8137.2019.004": "Zoological Research"}
# Errata and duplicate preprint postings of papers already listed.
EXCLUDE = {
    "10.1007/s13364-019-00475-w",        # erratum to 10.1007/s13364-019-00470-1
    "10.2139/ssrn.5179250",              # preprint of 10.1016/j.gecco.2025.e03854
    "10.21203/rs.3.rs-2677031/v1",       # preprint of 10.1007/s10531-023-02766-w
    "10.21203/rs.3.rs-157741/v1",        # preprint of 10.1186/s12862-021-01813-w
    "10.6084/m9.figshare.25975360",      # dataset, not a publication
    "10.2139/ssrn.4876387",              # superseded by 10.1016/j.biocon.2024.110863
}
# Not in Crossref or OpenAlex: the DOI is on the Chinese registry (chndoi.org).
# Verified to resolve, and deposited in ORCID by Scopus.
MANUAL = [{
    "doi": "10.16829/j.slxb.150613", "year": 2022, "preprint": False,
    "title": "Methodological advances in explaining community assembly with niche-based theory",
    "journal": "Acta Theriologica Sinica", "volume": "42", "issue": "3",
    "page": "312-324", "artno": None, "npos": 3, "nauth": 4,
    "authors": [{"text": "Song, W.-Y.", "me": False}, {"text": "Li, X.-Y.", "me": False},
                {"text": "Onditi, K. O.", "me": True}, {"text": "Jiang, X.-L.", "me": False}],
}]

NORM = {"‐": "-", "‑": "-", " ": " ", "­": "", "﻿": ""}


def norm_chars(text):
    for a, b in NORM.items():
        text = text.replace(a, b)
    return text


def clean(text):
    text = norm_chars(re.sub(r"<[^>]+>", "", html.unescape(text or "")))
    return re.sub(r"\s+", " ", text).strip()


def bare_doi(value):
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", (value or "").strip()).lower()


def initials(given):
    parts = re.split(r"[\s\-]+", (given or "").strip())
    return " ".join(p[0].upper() + "." for p in parts if p and p[0].isalpha())


def format_authors(raw):
    out, seen = [], set()
    for a in raw:
        family, given = norm_chars(a.get("family") or ""), norm_chars(a.get("given") or "")
        if not family and not given:
            continue
        me = "onditi" in family.lower() or "onditi" in given.lower()
        if me:
            family, given = "Onditi", "Kenneth Otieno"
        text = f"{family}, {initials(given)}".strip().rstrip(",")
        if text in seen:            # some deposits repeat an author (e.g. SSRN 7010506)
            continue
        seen.add(text)
        out.append({"text": text, "me": me})
    return out


def _library():
    with open(LIBRARY, encoding="utf-8") as fh:
        return json.load(fh)


def refresh_cache():
    """Re-fetch Crossref for every DOI in the bibliography and store a trimmed copy."""
    dois = {bare_doi(i.get("DOI")) for i in _library() if i.get("DOI")}
    dois |= {"10.2139/ssrn.7010506"}          # in ORCID; kept even if not yet in the library
    dois -= set(MANUAL[0]["doi"] for _ in [0])
    cache, failed = {}, []
    for doi in sorted(d for d in dois if d):
        try:
            req = urllib.request.Request(
                "https://api.crossref.org/works/" + urllib.parse.quote(doi),
                headers={"User-Agent": f"OKO-CV/1.0 (mailto:{CONTACT_MAIL})"})
            msg = json.load(urllib.request.urlopen(req, timeout=40))["message"]
            cache[doi] = {k: msg[k] for k in CACHE_FIELDS if k in msg}
        except Exception as exc:
            failed.append((doi, str(exc)))
        time.sleep(0.15)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False, indent=1, sort_keys=True)
    print(f"cached {len(cache)} Crossref records -> {os.path.relpath(CACHE, REPO)}")
    for doi, err in failed:
        print(f"  not in Crossref: {doi} ({err})")
    return cache


def publications():
    """Every publication, newest first, with Kenneth's author position resolved."""
    with open(CACHE, encoding="utf-8") as fh:
        cache = json.load(fh)
    lib = {bare_doi(i.get("DOI")): i for i in _library() if i.get("DOI")}

    records = []
    for doi, msg in cache.items():
        if doi in EXCLUDE:
            continue
        item = lib.get(doi)
        raw = (item or {}).get("author", []) if doi in USE_LIBRARY_AUTHORS else msg.get("author", [])
        authors = format_authors(raw)
        pos = [i + 1 for i, a in enumerate(authors) if a["me"]]
        parts = (msg.get("published") or msg.get("issued", {})).get("date-parts", [[None]])[0]
        records.append({
            "doi": doi,
            "year": YEAR_OVERRIDE.get(doi, parts[0]),
            "preprint": msg.get("type") == "posted-content",
            "title": TITLE_OVERRIDE.get(doi) or clean((msg.get("title") or [""])[0]),
            "journal": clean(JOURNAL_OVERRIDE.get(doi) or (msg.get("container-title") or [""])[0]),
            "volume": msg.get("volume"), "issue": msg.get("issue"),
            "page": msg.get("page"), "artno": msg.get("article-number"),
            "authors": authors, "npos": pos[0] if pos else None, "nauth": len(authors),
        })
    records += [dict(r) for r in MANUAL]
    records.sort(key=lambda r: (-r["year"], r["authors"][0]["text"]))

    unresolved = [r["doi"] for r in records if r["npos"] is None]
    if unresolved:
        raise SystemExit("author position unresolved for: " + ", ".join(unresolved))
    return records


def metrics():
    with open(STATS, encoding="utf-8") as fh:
        return json.load(fh)


if __name__ == "__main__":
    if "--refresh" in sys.argv:
        refresh_cache()
    recs = publications()
    arts = [r for r in recs if not r["preprint"]]
    print(f"{len(recs)} publications: {len(arts)} peer-reviewed, "
          f"{len(recs) - len(arts)} preprints, "
          f"{sum(1 for r in arts if r['npos'] == 1)} first-author")
