from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.config import PhaseVIIIRepresentationInvarianceConfig
from experiments.evaluation.phase_viii_representation_invariance.runner import (
    build_representation_invariance_runs,
    run_phase_viii_representation_invariance,
    write_phase_viii_representation_invariance_outputs,
)


class PhaseVIIIRepresentationInvarianceTests(unittest.TestCase):
    def test_build_runs(self) -> None:
        config = PhaseVIIIRepresentationInvarianceConfig(
            encoder_names=("toy-e5", "toy-bge"),
            parser_names=("rule_parser", "llm_parser"),
            recovery_modes=("vector_only", "relation_expansion", "relation_closure"),
        )
        runs = build_representation_invariance_runs(config)
        self.assertEqual(len(runs), 4 * 2 * 2 * 3)
        self.assertEqual(runs[0].config.mode, "vector_only")

    def test_run_roundtrip(self) -> None:
        config = PhaseVIIIRepresentationInvarianceConfig(
            encoder_names=("toy-e5",),
            parser_names=("rule_parser",),
            recovery_modes=("vector_only", "relation_expansion", "relation_closure"),
        )
        outputs = run_phase_viii_representation_invariance(config)
        self.assertEqual(outputs["report"]["summary"]["case_count"], 4 * 1 * 1 * 3)
        self.assertIn("hierarchy_consistency_rate", outputs["report"]["summary"])

    def test_summary(self) -> None:
        config = PhaseVIIIRepresentationInvarianceConfig(
            encoder_names=("toy-e5", "toy-bge"),
            parser_names=("rule_parser",),
            recovery_modes=("vector_only", "relation_expansion", "relation_closure"),
        )
        outputs = run_phase_viii_representation_invariance(config)
        summary = outputs["report"]["summary"]
        self.assertGreaterEqual(summary["mean_semantic_coverage"], 0.0)
        self.assertGreaterEqual(summary["hierarchy_consistency_rate"], 0.0)
        self.assertLessEqual(summary["governance_consistency_rate"], 1.0)

    def test_write_outputs(self) -> None:
        config = PhaseVIIIRepresentationInvarianceConfig(
            encoder_names=("toy-e5",),
            parser_names=("rule_parser",),
            recovery_modes=("vector_only", "relation_expansion", "relation_closure"),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_phase_viii_representation_invariance_outputs(Path(tmpdir), config=config)
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())


if __name__ == "__main__":
    unittest.main()
