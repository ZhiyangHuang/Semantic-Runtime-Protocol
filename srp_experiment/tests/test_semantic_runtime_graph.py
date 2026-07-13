import unittest

from srp_experiment.srp.semantic_graph import build_semantic_runtime_graph
from srp_experiment.srp.semantic_graph_validator import validate_semantic_runtime_graph
from srp_experiment.srp.semantic_parser import stable_semantic_object_id
from srp_experiment.srp.validation_targets import build_validation_targets


class TestSemanticRuntimeGraph(unittest.TestCase):
    def test_build_semantic_runtime_graph_tracks_lifecycle_and_validation(self):
        task = {
            "id": "graph-v1-task",
            "initial_state": {
                "constraints": ["Keep the key constraint."],
                "memory": "Keep the key constraint. The answer is B.",
            },
            "query_expectations": [[["Keep the key constraint."]]],
            "expected_keywords": ["constraint", "answer"],
            "semantic_dependencies": {
                "required_dependency_objects": [
                    {
                        "dependency_id": "dep-1",
                        "subject": {"type": "entity", "canonical": "John"},
                        "relation": {"type": "relation", "canonical": "owns"},
                        "object": {"type": "entity", "canonical": "Key"},
                    }
                ]
            },
        }
        source_package = {
            "memory": "Keep the key constraint. The answer is B.",
            "constraints": ["Keep the key constraint."],
            "semantic_object_inventory": {
                "objects": [
                    {
                        "object_id": stable_semantic_object_id("constraint", "Keep the key constraint."),
                        "type": "constraint",
                        "value": "Keep the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "constraint:1",
                    },
                    {
                        "object_id": stable_semantic_object_id("fact", "The answer is B."),
                        "type": "fact",
                        "value": "The answer is B.",
                        "confidence": 0.9,
                        "evidence_pointer": "memory:2",
                    },
                ],
                "important_objects": [
                    {
                        "object_id": stable_semantic_object_id("constraint", "Keep the key constraint."),
                        "type": "constraint",
                        "value": "Keep the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "constraint:1",
                    }
                ],
            },
            "runtime_metadata": {
                stable_semantic_object_id("constraint", "Keep the key constraint."): {"importance": 0.9}
            },
        }
        recovered_package = {
            "typed_representation": {
                "objects": [
                    {
                        "type": "constraint",
                        "value": "Keep the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "constraint:1",
                        "metadata": {},
                    },
                    {
                        "type": "fact",
                        "value": "Recovered extra detail.",
                        "confidence": 0.4,
                        "evidence_pointer": "memory:3",
                        "metadata": {},
                    },
                ]
            }
        }

        graph = build_semantic_runtime_graph(
            source_package,
            recovered_package,
            build_validation_targets(task),
        )
        graph_dict = graph.as_dict()
        self.assertEqual(graph_dict["schema_version"], "semantic_runtime_graph.v1")
        self.assertGreaterEqual(graph_dict["summary"]["node_count"], 3)
        self.assertGreaterEqual(graph_dict["summary"]["edge_count"], 2)
        self.assertIn("validation", graph_dict["summary"])

        validation = validate_semantic_runtime_graph(graph)
        self.assertEqual(validation.schema_version, "semantic_graph_validation.v1")
        self.assertGreaterEqual(validation.source_node_count, 1)
        self.assertGreaterEqual(validation.recovered_node_count, 1)
        self.assertGreaterEqual(validation.retained_node_count, 1)
        self.assertGreaterEqual(validation.hallucinated_node_count, 1)
        self.assertIsNotNone(validation.graph_integrity_score)


if __name__ == "__main__":
    unittest.main()
