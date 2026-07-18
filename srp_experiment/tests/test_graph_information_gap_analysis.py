import tempfile
import unittest
from pathlib import Path

from experiments.analysis.graph_information_gap_analysis import (
    build_graph_information_gap_analysis,
    render_graph_information_gap_analysis_markdown,
    write_graph_information_gap_outputs,
)


class TestGraphInformationGapAnalysis(unittest.TestCase):
    def test_gap_analysis_classifies_schema_level_gaps(self):
        records = [
            {
                "task_id": "task-1",
                "graph_recovery_scenario": "dependency_chain",
                "semantic_runtime_graph": {
                    "nodes": [
                        {
                            "id": "n1",
                            "type": "entity",
                            "label": "John",
                            "attributes": {"evidence_pointer": "memory:1"},
                            "lifecycle": {
                                "created": True,
                                "compressed": True,
                                "recovered": True,
                                "verified": True,
                                "retained": True,
                                "source_present": True,
                                "recovered_present": True,
                            },
                        },
                        {
                            "id": "n2",
                            "type": "constraint",
                            "label": "John cannot enter Room A",
                            "attributes": {"evidence_pointer": "constraint:1"},
                            "lifecycle": {
                                "created": True,
                                "compressed": True,
                                "recovered": False,
                                "verified": False,
                                "retained": False,
                                "source_present": True,
                                "recovered_present": False,
                            },
                        },
                    ],
                    "edges": [
                        {"edge_id": "e1", "source": "root", "target": "n1", "relation": "contains"},
                    ],
                },
                "semantic_graph_validation": {
                    "source_node_count": 2,
                    "recovered_node_count": 2,
                    "retained_node_count": 1,
                    "missing_node_count": 1,
                    "hallucinated_node_count": 1,
                    "dependency_edge_count": 0,
                    "missing_dependency_count": 1,
                    "constraint_node_count": 1,
                    "constraint_violation_count": 1,
                    "object_survival_rate": 0.5,
                    "dependency_recall": 0.0,
                    "constraint_accuracy": 0.0,
                    "hallucination_rate": 0.5,
                    "graph_integrity_score": 0.25,
                    "issues": {
                        "dependency": [{"node_id": "n2", "issue": "missing_dependency_edge"}],
                        "constraint": [{"node_id": "n2", "issue": "constraint_missing_in_recovery"}],
                        "hallucination": [{"node_id": "n3", "issue": "hallucinated_node"}],
                    },
                },
                "graph_recovery_result": {
                    "repair_cost": 4,
                    "dependency_closure_rate": 0.5,
                    "graph_recovery_precision": 1.0,
                },
            }
        ]

        analysis = build_graph_information_gap_analysis(records)
        self.assertEqual(analysis["schema_version"], "graph_information_gap_analysis.v1")
        self.assertEqual(analysis["records_processed"], 1)
        self.assertIn("missing_node", analysis["failure_types"])
        self.assertIn("missing_edge", analysis["failure_types"])
        self.assertIn("missing_attribute", analysis["failure_types"])
        self.assertIn("missing_lifecycle", analysis["failure_types"])
        markdown = render_graph_information_gap_analysis_markdown(analysis)
        self.assertIn("# Graph Information Gap Analysis", markdown)
        self.assertIn("Representative Evidence", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_graph_information_gap_outputs(analysis, Path(tmpdir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["markdown"].exists())


if __name__ == "__main__":
    unittest.main()
