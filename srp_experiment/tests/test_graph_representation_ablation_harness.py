import tempfile
import unittest
from pathlib import Path

from srp_experiment.graph_representation_ablation_harness import (
    build_graph_representation_suites,
    render_graph_representation_ablation_markdown,
    run_graph_representation_ablation,
    summarize_graph_representation_ablation,
    write_graph_representation_ablation_outputs,
)


class TestGraphRepresentationAblationHarness(unittest.TestCase):
    def test_graph_representation_ablation_exposes_fixed_groups(self):
        suites = build_graph_representation_suites()
        self.assertEqual(
            [suite.name for suite in suites[:4]],
            [
                "dependency_chain_A_text",
                "dependency_chain_B_structured",
                "dependency_chain_C_graph_v1",
                "dependency_chain_D_graph_v1_5",
            ],
        )
        self.assertEqual(suites[0].group, "A")
        self.assertEqual(suites[2].recovery_mode, "graph")
        self.assertEqual(suites[3].representation_version, "v1.5")

    def test_graph_representation_ablation_runs_graph_v1_and_v1_5(self):
        records = run_graph_representation_ablation(
            [
                "dependency_chain_A_text",
                "dependency_chain_B_structured",
                "dependency_chain_C_graph_v1",
                "dependency_chain_D_graph_v1_5",
            ],
            cycles=1,
            seeds=1,
        )
        self.assertEqual(len(records), 4)
        groups = {record["graph_representation_group"] for record in records}
        self.assertEqual(groups, {"A", "B", "C", "D"})
        graph_v1_5 = next(record for record in records if record["graph_representation_group"] == "D")
        self.assertEqual(graph_v1_5["graph_schema_version"], "semantic_runtime_graph.v1.5")
        self.assertIn("attribute_retention", graph_v1_5["semantic_graph_validation"])
        self.assertIn("state_retention", graph_v1_5["semantic_graph_validation"])
        self.assertIn("lifecycle_accuracy", graph_v1_5["semantic_graph_validation"])

    def test_graph_representation_summary_and_outputs(self):
        records = run_graph_representation_ablation(
            [
                "dependency_chain_C_graph_v1",
                "dependency_chain_D_graph_v1_5",
            ],
            cycles=1,
            seeds=1,
        )
        summary = summarize_graph_representation_ablation(records)
        self.assertEqual(summary["records"], 2)
        self.assertIn("C", summary["groups"])
        self.assertIn("D", summary["groups"])
        self.assertIn("graph_v1_5_minus_graph_v1", summary["comparison"])
        markdown = render_graph_representation_ablation_markdown(summary)
        self.assertIn("# Graph Representation Ablation", markdown)
        self.assertIn("Representation Deltas", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_graph_representation_ablation_outputs(records, Path(tmpdir))
            self.assertTrue(output_paths["jsonl"].exists())
            self.assertTrue(output_paths["csv"].exists())
            self.assertTrue(output_paths["markdown"].exists())
            self.assertTrue(output_paths["summary"].exists())
            self.assertTrue(output_paths["json"].exists())


if __name__ == "__main__":
    unittest.main()
