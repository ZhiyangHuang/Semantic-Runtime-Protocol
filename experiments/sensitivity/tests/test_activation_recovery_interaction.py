from __future__ import annotations

import unittest

from experiments.sensitivity.interaction.activation_recovery_interaction import run_activation_recovery_interaction_experiment
from experiments.sensitivity.interaction.runner import run_activation_recovery_cell


class ActivationRecoveryInteractionAnalysisTests(unittest.TestCase):
    def test_matrix_has_four_cells(self) -> None:
        result = run_activation_recovery_interaction_experiment([0.1, 0.9], [1, 3])
        self.assertEqual(result["experiment"]["parameter_a"], "activation_threshold")
        self.assertEqual(result["experiment"]["parameter_b"], "recovery_min_evidence")
        self.assertEqual(len(result["matrix"]), 4)

    def test_boundary_consistency_is_preserved(self) -> None:
        cell_low = run_activation_recovery_cell(0.1, 1)
        cell_high = run_activation_recovery_cell(0.9, 3)

        self.assertTrue(cell_low["metrics"]["replay_equivalent"])
        self.assertTrue(cell_high["metrics"]["replay_equivalent"])
        self.assertTrue(cell_low["metrics"]["state_transition_equivalence"])
        self.assertTrue(cell_high["metrics"]["state_transition_equivalence"])
        self.assertGreaterEqual(cell_low["metrics"]["boundary_consistency_score"], 0.66)
        self.assertGreaterEqual(cell_high["metrics"]["boundary_consistency_score"], 0.66)

    def test_pairwise_observation_varies_by_condition(self) -> None:
        low_low = run_activation_recovery_cell(0.1, 1)
        low_high = run_activation_recovery_cell(0.1, 3)
        high_low = run_activation_recovery_cell(0.9, 1)
        high_high = run_activation_recovery_cell(0.9, 3)

        self.assertNotEqual(low_low["metrics"]["final_activation"], high_low["metrics"]["final_activation"])
        self.assertNotEqual(low_low["metrics"]["recovery_success"], low_high["metrics"]["recovery_success"])
        self.assertNotEqual(high_low["metrics"]["recovery_success"], high_high["metrics"]["recovery_success"])


if __name__ == "__main__":
    unittest.main()
