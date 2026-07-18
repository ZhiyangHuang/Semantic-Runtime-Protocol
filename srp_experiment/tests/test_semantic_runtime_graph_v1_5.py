import unittest

from experiments.srp_runtime_legacy.srp.semantic_graph import build_semantic_runtime_graph_v1_5
from experiments.srp_runtime_legacy.srp.semantic_graph_validator import validate_semantic_runtime_graph_v1_5
from experiments.srp_runtime_legacy.srp.semantic_parser import stable_semantic_object_id
from experiments.srp_runtime_legacy.srp.validation_targets import build_validation_targets


class TestSemanticRuntimeGraphV15(unittest.TestCase):
    def test_build_semantic_runtime_graph_v1_5_tracks_richer_state(self):
        task = {
            "id": "graph-v15-task",
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
        source_object_id = stable_semantic_object_id("constraint", "Keep the key constraint.")
        source_package = {
            "memory": "Keep the key constraint. The answer is B.",
            "constraints": ["Keep the key constraint."],
            "semantic_object_inventory": {
                "objects": [
                    {
                        "object_id": source_object_id,
                        "type": "constraint",
                        "value": "Keep the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "constraint:1",
                        "metadata": {"domain": "test"},
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
                        "object_id": source_object_id,
                        "type": "constraint",
                        "value": "Keep the key constraint.",
                        "confidence": 1.0,
                        "evidence_pointer": "constraint:1",
                    }
                ],
            },
            "runtime_metadata": {
                source_object_id: {"importance": 0.9}
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
                        "metadata": {"recovered": True},
                    },
                    {
                        "type": "fact",
                        "value": "Recovered extra detail.",
                        "confidence": 0.4,
                        "evidence_pointer": "memory:3",
                        "metadata": {"recovered": True},
                    },
                ]
            }
        }

        graph = build_semantic_runtime_graph_v1_5(
            source_package,
            recovered_package,
            build_validation_targets(task),
        )
        graph_dict = graph.as_v1_5_dict()
        self.assertEqual(graph_dict["schema_version"], "semantic_runtime_graph.v1.5")
        self.assertGreaterEqual(graph_dict["summary"]["node_count"], 3)
        self.assertIn("validation_v1_5", graph_dict["summary"])
        self.assertEqual(graph_dict["summary"]["validation_v1_5"]["schema_version"], "semantic_graph_validation.v1.5")
        object_node = next(node for node in graph_dict["nodes"] if node["id"] == source_object_id)
        self.assertIn("identity", object_node)
        self.assertIn("properties", object_node["attributes"])
        self.assertIn("state", object_node["attributes"])
        self.assertIsInstance(object_node["importance"], dict)
        self.assertIn("modified", object_node["lifecycle"])

        validation = validate_semantic_runtime_graph_v1_5(graph)
        self.assertEqual(validation.schema_version, "semantic_graph_validation.v1.5")
        self.assertIsNotNone(validation.attribute_retention)
        self.assertIsNotNone(validation.state_retention)
        self.assertIsNotNone(validation.lifecycle_accuracy)
        self.assertGreaterEqual(validation.graph_integrity_score, 0.0)


if __name__ == "__main__":
    unittest.main()
