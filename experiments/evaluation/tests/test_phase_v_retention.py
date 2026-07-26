from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from experiments.config import PhaseVRetentionConfig
from experiments.evaluation.phase_v_retention.metrics import evaluate_retention_case, summarize_retention_results
from experiments.evaluation.phase_v_retention.runner import build_retention_cases, run_phase_v_retention, write_phase_v_retention_outputs


class PhaseVRetentionTests(unittest.TestCase):
    def test_retention_metrics_schema(self) -> None:
        config = PhaseVRetentionConfig(
            baseline_activation_threshold=0.5,
            baseline_recovery_min_evidence=1,
            baseline_preserve_evidence=False,
            baseline_archive_relations=False,
        )
        cases = build_retention_cases(config)
        self.assertEqual(len(cases), 4)

        result = evaluate_retention_case(cases[0], weights=config.semantic_drift_weights)
        self.assertAlmostEqual(result.metrics.semantic_coverage, 1.0)
        self.assertAlmostEqual(result.metrics.semantic_drift, 0.0)
        self.assertAlmostEqual(result.metrics.recovery_accuracy, 1.0)
        self.assertIn("evidence_cost", result.metrics.as_dict())

    def test_retention_summary(self) -> None:
        config = PhaseVRetentionConfig()
        cases = build_retention_cases(config)
        records = [evaluate_retention_case(case, weights=config.semantic_drift_weights) for case in cases]
        summary = summarize_retention_results(records)
        self.assertEqual(summary["case_count"], 4)
        self.assertIn("mean_semantic_coverage", summary)
        self.assertIn("mean_semantic_drift", summary)
        self.assertIn("mean_recovery_accuracy", summary)
        self.assertGreaterEqual(summary["coverage_max"], summary["coverage_min"])

    def test_write_outputs(self) -> None:
        config = PhaseVRetentionConfig()
        with TemporaryDirectory() as tmpdir:
            outputs = write_phase_v_retention_outputs(Path(tmpdir) / "phase_v_retention", config=config)
            self.assertTrue(Path(outputs["records_csv"]).exists())
            self.assertTrue(Path(outputs["records_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())

    def test_runner_returns_report(self) -> None:
        output = run_phase_v_retention(PhaseVRetentionConfig())
        self.assertEqual(output["report"]["summary"]["case_count"], 4)
        self.assertIn("Phase V Retention and Drift Evaluation", output["markdown"])


if __name__ == "__main__":
    unittest.main()
