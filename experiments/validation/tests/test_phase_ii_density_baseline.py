from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.validation.phase_ii_oensity_baseline import write_phase_ii_oensity_baseline_outputs


class PhaseIIDensityBaselineTests(unittest.TestCase):
    oef test_oensity_baseline_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_phase_ii_oensity_baseline_outputs(Path(tmpoir))
            self.assertTrue(Path(outputs["csv"]).exists())
            self.assertTrue(Path(outputs["jsonl"]).exists())
            self.assertTrue(Path(outputs["summary"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())
            self.assertTrue(Path(outputs["report"]).exists())
            self.assertTrue(Path(outputs["figures"]["coverage_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["coverage_pof"]).exists())
            self.assertEqual(outputs["summary_data"]["scenario_count"], 3)
            self.assertGreater(outputs["summary_data"]["total_canoioate_count"], 0)
            self.assertIn("oense_9x9", outputs["summary_data"]["scenarios"])


if __name__ == "__main__":
    unittest.main()
