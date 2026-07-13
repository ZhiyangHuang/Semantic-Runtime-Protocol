import tempfile
import unittest
from pathlib import Path

from srp_experiment.graph_recovery_harness import (
    build_graph_recovery_suites,
    render_graph_recovery_summary_markdown,
    run_graph_recovery_evaluation,
    summarize_graph_recovery_evaluation,
    write_graph_recovery_outputs,
)


class TestGraphRecoveryHarness(unittest.TestCase):
    def test_graph_recovery_harness_exposes_fixed_suite_names(self):
        suites = build_graph_recovery_suites()
        self.assertEqual(
            [suite.name for suite in suites[:3]],
            [
                "dependency_chain_text",
                "dependency_chain_structured",
                "dependency_chain_graph",
            ],
        )
        self.assertEqual(suites[0].recovery_mode, "text")
        self.assertEqual(suites[1].recovery_mode, "structured")
        self.assertEqual(suites[2].recovery_mode, "graph")
        self.assertEqual(suites[0].task["task_type"], "graph_recovery_evaluation")

    def test_graph_recovery_harness_runs_all_modes_for_dependency_chain(self):
        records = run_graph_recovery_evaluation(
            [
                "dependency_chain_text",
                "dependency_chain_structured",
                "dependency_chain_graph",
            ],
            cycles=1,
        )
        self.assertEqual(len(records), 3)
        modes = {record["graph_recovery_mode"] for record in records}
        self.assertEqual(modes, {"text", "structured", "graph"})
        self.assertTrue(all("semantic_runtime_graph" in record for record in records))
        graph_record = next(record for record in records if record["graph_recovery_mode"] == "graph")
        self.assertIn("graph_recovery_result", graph_record)
        self.assertIn("graph_integrity_score", graph_record["semantic_graph_validation"])

    def test_graph_recovery_summary_and_outputs(self):
        records = run_graph_recovery_evaluation(
            [
                "dependency_chain_text",
                "dependency_chain_structured",
                "dependency_chain_graph",
            ],
            cycles=1,
        )
        summary = summarize_graph_recovery_evaluation(records)
        self.assertEqual(summary["records"], 3)
        self.assertIn("text", summary["modes"])
        self.assertIn("graph", summary["modes"])
        self.assertIn("graph_vs_text", summary["comparison"])
        markdown = render_graph_recovery_summary_markdown(summary)
        self.assertIn("# Graph Recovery Evaluation", markdown)
        self.assertIn("Graph Repair Cost", markdown)
        self.assertIn("Comparison Deltas", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_graph_recovery_outputs(records, Path(tmpdir))
            self.assertTrue(output_paths["jsonl"].exists())
            self.assertTrue(output_paths["csv"].exists())
            self.assertTrue(output_paths["markdown"].exists())
            self.assertTrue(output_paths["summary"].exists())
            self.assertTrue(output_paths["json"].exists())


if __name__ == "__main__":
    unittest.main()
