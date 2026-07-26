from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from experiments.config import PhaseVIRelationRecoveryConfig
from experiments.evaluation.phase_vi_relation_recovery.cases import build_relation_recovery_cases
from experiments.evaluation.phase_vi_relation_recovery.metrics import evaluate_relation_recovery_case, summarize_relation_recovery_results
from experiments.evaluation.phase_vi_relation_recovery.schema import RecoveryConfig
from experiments.evaluation.phase_vi_relation_recovery.runner import run_phase_vi_relation_recovery, write_phase_vi_relation_recovery_outputs


class PhaseVIRelationRecoveryTests(unittest.TestCase):
    def test_relation_recovery_schema(self) -> None:
        config = PhaseVIRelationRecoveryConfig()
        cases = build_relation_recovery_cases()
        self.assertEqual(len(cases), 4)
        self.assertEqual(config.recovery_modes, ("vector_only", "relation_expansion", "relation_closure"))

        result = evaluate_relation_recovery_case(
            cases[0],
            config=RecoveryConfig(
                mode="vector_only",
                top_k=2,
                relation_depth=1,
                closure_validation=False,
            ),
        )
        self.assertIn("semantic_coverage", result.metrics.as_dict())
        self.assertIn("closure_accuracy", result.metrics.as_dict())

    def test_relation_recovery_summary(self) -> None:
        config = PhaseVIRelationRecoveryConfig()
        cases = build_relation_recovery_cases()
        records = []
        for case in cases:
            for mode in config.recovery_modes:
                records.append(
                    evaluate_relation_recovery_case(
                        case,
                        RecoveryConfig(
                            mode=mode,
                            top_k=config.top_k,
                            relation_depth=config.relation_depth,
                            closure_validation=config.closure_validation,
                        ),
                    )
                )
        summary = summarize_relation_recovery_results(records)
        self.assertEqual(summary["case_count"], 12)
        self.assertIn("mean_semantic_coverage", summary)
        self.assertIn("mean_closure_accuracy", summary)
        self.assertIn("mode_summary", summary)

    def test_write_outputs(self) -> None:
        config = PhaseVIRelationRecoveryConfig()
        with TemporaryDirectory() as tmpdir:
            outputs = write_phase_vi_relation_recovery_outputs(Path(tmpdir) / "phase_vi_relation_recovery", config=config)
            self.assertTrue(Path(outputs["records_csv"]).exists())
            self.assertTrue(Path(outputs["records_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())

    def test_runner_returns_report(self) -> None:
        output = run_phase_vi_relation_recovery(PhaseVIRelationRecoveryConfig())
        self.assertEqual(output["report"]["summary"]["case_count"], 12)
        self.assertIn("Phase VI Relation-Aware Recovery Report", output["markdown"])


if __name__ == "__main__":
    unittest.main()
