import unittest

from legalir_portfolio.core import constrained_top5, reciprocal_rank_fusion
from legalir_portfolio.metrics import evaluate_ranking, membership_is_preserved


class CoreTests(unittest.TestCase):
    def test_rrf_prefers_cross_signal_consensus(self):
        result = reciprocal_rank_fusion(
            [["a", "b", "c"], ["b", "d", "a"]], k=3, weights=[1, 1]
        )
        self.assertEqual(result[0], "b")
        self.assertEqual(set(result), {"a", "b", "c", "d"})

    def test_constrained_top5_preserves_top20(self):
        hard = {"q": [str(i) for i in range(1, 31)]}
        guide = {"q": ["8", "7", "6", "5", "4", "99"]}
        result = constrained_top5(hard, guide)
        self.assertEqual(result["q"][:5], ["8", "7", "6", "5", "4"])
        self.assertTrue(membership_is_preserved(hard, result, 20))

    def test_metrics(self):
        ranking = {"q1": ["a", "x"], "q2": ["y", "z"]}
        gold = {"q1": {"a", "b"}, "q2": {"c"}}
        metric = evaluate_ranking(ranking, gold, cutoff=1)
        self.assertEqual(metric["hits"], 1)
        self.assertEqual(metric["gold"], 3)
        self.assertEqual(metric["zero_hit_queries"], 1)


if __name__ == "__main__":
    unittest.main()
