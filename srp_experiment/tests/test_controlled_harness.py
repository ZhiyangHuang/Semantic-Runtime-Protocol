import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.controlled_harness import (
    build_controlled_suites,
    render_controlled_summary_markdown,
    run_controlled_harness,
    summarize_controlled_records,
    write_controlled_outputs,
)


class TestControlledHarness(unittest.TestCase):
    def test_controlled_harness_exposes_fixed_suite_names(self):
        suites = build_controlled_suites()
        self.assertEqual([suite.name for suite in suites], ["structured_recovery", "object_retention", "repair_loop"])
        self.assertEqual(suites[0].task["task_type"], "structured_recovery")
        self.assertEqual(suites[1].task["task_type"], "object_retention")
        self.assertEqual(suites[2].task["task_type"], "repair_loop")

    def test_controlled_harness_runs_repair_loop_with_repair_attempted(self):
        records = run_controlled_harness(["repair_loop"], cycles=1)
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["harness_suite"], "repair_loop")
        self.assertTrue(record["repair_attempted"])
        self.assertIsNotNone(record["token_overhead"])
        self.assertIn("repair", record["experiment_result"])
        self.assertIn("diagnostics", record["experiment_result"]["repair"])
        self.assertIn("token_overhead", record["experiment_result"]["repair"])
        self.assertEqual(record["experiment_result"]["repair"]["token_overhead"], record["token_overhead"])
        self.assertEqual(record["experiment_result"]["repair"]["diagnostics"]["schema_version"], "repair_diagnostics.v1")

    def test_controlled_harness_writes_all_outputs(self):
        records = run_controlled_harness(["structured_recovery", "object_retention"], cycles=1)
        summary = summarize_controlled_records(records)
        self.assertEqual(summary["records"], 2)
        self.assertIn("structured_recovery", summary["suites"])
        self.assertIn("important_recall", summary["suites"]["structured_recovery"])
        self.assertIn("token_overhead", summary["suites"]["structured_recovery"])
        markdown = render_controlled_summary_markdown(summary)
        self.assertIn("# Controlled SRP Harness Summary", markdown)
        self.assertIn("Important Recall", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_controlled_outputs(records, Path(tmpdir))
            self.assertTrue(output_paths["jsonl"].exists())
            self.assertTrue(output_paths["csv"].exists())
            self.assertTrue(output_paths["markdown"].exists())
            self.assertTrue(output_paths["summary"].exists())


if __name__ == "__main__":
    unittest.main()
