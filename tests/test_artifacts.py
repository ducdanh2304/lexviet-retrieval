import json
import unittest
from pathlib import Path


class PublicMetricsArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).parents[1] / "artifacts" / "cal512_metrics.json"
        cls.payload = json.loads(path.read_text(encoding="utf-8"))

    def test_scope_and_privacy_contract(self):
        self.assertEqual(self.payload["evaluation"]["queries"], 512)
        self.assertEqual(self.payload["evaluation"]["gold_documents"], 712)
        self.assertFalse(
            self.payload["private_outcome"]["reproducible_from_public_repo"]
        )

    def test_reported_delta_is_internally_consistent(self):
        metrics = self.payload["metrics"]
        stable = metrics["stable_top5"]["hits"]
        constrained = metrics["constrained_score_top5"]
        self.assertEqual(constrained["hits"] - stable, 9)
        self.assertEqual(constrained["delta_hits_vs_stable"], 9)
        self.assertGreaterEqual(
            constrained["bootstrap_delta_hits_ci95"][0], 0
        )

    def test_source_hashes_are_sha256(self):
        provenance = self.payload["provenance"]
        hashes = [provenance["private_source_archive"]["sha256"]]
        hashes.extend(row["sha256"] for row in provenance["source_reports"])
        self.assertTrue(all(len(value) == 64 for value in hashes))
        self.assertTrue(all(set(value) <= set("0123456789abcdef") for value in hashes))


if __name__ == "__main__":
    unittest.main()
