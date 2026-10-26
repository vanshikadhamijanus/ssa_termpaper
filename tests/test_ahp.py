"""AHP mathematical properties and declared preference sampling policy."""
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import ahp as H
import model as M


class AHPProperties(unittest.TestCase):
    def test_consistent_ratios_recover_known_priorities(self):
        expected = np.array([.1, .2, .3, .4])
        matrix = expected[:, None] / expected[None, :]
        weights, eigenvalue, ci, cr = H.AHPmat(matrix)
        np.testing.assert_allclose(weights, expected, atol=1e-12)
        self.assertAlmostEqual(eigenvalue, len(expected))
        self.assertLess(ci, 1e-12)
        self.assertLess(cr, 1e-12)

    def test_option_relabelling_preserves_priorities(self):
        matrix = H.pairwise([2, 3, 4, 2, 3, 2])
        permutation = [2, 0, 3, 1]
        weights, eigenvalue, _, cr = H.AHPmat(matrix)
        new_weights, new_eigenvalue, _, new_cr = H.AHPmat(matrix[np.ix_(permutation, permutation)])
        np.testing.assert_allclose(new_weights, weights[permutation], atol=1e-12)
        self.assertAlmostEqual(new_eigenvalue, eigenvalue)
        self.assertAlmostEqual(new_cr, cr)

    def test_nonreciprocal_or_nonpositive_comparisons_fail(self):
        for matrix in ([[1, 2], [2, 1]], [[1, 0], [0, 1]], [[1, np.nan], [1, 1]]):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                H.AHPmat(matrix)

    def test_scores_preserve_order_under_offset_and_units(self):
        values = np.array([-3., 0., 5., 8.])
        for floor in (.01, .10, .30):
            priorities = H.less_is_better(values, floor)
            np.testing.assert_allclose(priorities, H.less_is_better(20 + 1000 * values, floor))
            self.assertTrue((np.diff(priorities) < 0).all())
            self.assertAlmostEqual(priorities.sum(), 1.)
        np.testing.assert_allclose(H.less_is_better([2, 2, 2, 2]), .25)

    def test_proxy_removal_and_extreme_weights_stay_normalized(self):
        p = M.load_params()
        L = M.lca(p)
        C = M.lcc(p, L)
        v, _ = H.sub_weights()
        for floor in (.01, .10, .30):
            local, _, _ = H.local_priorities(L, C, floor)
            for omitted in H.PROXY_CASES.values():
                subweights = H.omit_leaves(v, omitted)
                for main_weights in np.eye(4):
                    scores = H.global_scores(local, subweights, main_weights)
                    self.assertAlmostEqual(scores.sum(), 1.)
                    self.assertTrue((scores >= 0).all())

    def test_seeded_preferences_are_reciprocal_and_pass_cr_rule(self):
        rng = np.random.default_rng(2901)
        for _ in range(100):
            main, sub, qualitative, diagnostics = H.sample_preferences(rng)
            self.assertAlmostEqual(main.sum(), 1.)
            self.assertTrue((main > 0).all())
            self.assertLessEqual(diagnostics["maximum_accepted_cr"], .10)
            self.assertEqual(diagnostics["matrix_attempts"] - diagnostics["matrices_rejected"],
                             len(H.SUB_PAIRWISE) + len(H.QUAL_PAIRWISE))
            for weights in sub.values():
                self.assertAlmostEqual(weights.sum(), 1.)
                self.assertTrue((weights > 0).all())
            for matrix in qualitative.values():
                np.testing.assert_allclose(matrix * matrix.T, 1.)
                self.assertLessEqual(H.AHPmat(matrix)[3], .10)
        first = H.sample_preferences(np.random.default_rng(2901))
        repeat = H.sample_preferences(np.random.default_rng(2901))
        np.testing.assert_allclose(first[0], repeat[0])
        for name in first[2]:
            np.testing.assert_allclose(first[2][name], repeat[2][name])


if __name__ == "__main__":
    unittest.main()
