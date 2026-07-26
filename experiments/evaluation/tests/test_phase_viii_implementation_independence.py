from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.config import load_phase_viii_implementation_independence_config
from experiments.evaluation.phase_viii_implementation_independence.runner import write_phase_viii_implementation_independence_outputs


class PhaseVIIIImplementationIndependenceTests(unittest.TestCase):
    def test_config_loader(self) -> None:
        config = load_phase_viii_implementation_independence_config()
        self.assertEqual(config.phase, "phase_viii_implementation_independence")
        self.assertIn("flat_semantic_store", config.backend_names)
        self.assertIn("graph_semantic_store", config.backend_names)
        self.assertIn("vector_overlay_store", config.backend_names)

    def test_run_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = write_phase_viii_implementation_independence_outputs(Path(temp_dir))
        report = outputs["report"]
        summary = report["summary"]
        self.assertEqual(summary["case_count"], 36)
        self.assertEqual(summary["hierarchy_consistency_rate"], 1.0)
        self.assertEqual(summary["governance_consistency_rate"], 1.0)
        self.assertIn("backend_summary", report)
        self.assertIn("implementation_summary", report)


if __name__ == "__main__":
    unittest.main()
