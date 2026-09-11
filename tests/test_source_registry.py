import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from forecast_input_archive import retain
from compare_input_bundles import retain_comparison
from build_source_registry import additional_pairs
from test_input_bundle_comparison import edition


class SourceRegistryTests(unittest.TestCase):
    def test_registry_binds_exact_pair_and_rejects_changed_comparison(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); archive = root / 'archive'
            edition(root, '2026-09-10T10:00:00Z', 7); before = retain(root, archive)['manifestSha256']
            edition(root, '2026-09-11T10:00:00Z', 10); after = retain(root, archive)['manifestSha256']
            receipt = retain_comparison(archive, before, after)
            pairs = additional_pairs(archive, ['g', 'unknown'])
            self.assertEqual(len(pairs), 1)
            self.assertEqual(pairs[0]['comparedSiteGames'], ['g'])
            self.assertEqual(pairs[0]['revisions'], [{'gameId': 'g', 'fields': ['score']}])
            self.assertEqual(pairs[0]['changedRecords'], 1)
            path = archive / 'comparisons' / (receipt['comparisonSha256'] + '.json')
            path.write_text('{}')
            with self.assertRaises(ValueError): additional_pairs(archive, ['g'])


if __name__ == '__main__': unittest.main()
