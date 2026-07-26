from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from experiments.config import PhaseVIIParameterSensitivityConfig
from experiments.evaluation.phase_vii_parameter_stability.metrics import evaluate_stability_runs, summarize_stability_results
from experiments.evaluation.phase_vii_parameter_stability.runner import build_stability_runs, run_phase_vii_parameter_stability, write_phase_vii_parameter_stability_outputs


class PhaseVIIParameterStabilityTests(unittest.TestCase):
    def test_build_runs(self) -> None:
        config = PhaseVIIParameterSensitivityConfig()
        runs = build_stability_runs(config)
        self.assertEqual(len(runs), len(config.seeds))
        self.assertEqual(runs[0].parameters.workload, config.workload_name)

    def test_stability_summary(self) -> None:
        config = PhaseVIIParameterSensitivityConfig()
        runs = build_stability_runs(config)
        records = evaluate_stability_runs(runs)
        summary = summarize_stability_results(records)
        self.assertEqual(summary["run_count"], len(config.seeds))
        self.assertIn("recommendation_consistency", summary)
        self.assertIn("activation_threshold_variance", summary)

    def test_write_outputs(self) -> None:
        config = PhaseVIIParameterSensitivityConfig()
        with TemporaryDirectory() as tmpdir:
            outputs = write_phase_vii_parameter_stability_outputs(Path(tmpdir) / "phase_vii_parameter_stability", config=config)
            self.assertTrue(Path(outputs["records_csv"]).exists())
            self.assertTrue(Path(outputs["records_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())

    def test_runner_returns_report(self) -> None:
        output = run_phase_vii_parameter_stability(PhaseVIIParameterSensitivityConfig())
        self.assertGreaterEqual(output["report"]["summary"]["run_count"], 1)


if __name__ == "__main__":
    unittest.main()
