from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.optimization.phase_iii_a_round1.baseline import write_phase_iii_a_baseline_comparison_report
from experiments.validation.phase_ii_boundary import load_feasible_region, write_phase_ii_boundary_outputs


class PhaseIIIBaselineComparisonTests(unittest.TestCase):
    def test_baseline_comparison_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            boundary_outputs = write_phase_ii_boundary_outputs(Path(tmpdir) / "phase_ii_boundary")
            region = load_feasible_region(boundary_outputs["feasible_region"])
            outputs = write_phase_iii_a_baseline_comparison_report(feasible_region=region, output_dir=Path(tmpdir) / "phase_iii_a_baseline")

            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertEqual(outputs["summary"]["baseline_candidate_count"], 25)
            self.assertEqual(outputs["summary"]["srp_candidate_count"], 10)
            self.assertTrue(outputs["summary"]["top_match"])
            self.assertAlmostEqual(outputs["summary"]["search_reduction"], 0.6)


if __name__ == "__main__":
    unittest.main()
