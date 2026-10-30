"""Regression coverage: a partial Crossref outage must not shrink the CV."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from io import BytesIO

spec = importlib.util.spec_from_file_location('cvdata', Path(__file__).parent.parent / 'cv/cvdata.py')
cvdata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cvdata)


class CacheRefreshTests(unittest.TestCase):
    def test_partial_outage_retains_old_record_and_adds_new_record(self):
        old = {'title': ['Previously verified paper'], 'type': 'journal-article'}
        new = {'title': ['New paper'], 'type': 'journal-article'}
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp) / 'cache.json'
            cache.write_text(json.dumps({'10.test/old': old}))

            def fetch(req, **kwargs):
                if req.full_url.endswith('10.test/new'):
                    return BytesIO(json.dumps({'message': new}).encode())
                raise OSError('Temporary service outage')

            with patch.object(cvdata, 'CACHE', str(cache)), \
                    patch.object(cvdata, '_library', return_value=[{'DOI': '10.test/old'}, {'DOI': '10.test/new'}]), \
                    patch.object(cvdata.urllib.request, 'urlopen', side_effect=fetch), \
                    patch.object(cvdata.time, 'sleep'):
                cvdata.refresh_cache()
            self.assertEqual(json.loads(cache.read_text()), {'10.test/old': old, '10.test/new': new})


    def test_manual_record_yields_to_registered_crossref_record(self):
        manual = next(r for r in cvdata.MANUAL if r['doi'] == '10.5252/zoosystema2026v48a25')
        registered = {'title': [manual['title']], 'type': 'journal-article', 'volume': '48',
                      'issue': '25', 'page': '741-789', 'issued': {'date-parts': [[2026, 10, 30]]},
                      'author': [{'family': 'Hounmavo', 'given': 'Amétépé'},
                                 {'family': 'Onditi', 'given': 'Kenneth Otieno'}]}
        for cached, expected in [({}, 1), ({manual['doi']: registered}, 1)]:
            with tempfile.TemporaryDirectory() as tmp:
                cache = Path(tmp) / 'cache.json'
                cache.write_text(json.dumps(cached))
                with patch.object(cvdata, 'CACHE', str(cache)), \
                        patch.object(cvdata, '_library', return_value=[]):
                    records = cvdata.publications()
            self.assertEqual(sum(r['doi'] == manual['doi'] for r in records), expected)
        self.assertNotIn(manual['doi'], cvdata.NOT_IN_CROSSREF)


if __name__ == '__main__':
    unittest.main()
