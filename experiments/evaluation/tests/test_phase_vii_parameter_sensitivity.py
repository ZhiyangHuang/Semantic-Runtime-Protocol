from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.config import PhaseVIIBParameterSensitivityConfig
from experiments.evaluation.phase_vii_parameter_sensitivity.metrics import evaluate_parameter_sensitivity_runs, summarize_parameter_sensitivity_results
from experiments.evaluation.phase_vii_parameter_sensitivity.runner import build_parameter_sensitivity_runs, run_phase_vii_parameter_sensitivity, write_phase_vii_parameter_sensitivity_outputs


class PhaseVIIBParameterSensitivityTests(unittest.TestCase):
    def test_build_parameter_sensitivity_runs(self) -> None:
        runs = build_parameter_sensitivity_runs(PhaseVIIBParameterSensitivityConfig())
        self.assertGreaterEqual(len(runs), 5)
        self.assertEqual(runs[0].axis_name, "baseline")

    def test_sensitivity_summary(self) -> None:
        config = PhaseVIIBParameterSensitivityConfig()
        runs = build_parameter_sensitivity_runs(config)
        records = evaluate_parameter_sensitivity_runs(runs)
        summary = summarize_parameter_sensitivity_results(records)
        self.assertEqual(summary["run_count"], len(runs))
        self.assertIn("pareto_frontier", summary)
        self.assertGreaterEqual(summary["mean_semantic_coverage"], 0.0)

    def test_write_outputs(self) -> None:
        config = PhaseVIIBParameterSensitivityConfig()
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_phase_vii_parameter_sensitivity_outputs(Path(tmpdir) / "phase_vii_parameter_sensitivity", config=config)
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["records_csv"]).exists())

    def test_run_roundtrip(self) -> None:
        output = run_phase_vii_parameter_sensitivity(PhaseVIIBParameterSensitivityConfig())
        self.assertIn("report", output)
        self.assertEqual(output["report"]["status"], "evaluated")


if __name__ == "__main__":
    unittest.main()
