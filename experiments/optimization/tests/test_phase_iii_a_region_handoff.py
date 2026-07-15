from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.optimization.phase_iii_a_round1.runner import run_phase_iii_a_round1_optimization
from experiments.validation.phase_ii_boundary import load_feasible_region, write_phase_ii_boundary_outputs


class PhaseIIIARegionHandoffTests(unittest.TestCase):
    def test_round1_optimizer_consumes_phase_ii_region(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            boundary_outputs = write_phase_ii_boundary_outputs(Path(tmpdir) / "phase_ii_boundary")
            region = load_feasible_region(boundary_outputs["feasible_region"])
            result = run_phase_iii_a_round1_optimization(feasible_region=region)

            self.assertEqual(result["report"]["summary"]["candidate_count"], 10)
            self.assertEqual(len(result["candidates"]), 10)
            self.assertEqual(result["report"]["summary"]["passed_constraint_count"], 10)
            self.assertEqual(result["feasible_region"]["coverage"], 0.4)
            recommended = result["report"]["recommended_configuration"]
            self.assertIn(recommended["activation_threshold"], region.activation_threshold_values())
            self.assertIn(recommended["recovery_min_evidence"], region.recovery_min_evidence_values())


if __name__ == "__main__":
    unittest.main()
