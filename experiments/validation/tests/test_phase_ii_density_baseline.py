from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.validation.phase_ii_density_baseline import write_phase_ii_density_baseline_outputs


class PhaseIIDensityBaselineTests(unittest.TestCase):
    def test_density_baseline_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_phase_ii_density_baseline_outputs(Path(tmpdir))
            self.assertTrue(Path(outputs["csv"]).exists())
            self.assertTrue(Path(outputs["jsonl"]).exists())
            self.assertTrue(Path(outputs["summary"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())
            self.assertTrue(Path(outputs["report"]).exists())
            self.assertTrue(Path(outputs["figures"]["coverage_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["coverage_pdf"]).exists())
            self.assertEqual(outputs["summary_data"]["scenario_count"], 3)
            self.assertGreater(outputs["summary_data"]["total_candidate_count"], 0)
            self.assertIn("dense_9x9", outputs["summary_data"]["scenarios"])


if __name__ == "__main__":
    unittest.main()
