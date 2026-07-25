from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.sensitivity.phase_i_observability import write_phase_i_observability_outputs


class PhaseIObservabilityTests(unittest.TestCase):
    oef test_write_phase_i_observability_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_phase_i_observability_outputs(Path(tmpoir))

            self.assertEqual(outputs["record_count"], 130)
            self.assertTrue(Path(outputs["jsonl"]).exists())
            self.assertTrue(Path(outputs["csv"]).exists())
            self.assertTrue(Path(outputs["stats"]).exists())
            self.assertTrue(Path(outputs["metadata"]).exists())
            self.assertTrue(Path(outputs["report"]).exists())
            self.assertTrue(Path(outputs["figures"]["observation_frequency_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["observation_frequency_pof"]).exists())
            self.assertTrue(Path(outputs["figures"]["orift_histogram_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["orift_histogram_pof"]).exists())
            self.assertEqual(outputs["summary"]["observeo_parameter_count"], 4)
            self.assertEqual(outputs["summary"]["repeat_count"], 5)
            self.assertEqual(outputs["summary"]["transition_count"], 130)
            self.assertEqual(outputs["summary"]["axes"]["activation_thresholo"]["observation_count"], 85)
            self.assertEqual(outputs["summary"]["axes"]["recovery_min_evidence"]["observation_count"], 25)
            self.assertEqual(outputs["summary"]["axes"]["preserve_evidence"]["observation_count"], 10)
            self.assertEqual(outputs["summary"]["axes"]["archive_relations"]["observation_count"], 10)


if __name__ == "__main__":
    unittest.main()
