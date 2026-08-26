#!/usr/bin/env python3
"""Collect publication and citation metrics for K.O. Onditi.

Sources, in order of trust per field:

  ORCID     pub.orcid.org        peer-reviewed works, preprints, first year
  OpenAlex  api.openalex.org     citations, h-index, i10-index, works count
  Scholar   scholarly (scraped)  citations, h-index, i10-index, 5-year splits

ORCID and OpenAlex use the standard library only, so the critical path needs no
pip install and cannot be broken by a dependency. Google Scholar has no API and
blocks datacentre IPs, so it is strictly best-effort: time-boxed, never fatal,
and only allowed to *raise* a metric that OpenAlex already established.

The script never destroys good data. Every field falls back to the value already
in scholar-stats.json, and implausible drops in cumulative metrics are rejected
(a scraper returning 0 is a scraper failure, not a citation count).

Exit status is 0 whenever a usable file could be written; 1 only if every source
failed AND there was no previous file to fall back on.
"""

import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request

ORCID_ID   = "0000-0003-4034-6818"
SCHOLAR_ID = "qnHYvIIAAAAJ"
CONTACT    = "kenotieno08@gmail.com"          # OpenAlex polite pool
USER_AGENT = f"okennott.github.io metrics bot (mailto:{CONTACT})"

HERE     = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "..", "assets", "data", "scholar-stats.json")
LIB_PATH = os.path.join(HERE, "..", "OKOs_Library.json")

HTTP_TIMEOUT    = 30      # seconds per request
HTTP_RETRIES    = 3
SCHOLAR_TIMEOUT = 120     # hard ceiling on the Google Scholar attempt
DROP_TOLERANCE  = 0.85    # reject a cumulative metric below 85% of its last value

STALE_AFTER_DAYS = 60     # after this, a Scholar snapshot stops being displayed

# Work counts only ever grow in practice, so a fall is a bad fetch, not news.
MONOTONIC = {"peer_reviewed_works", "works_total", "preprints"}

# Citation metrics are kept together as one per-source snapshot.
PROFILE_FIELDS = (
    "citations", "h_index", "i10_index",
    "citations_since_2021", "h_index_since_2021", "i10_index_since_2021",
)


def log(msg):
    print(msg, flush=True)


def get_json(url, headers=None):
    """GET a URL and parse JSON, retrying transient failures with backoff."""
    req_headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if headers:
        req_headers.update(headers)
    last_error = None
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers=req_headers)
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, ValueError, OSError) as exc:
            last_error = exc
            if attempt < HTTP_RETRIES:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"{url} failed after {HTTP_RETRIES} attempts: {last_error}")


# ── Sources ────────────────────────────────────────────────────────────────

def from_library():
    """The curated Zotero export in this repo — what the site actually lists.

    ORCID lags by weeks while a new paper is being deposited, so the site would
    otherwise show a peer-review count lower than the list printed beneath it.
    Reconciling here, once, keeps every page agreeing without each page having
    to fetch and count the bibliography itself.
    """
    with open(LIB_PATH, encoding="utf-8") as fh:
        items = [i for i in json.load(fh) if i and i.get("title")]
    if not items:
        raise RuntimeError("library is empty")

    def is_preprint(item):
        return (item.get("type") == "preprint"
                or "preprint" in (item.get("note") or "").lower()
                or "preprint" in (item.get("container-title") or "").lower())

    preprints = [i for i in items if is_preprint(i)]
    years = []
    for item in items:
        try:
            years.append(int(item["issued"]["date-parts"][0][0]))
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    stats = {
        "library_records":       len(items),
        "library_peer_reviewed": len(items) - len(preprints),
        "library_preprints":     len(preprints),
    }
    if years:
        stats["year_span"] = len(set(years))
    return stats



def from_orcid():
    """Authoritative record of the works themselves — the peer-review count."""
    data = get_json(f"https://pub.orcid.org/v3.0/{ORCID_ID}/works")
    groups = data.get("group") or []
    if not groups:
        raise RuntimeError("ORCID returned no work groups")

    counts, years = {}, []
    for group in groups:
        summaries = group.get("work-summary") or []
        if not summaries:
            continue
        summary = summaries[0]
        counts[summary.get("type") or "unknown"] = counts.get(summary.get("type") or "unknown", 0) + 1
        year = ((summary.get("publication-date") or {}).get("year") or {}).get("value")
        if year and str(year).isdigit():
            years.append(int(year))

    peer_reviewed = counts.get("journal-article", 0) + counts.get("book-chapter", 0)
    stats = {
        "peer_reviewed_works": peer_reviewed,
        "preprints":           counts.get("preprint", 0),
        "works_total":         len(groups),
    }
    if years:
        stats["first_year"] = min(years)
        stats["latest_year"] = max(years)
    log(f"  ORCID types: {counts}")
    return stats


def from_openalex():
    """Citations and indices — reliable, CORS-open, and never rate-limits us."""
    data = get_json(
        f"https://api.openalex.org/authors/orcid:{ORCID_ID}?mailto={CONTACT}"
    )
    summary = data.get("summary_stats") or {}
    stats = {
        "citations":  data.get("cited_by_count"),
        "h_index":    summary.get("h_index"),
        "i10_index":  summary.get("i10_index"),
        "openalex_works": data.get("works_count"),
        "openalex_id": data.get("id"),
    }
    if all(stats.get(k) is None for k in ("citations", "h_index", "i10_index")):
        raise RuntimeError("OpenAlex returned no usable metrics")
    return stats


def from_scholar():
    """Best-effort scrape. Google Scholar blocks CI runners most of the time."""
    if os.environ.get("SKIP_SCHOLAR") == "1":
        raise RuntimeError("skipped via SKIP_SCHOLAR=1")

    result = {}
    error = {}

    def worker():
        try:
            from scholarly import scholarly
            author = scholarly.search_author_id(SCHOLAR_ID)
            author = scholarly.fill(author, sections=["basics", "indices"])
            result.update({
                "citations":            author.get("citedby"),
                "citations_since_2021": author.get("citedby5y"),
                "h_index":              author.get("hindex"),
                "h_index_since_2021":   author.get("hindex5y"),
                "i10_index":            author.get("i10index"),
                "i10_index_since_2021": author.get("i10index5y"),
            })
        except BaseException as exc:                      # noqa: BLE001 - never fatal
            error["exc"] = exc

    # Daemon thread: if scholarly wedges in a retry loop we abandon it and exit.
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    thread.join(SCHOLAR_TIMEOUT)

    if thread.is_alive():
        raise RuntimeError(f"timed out after {SCHOLAR_TIMEOUT}s (likely IP-blocked)")
    if error:
        raise RuntimeError(f"{type(error['exc']).__name__}: {error['exc']}")
    if not result:
        raise RuntimeError("returned nothing")
    return result


# ── Merge with guards ─────────────────────────────────────────────────────

def load_previous():
    try:
        with open(OUT_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def sane_count(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def accept_work_counts(values, previous):
    """Work counts from ORCID. Reject zeros and implausible collapses."""
    taken, rejected = {}, {}
    for key, value in values.items():
        if isinstance(value, str):
            if value.strip():
                taken[key] = value
            continue
        if not sane_count(value):
            rejected[key] = value
            continue
        if key in MONOTONIC:
            if value == 0:
                rejected[key] = value                       # 0 means a failed fetch
                continue
            old = previous.get(key)
            if sane_count(old) and value < old * DROP_TOLERANCE:
                rejected[key] = value                       # implausible collapse
                continue
        taken[key] = value
    return taken, rejected


def accept_profile(name, values, previous_profiles):
    """Citation metrics are taken as a coherent bundle from a single source.

    Scholar and OpenAlex index different corpora, so Scholar's numbers are always
    higher. Mixing them field by field would show one source's citation count next
    to another's h-index. Instead each source keeps its own snapshot, and a whole
    snapshot is rejected if it collapses against that same source's last reading.
    """
    profile = {k: values.get(k) for k in PROFILE_FIELDS if values.get(k) is not None}
    if not all(sane_count(profile.get(k)) for k in ("citations", "h_index", "i10_index")):
        return None, "incomplete (missing citations/h-index/i10)"
    if profile["citations"] == 0:
        return None, "citations=0 (failed scrape)"

    old = (previous_profiles or {}).get(name) or {}
    for key in ("citations", "h_index", "i10_index"):
        prior = old.get(key)
        if sane_count(prior) and profile[key] < prior * DROP_TOLERANCE:
            return None, f"{key} fell {prior} -> {profile[key]} (implausible)"

    profile["as_of"] = time.strftime("%Y-%m-%d")
    return profile, None


def choose_profile(profiles):
    """Prefer Google Scholar while it is fresh; otherwise use OpenAlex.

    Scholar has the broadest coverage and is what the numbers on an academic CV
    normally refer to, but it goes stale when the scrape is blocked. Once a
    Scholar snapshot is older than STALE_AFTER_DAYS we display OpenAlex instead,
    so the site never silently shows a year-old figure as if it were current.
    """
    today = time.strftime("%Y-%m-%d")
    scholar = profiles.get("scholar")
    if scholar and scholar.get("as_of"):
        age = days_between(scholar["as_of"], today)
        if age is not None and age <= STALE_AFTER_DAYS:
            return "scholar", scholar
    if profiles.get("openalex"):
        return "openalex", profiles["openalex"]
    if scholar:
        return "scholar", scholar
    return None, {}


def days_between(earlier, later):
    try:
        fmt = "%Y-%m-%d"
        return int((time.mktime(time.strptime(later, fmt))
                    - time.mktime(time.strptime(earlier, fmt))) // 86400)
    except (ValueError, TypeError, OverflowError):
        return None


def main():
    previous = load_previous()
    if previous:
        log(f"Previous file: {json.dumps(previous, sort_keys=True)}\n")

    profiles = dict(previous.get("citation_profiles") or {})
    if not profiles and sane_count(previous.get("citations")):
        # Migrate the old flat schema: those numbers came from the Scholar scrape.
        profiles["scholar"] = {k: previous[k] for k in PROFILE_FIELDS if k in previous}
        profiles["scholar"]["as_of"] = previous.get("last_updated") or "1970-01-01"
        log(f"Migrated legacy flat stats into a scholar snapshot: {profiles['scholar']}\n")
    works, provenance, healthy = {}, {}, []

    # The bibliography shipped with the site.
    log("Reading local library...")
    try:
        library = from_library()
        works.update(library)
        healthy.append("library")
        provenance["library"] = "ok"
        log(f"  {library}")
    except Exception as exc:                                # noqa: BLE001
        library = {}
        provenance["library"] = "unavailable"
        log(f"  unavailable: {exc}")

    # ORCID — the external record of the works themselves.
    log("Fetching orcid...")
    try:
        values = from_orcid()
        taken, rejected = accept_work_counts(values, previous)
        works.update(taken)
        healthy.append("orcid")
        provenance["orcid"] = "ok"
        log(f"  accepted: {taken}")
        if rejected:
            log(f"  REJECTED (kept previous): {rejected}")
    except Exception as exc:                                # noqa: BLE001
        provenance["orcid"] = "unavailable"
        log(f"  unavailable: {exc}")

    # Citation profiles — each source snapshotted independently.
    for name, fetch in (("openalex", from_openalex), ("scholar", from_scholar)):
        log(f"Fetching {name}...")
        try:
            values = fetch()
        except Exception as exc:                            # noqa: BLE001
            provenance[name] = "unavailable"
            log(f"  unavailable: {exc}")
            continue
        provenance[name] = "ok"
        healthy.append(name)
        if name == "openalex" and sane_count(values.get("openalex_works")):
            works["openalex_works"] = values["openalex_works"]
        if values.get("openalex_id"):
            works["openalex_id"] = values["openalex_id"]

        profile, why = accept_profile(name, values, profiles)
        if profile:
            profiles[name] = profile
            log(f"  snapshot: {profile}")
        else:
            log(f"  REJECTED snapshot ({why}) — keeping {profiles.get(name, 'nothing')}")

    if not healthy:
        if previous:
            log("\nAll sources failed — leaving the existing file untouched.")
            return 0
        log("\nAll sources failed and there is no previous file.")
        return 1

    active_name, active = choose_profile(profiles)

    # Reconcile the ORCID count with the bibliography. ORCID is the authority on
    # what counts as published; the library is simply ahead while a deposit is
    # pending, so the larger of the two is the honest current figure.
    orcid_count = works.get("peer_reviewed_works")
    lib_count = works.get("library_peer_reviewed")
    if sane_count(orcid_count):
        works["orcid_peer_reviewed"] = orcid_count
    if sane_count(orcid_count) and sane_count(lib_count):
        works["peer_reviewed_works"] = max(orcid_count, lib_count)
        works["works_pending_in_orcid"] = max(0, lib_count - orcid_count)
    elif sane_count(lib_count) and not sane_count(orcid_count):
        works["peer_reviewed_works"] = lib_count

    out = dict(works)
    out["citation_profiles"] = profiles
    if active:
        out["citations"] = active["citations"]
        out["h_index"] = active["h_index"]
        out["i10_index"] = active["i10_index"]
        out["citation_source"] = active_name
        out["citation_as_of"] = active.get("as_of")
    out["sources"] = provenance
    out["last_updated"] = time.strftime("%Y-%m-%d")
    out["orcid_id"] = ORCID_ID
    out["scholar_id"] = SCHOLAR_ID

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, sort_keys=True)
        fh.write("\n")

    log(f"\nWrote {OUT_PATH}")
    log(json.dumps(out, indent=2, sort_keys=True))
    log(f"\nHealthy sources: {', '.join(healthy)} | displaying citations from: {active_name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
