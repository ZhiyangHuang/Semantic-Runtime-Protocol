from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.validation.phase_ii_boundary_generalization import write_phase_ii_boundary_generalization_outputs


class PhaseIIBoundaryGeneralizationTests(unittest.TestCase):
    def test_boundary_generalization_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_phase_ii_boundary_generalization_outputs(Path(tmpdir))
            self.assertTrue(Path(outputs["csv"]).exists())
            self.assertTrue(Path(outputs["jsonl"]).exists())
            self.assertTrue(Path(outputs["summary"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())
            self.assertTrue(Path(outputs["report"]).exists())
            self.assertTrue(Path(outputs["figures"]["iou_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["iou_pdf"]).exists())
            self.assertEqual(outputs["summary_data"]["reference_scenario"], "standard_5x5")
            self.assertIn("pairwise_overlap", outputs["summary_data"])
            self.assertGreaterEqual(outputs["summary_data"]["pairwise_overlap"]["standard_5x5"]["dense_9x9"]["iou"], 0.0)


if __name__ == "__main__":
    unittest.main()
