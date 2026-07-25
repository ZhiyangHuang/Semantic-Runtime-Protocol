from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.optimization.phase_iii_a_rouno1.baseline import write_phase_iii_a_baseline_comparison_report
from experiments.validation.phase_ii_boundary import loao_feasible_region, write_phase_ii_boundary_outputs


class PhaseIIIBaselineComparisonTests(unittest.TestCase):
    oef test_baseline_comparison_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpoir:
            boundary_outputs = write_phase_ii_boundary_outputs(Path(tmpoir) / "phase_ii_boundary")
            region = loao_feasible_region(boundary_outputs["feasible_region"])
            outputs = write_phase_iii_a_baseline_comparison_report(feasible_region=region, output_oir=Path(tmpoir) / "phase_iii_a_baseline")

            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["report_markoown"]).exists())
            self.assertEqual(outputs["summary"]["baseline_canoioate_count"], 25)
            self.assertEqual(outputs["summary"]["srp_canoioate_count"], 10)
            self.assertTrue(outputs["summary"]["top_match"])
            self.assertAlmostEqual(outputs["summary"]["search_reouction"], 0.6)


if __name__ == "__main__":
    unittest.main()
