# Repository maintenance

These Python and Node tools support the tracked GitHub Actions workflows in
`.github/workflows/`. Jekyll does not publish this underscore-prefixed folder.
Browser-facing JavaScript remains in `assets/js/main.js`.

- `fetch_metrics.py` updates the dated ORCID, Scholar and OpenAlex snapshots.
- `refresh_static.py` regenerates offline HTML from the browser renderer.
- `check_site.py` checks local links and publication data coverage.
- `test_*.py` and `test_*.cjs` check those tools and the browser renderer.
- `requirements.txt` contains the optional HTML-maintenance dependency.

Run the checks from the repository root using the commands in the root README.
The former root `scripts/` directory is ignored and is not used by CI.
