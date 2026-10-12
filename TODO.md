# Repository review and publication update — 11 October 2026

## Findings and implementation plan

- [x] Review repository status, local links, publication data flow and existing checks. Baseline: eight Python tests and the JavaScript metrics checks pass; local HTML asset links resolve. The existing untracked `Claude outputs/` folder is outside this change.
- [x] Retrieve DOI `10.1016/j.ympev.2026.108749` from Crossref. Verified title, all 12 authors, journal, October 2026 date and article number 108749; volume, issue and abstract are absent from the deposit.
- [x] Add the verified publication to the CSL library and CV metadata cache; save a source-backed extraction note.
- [x] Synchronize publication totals, static publication cards and homepage highlights with the library, retaining author-copy links. At review start the fallback had 35 cards versus 42 library records; both now include all 43 records.
- [x] Preserve previous CV metadata when Crossref requests fail; add a regression check for partial outages.
- [x] Fix inconsistent preprint classification, correction filtering, missing Nectogale italics and malformed-fragment handling; verify publication rendering.
- [x] Make navigation expansion state accessible and keep page content visible without JavaScript.
- [x] Correct stale repository/setup instructions and citation-source descriptions; provide a repeatable fallback refresh and CI checks.
- [x] Rebuild downloadable Word/PDF CVs and validate publication data, local links, desktop/mobile rendering and offline fallbacks.

## Scope

Implement locally without committing or pushing. Preserve the dated citation and ORCID snapshots; updating the bibliography does not constitute a new remote metrics observation. Do not invent missing publication fields or attach an unverified PDF.

## Validation results

- Nine Python regression tests passed, including preservation of cached CV records during a partial Crossref outage. Both JavaScript suites passed.
- Static refresh is repeatable (`--check` passes); all 43 library records have fallback cards and all 36 existing author-copy links are preserved.
- Final checks on 12 October also simulated a new library record and stale Scholar data: counts reconciled, citation snapshots were preserved, source links followed the selected index, and `--check` made no writes. The final CV publication page was visually inspected.
- Local HTML links, fragments, navigation targets and IDs passed validation. Library totals agree with the saved metrics: 40 peer-reviewed articles (including one accepted/in press), two preprints and one correction.
- Headless Chrome verified desktop rendering, the new DOI deep link, abstract toggling, preprint filtering and homepage totals. All six main pages fit a 390px mobile viewport. Navigation ARIA state follows opening/closing. No JavaScript errors occurred.
- With the bibliography request blocked, all 43 cards remain available. With JavaScript disabled, homepage highlights stay visible and publication PDF links remain accessible.
- Word and six-page PDF CV rebuilt using Quarto and Windows LibreOffice. PDF text includes the new paper and the corrected total. Missing volume metadata no longer automatically claims advance-online status.
- `git diff --check` passed. No commit or push performed; the pre-existing `Claude outputs/` folder was preserved.

## Source limitations and later maintenance

Crossref has no abstract, volume or issue for the new DOI. Elsevier's API was rate-limited and its web page did not expose the article content to this session. Access is labelled unverified and no new PDF was attached. Recheck these fields when the publisher metadata becomes available, and retain this new record in the reference manager before a future Zotero export. Browser tests blocked external APIs deliberately to verify deterministic fallbacks; they do not establish current live API availability.
