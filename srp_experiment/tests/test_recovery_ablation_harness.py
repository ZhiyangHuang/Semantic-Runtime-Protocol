import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.recovery_ablation_harness import (
    build_recovery_ablation_suites,
    render_recovery_ablation_summary_markdown,
    run_recovery_ablation,
    summarize_recovery_ablation,
    write_recovery_ablation_outputs,
)


class TestRecoveryAblationHarness(unittest.TestCase):
    def test_recovery_ablation_exposes_fixed_suite_names(self):
        suites = build_recovery_ablation_suites()
        self.assertEqual(
            [suite.name for suite in suites],
            ["text_only_recovery", "structured_only_recovery", "hybrid_recovery"],
        )
        self.assertEqual(suites[0].reconstruction_policy, "unrestricted")
        self.assertEqual(suites[1].reconstruction_policy, "minimal")
        self.assertEqual(suites[2].reconstruction_policy, "constrained")

    def test_recovery_ablation_runs_all_three_modes(self):
        records = run_recovery_ablation(["text_only_recovery", "structured_only_recovery", "hybrid_recovery"], cycles=1)
        self.assertEqual(len(records), 3)
        policies = {record["ablation_suite"]: record["reconstruction_policy"] for record in records}
        self.assertEqual(policies["text_only_recovery"], "unrestricted")
        self.assertEqual(policies["structured_only_recovery"], "minimal")
        self.assertEqual(policies["hybrid_recovery"], "constrained")
        self.assertTrue(all("experiment_result" in record for record in records))

    def test_recovery_ablation_summary_and_outputs(self):
        records = run_recovery_ablation(["text_only_recovery", "structured_only_recovery"], cycles=1)
        summary = summarize_recovery_ablation(records)
        self.assertEqual(summary["records"], 2)
        self.assertIn("text_only_recovery", summary["suites"])
        self.assertIn("validation_coverage", summary["suites"]["text_only_recovery"])
        markdown = render_recovery_ablation_summary_markdown(summary)
        self.assertIn("# Text vs Structured Recovery Ablation", markdown)
        self.assertIn("Validation Coverage", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_recovery_ablation_outputs(records, Path(tmpdir))
            self.assertTrue(output_paths["jsonl"].exists())
            self.assertTrue(output_paths["csv"].exists())
            self.assertTrue(output_paths["markdown"].exists())
            self.assertTrue(output_paths["summary"].exists())


if __name__ == "__main__":
    unittest.main()
