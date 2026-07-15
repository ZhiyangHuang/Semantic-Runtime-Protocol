from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.optimization.phase_iii_a_round1.objective_sensitivity import write_phase_iii_a_objective_sensitivity_outputs
from experiments.validation.phase_ii_boundary import load_feasible_region, write_phase_ii_boundary_outputs


class PhaseIIIAObjectiveSensitivityTests(unittest.TestCase):
    def test_objective_sensitivity_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            boundary_outputs = write_phase_ii_boundary_outputs(Path(tmpdir) / "phase_ii_boundary")
            region = load_feasible_region(boundary_outputs["feasible_region"])
            outputs = write_phase_iii_a_objective_sensitivity_outputs(
                feasible_region=region,
                output_dir=Path(tmpdir) / "phase_iii_a_objective_sensitivity",
            )

            self.assertTrue(Path(outputs["rankings_csv"]).exists())
            self.assertTrue(Path(outputs["rankings_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())
            self.assertTrue(Path(outputs["report"]).exists())
            self.assertTrue(Path(outputs["figures"]["rank_correlation_heatmap_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["top_objective_bar_png"]).exists())
            self.assertEqual(outputs["summary_data"]["scenario_count"], 4)
            self.assertEqual(outputs["summary_data"]["reference_scenario"], "O1_balanced")
            self.assertIn("O3_cost_priority", outputs["summary_data"]["scenario_names"])


if __name__ == "__main__":
    unittest.main()
