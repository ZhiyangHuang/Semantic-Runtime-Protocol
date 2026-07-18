import tempfile
import unittest
from pathlib import Path

from experiments.analysis.semantic_failure_taxonomy import (
    build_semantic_failure_taxonomy,
    render_semantic_failure_taxonomy_markdown,
    write_semantic_failure_taxonomy_outputs,
)


class TestSemanticFailureTaxonomy(unittest.TestCase):
    def test_taxonomy_groups_multiple_failure_types(self):
        records = [
            {
                "task_id": "task-1",
                "compression_scenario": "budget_pressure",
                "experiment_result": {
                    "lifecycle_attribution": {
                        "transitions": {
                            "source_to_compressed": {
                                "missing": [
                                    {"object_id": "o1", "type": "fact", "value": "A moved to B"},
                                ],
                                "source_count": 2,
                            }
                        }
                    }
                },
                    "dependency_audit": {
                        "expected_labels": ["Only Alice can access the key", "John moved to Boston"],
                        "expected_count": 2,
                        "matched_count": 0,
                        "recovered_count": 1,
                    "matched_object_ids": [],
                    "recovered_object_ids": ["x1"],
                },
                "object_retention_breakdown_v2": {
                    "all_objects": {
                        "hallucinated": [
                            {"object_id": "h1", "type": "fact", "value": "unsupported"},
                        ],
                        "source_count": 2,
                        "recovered_count": 2,
                    },
                    "important": {"source_count": 1},
                },
                "state_allocation_result": {
                    "metrics": {
                        "active_object_count": 0,
                        "active_retention_ratio": 0.0,
                    }
                },
                "semantic_drift_from_initial": 0.2,
                "runtime_round": 2,
            },
            {
                "task_id": "task-2",
                "compression_scenario": "subject_collision",
                "experiment_result": {
                    "lifecycle_attribution": {
                        "transitions": {
                            "source_to_compressed": {
                                "missing": [
                                    {"object_id": "o2", "type": "fact", "value": "Atlas collision"},
                                ],
                                "source_count": 1,
                            }
                        }
                    }
                },
                "dependency_audit": {
                    "expected_labels": ["Orion owns Atlas in the payments lane"],
                    "expected_count": 1,
                    "matched_count": 0,
                    "recovered_count": 1,
                    "matched_object_ids": [],
                    "recovered_object_ids": ["x2"],
                },
                "object_retention_breakdown_v2": {
                    "all_objects": {
                        "hallucinated": [],
                        "source_count": 1,
                        "recovered_count": 1,
                    },
                    "important": {"source_count": 1},
                },
                "state_allocation_result": {
                    "metrics": {
                        "active_object_count": 0,
                        "active_retention_ratio": 0.0,
                    }
                },
            }
        ]

        taxonomy = build_semantic_failure_taxonomy(records)
        self.assertEqual(taxonomy["schema_version"], "semantic_failure_taxonomy.v1")
        self.assertEqual(taxonomy["records_processed"], 2)
        self.assertIn("object_loss", taxonomy["failure_types"])
        self.assertIn("dependency_break", taxonomy["failure_types"])
        self.assertIn("hallucinated_reconstruction", taxonomy["failure_types"])
        self.assertIn("allocation_failure", taxonomy["failure_types"])
        self.assertIn("temporal_drift", taxonomy["failure_types"])

        dependency_subtypes = taxonomy["failure_types"]["dependency_break"]["subtypes"]
        self.assertIn("constraint_loss", dependency_subtypes)
        self.assertIn("temporal_loss", dependency_subtypes)
        self.assertIn("identity_collision", dependency_subtypes)

        markdown = render_semantic_failure_taxonomy_markdown(taxonomy)
        self.assertIn("# Semantic Failure Taxonomy", markdown)
        self.assertIn("Representative Evidence", markdown)
        self.assertIn("object_loss", markdown)

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_semantic_failure_taxonomy_outputs(taxonomy, Path(tmpdir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["markdown"].exists())


if __name__ == "__main__":
    unittest.main()
