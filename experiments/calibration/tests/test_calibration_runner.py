from __future__ import annotations

import unittest

from experiments.calibration.candidate import CalibrationCandidate
from experiments.calibration.runner import run_calibration_candidate


class CalibrationRunnerTests(unittest.TestCase):
    def test_activation_threshold_candidate_is_accepted_under_round1(self) -> None:
        result = run_calibration_candidate(CalibrationCandidate(parameter="activation_threshold", value=0.6))

        self.assertEqual(result.parameter, "activation_threshold")
        self.assertEqual(result.candidate_value, 0.6)
        self.assertTrue(result.accepted)
        self.assertTrue(result.constraints_passed)
        self.assertTrue(result.metrics["replay_equivalent"])
        self.assertTrue(result.metrics["state_transition_equivalent"])
        self.assertIn("accepted=True", result.notes)


if __name__ == "__main__":
    unittest.main()

