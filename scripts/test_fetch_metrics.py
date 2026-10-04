"""Offline regression checks for source failures and snapshot reconciliation.

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
import contextlib
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fetch_metrics as metrics


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.previous = {
            "peer_reviewed_works": 38, "orcid_peer_reviewed": 36,
            "works_pending_in_orcid": 2, "works_total": 42, "preprints": 2,
            "library_records": 41, "library_peer_reviewed": 38,
            "library_preprints": 2, "library_corrections": 1, "year_span": 8,
            "orcid_as_of": "2026-09-07", "peer_review_as_of": "2026-09-07",
            "peer_reviews": 76, "peer_review_journals": 1,
            "peer_review_first_year": 2020, "peer_review_latest_year": 2026,
            "peer_review_breakdown": [{"issn": "2071-1050", "name": "Sustainability", "reviews": 76}],
            "citation_profiles": {
                "scholar": {"as_of": "2026-09-07", "citations": 388, "h_index": 12, "i10_index": 12},
                "openalex": {"as_of": "2026-09-07", "citations": 288, "h_index": 10, "i10_index": 10},
            },
        }
        self.library = {key: self.previous[key] for key in
                        ("library_records", "library_peer_reviewed", "library_preprints",
                         "library_corrections", "year_span")}

    def refresh(self, **responses):
        with tempfile.TemporaryDirectory() as folder, contextlib.ExitStack() as stack:
            out = Path(folder) / "stats.json"
            out.write_text(json.dumps(self.previous))
            stack.enter_context(patch.object(metrics, "OUT_PATH", str(out)))
            stack.enter_context(patch.object(metrics, "log"))
            for name in ("from_library", "from_orcid", "from_orcid_peer_reviews",
                         "from_openalex", "from_scholar"):
                value = responses.get(name, RuntimeError("source unavailable"))
                args = {"side_effect": value} if isinstance(value, Exception) else {"return_value": value}
                stack.enter_context(patch.object(metrics, name, **args))
            self.assertEqual(metrics.main(), 0)
            return json.loads(out.read_text())

    def test_orcid_failure_preserves_counts_breakdown_and_verified_dates(self):
        result = self.refresh(from_library=self.library)
        for key in ("peer_reviewed_works", "orcid_peer_reviewed", "peer_reviews",
                    "peer_review_journals", "peer_review_breakdown", "orcid_as_of", "peer_review_as_of"):
            self.assertEqual(result[key], self.previous[key], key)
        self.assertEqual(result["sources"]["orcid"], "unavailable")
        self.assertEqual(result["sources"]["scholar"], "unavailable")
        self.assertEqual(result["citation_profiles"], self.previous["citation_profiles"])

    def test_failed_library_keeps_pending_papers_after_orcid_refresh(self):
        result = self.refresh(from_orcid={"peer_reviewed_works": 36, "preprints": 2, "works_total": 42})
        self.assertEqual(result["peer_reviewed_works"], 38)
        self.assertEqual(result["orcid_peer_reviewed"], 36)
        self.assertEqual(result["works_pending_in_orcid"], 2)

    def test_rejected_review_drop_keeps_complete_previous_snapshot(self):
        result = self.refresh(from_library=self.library,
                              from_orcid_peer_reviews={"peer_reviews": 1, "peer_review_journals": 1,
                                                       "peer_review_breakdown": []})
        self.assertEqual(result["sources"]["orcid_peer_reviews"], "rejected")
        self.assertEqual(result["peer_reviews"], self.previous["peer_reviews"])
        self.assertEqual(result["peer_review_breakdown"], self.previous["peer_review_breakdown"])
        self.assertEqual(result["peer_review_as_of"], "2026-09-07")

    def test_orcid_guard_compares_its_own_count_when_library_is_ahead(self):
        self.previous["peer_reviewed_works"] = 50
        self.library["library_peer_reviewed"] = 50
        result = self.refresh(from_library=self.library,
                              from_orcid={"peer_reviewed_works": 36, "preprints": 2, "works_total": 42})
        self.assertEqual(result["sources"]["orcid"], "ok")
        self.assertEqual(result["peer_reviewed_works"], 50)
        self.assertEqual(result["orcid_peer_reviewed"], 36)
        self.assertEqual(result["works_pending_in_orcid"], 14)

    def test_rejected_citation_drop_does_not_advance_snapshot_date(self):
        result = self.refresh(from_library=self.library,
                              from_scholar={"citations": 1, "h_index": 1, "i10_index": 1})
        self.assertEqual(result["sources"]["scholar"], "rejected")
        self.assertEqual(result["citation_profiles"]["scholar"], self.previous["citation_profiles"]["scholar"])

    def test_successful_reviews_update_counts_and_their_own_date(self):
        reviews = {key: copy.deepcopy(self.previous[key]) for key in
                   ("peer_reviews", "peer_review_journals", "peer_review_breakdown",
                    "peer_review_first_year", "peer_review_latest_year")}
        reviews["peer_reviews"] += 1
        reviews["peer_review_breakdown"][0]["reviews"] += 1
        result = self.refresh(from_library=self.library, from_orcid_peer_reviews=reviews)
        self.assertEqual(result["peer_reviews"], reviews["peer_reviews"])
        self.assertEqual(result["peer_review_as_of"], result["last_checked"])
        self.assertEqual(result["orcid_as_of"], "2026-09-07")

    def test_all_sources_fail_leaves_previous_file_untouched(self):
        self.assertEqual(self.refresh(), self.previous)

    def test_old_scholar_falls_back_to_whole_openalex_snapshot(self):
        profiles = copy.deepcopy(self.previous["citation_profiles"])
        profiles["scholar"]["as_of"] = "2000-01-01"
        name, profile = metrics.choose_profile(profiles)
        self.assertEqual(name, "openalex")
        self.assertEqual(profile, profiles["openalex"])


if __name__ == "__main__":
    unittest.main()
