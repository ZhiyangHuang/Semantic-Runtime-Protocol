from __future__ import annotations

import unittest

from experiments.optimization.phase_iii_a_round1.candidate import build_round1_candidate_space
from experiments.optimization.phase_iii_a_round1.objective import ObjectiveWeights
from experiments.optimization.phase_iii_a_round1.runner import run_phase_iii_a_round1_optimization


class PhaseIIIARound1OptimizationTests(unittest.TestCase):
    def test_candidate_space_has_eighteen_points(self) -> None:
        candidates = build_round1_candidate_space()

        self.assertEqual(len(candidates), 18)
        self.assertEqual(candidates[0].activation_threshold, 0.3)
        self.assertEqual(candidates[-1].recovery_min_evidence, 3)

    def test_round1_produces_ranked_recommendation(self) -> None:
        output = run_phase_iii_a_round1_optimization()
        report = output["report"]

        self.assertEqual(report["summary"]["candidate_count"], 18)
        self.assertEqual(len(report["evaluations"]), 18)
        self.assertIsNotNone(report["recommended_configuration"])
        self.assertEqual(report["evaluations"][0]["rank"], 1)
        self.assertGreaterEqual(report["evaluations"][0]["objective_value"], report["evaluations"][-1]["objective_value"])

    def test_recommendation_is_deterministic(self) -> None:
        first = run_phase_iii_a_round1_optimization()
        second = run_phase_iii_a_round1_optimization(weights=ObjectiveWeights())

        self.assertEqual(first["report"]["recommended_configuration"], second["report"]["recommended_configuration"])
        self.assertEqual(first["report"]["summary"], second["report"]["summary"])

    def test_constraint_status_is_retained(self) -> None:
        output = run_phase_iii_a_round1_optimization()
        evaluations = output["report"]["evaluations"]

        self.assertTrue(all(item["constraint_status"] == "passed" for item in evaluations))
        self.assertTrue(all(item["metric_breakdown"]["instability_penalty"] == 0.0 for item in evaluations))


if __name__ == "__main__":
    unittest.main()
