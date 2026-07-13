import os
import unittest

from srp_experiment.srp.recover import recover_state
from srp_experiment.srp.semantic_parser import stable_semantic_object_id


class TestGraphRecoveryPolicy(unittest.TestCase):
    def test_graph_recovery_policy_attaches_graph_metrics_and_closure(self):
        previous_mode = os.environ.get("SRP_RECOVERY_MODE")
        try:
            os.environ["SRP_RECOVERY_MODE"] = "graph"
            package = {
                "memory": "John owns the key. John cannot enter Room A.",
                "constraints": ["John cannot enter Room A."],
                "semantic_object_inventory": {
                    "objects": [
                        {
                            "object_id": stable_semantic_object_id("entity", "John"),
                            "type": "entity",
                            "value": "John",
                            "confidence": 0.9,
                            "evidence_pointer": "memory:1",
                        },
                        {
                            "object_id": stable_semantic_object_id("relation", "owns"),
                            "type": "relation",
                            "value": "owns",
                            "confidence": 0.8,
                            "evidence_pointer": "memory:1",
                        },
                        {
                            "object_id": stable_semantic_object_id("entity", "Key"),
                            "type": "entity",
                            "value": "Key",
                            "confidence": 0.8,
                            "evidence_pointer": "memory:1",
                        },
                        {
                            "object_id": stable_semantic_object_id("fact", "Noise detail"),
                            "type": "fact",
                            "value": "Noise detail",
                            "confidence": 0.2,
                            "evidence_pointer": "memory:2",
                        },
                    ],
                    "important_objects": [
                        {
                            "object_id": stable_semantic_object_id("entity", "John"),
                            "type": "entity",
                            "value": "John",
                            "confidence": 0.9,
                            "evidence_pointer": "memory:1",
                        }
                    ],
                },
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

            recovered = recover_state(package, client=None)
            state_dict = recovered.as_dict()
            self.assertEqual(state_dict["reconstruction_result"]["policy_name"], "graph")
            self.assertIn("graph_recovery_result", state_dict["reconstruction_result"])
            self.assertIn("graph_recovery_result", state_dict["recovered_state_package"])
            graph_result = state_dict["reconstruction_result"]["graph_recovery_result"]
            self.assertGreaterEqual(graph_result["dependency_closure_rate"], 0.0)
            self.assertGreaterEqual(graph_result["graph_recovery_precision"], 0.0)
            self.assertGreaterEqual(graph_result["repair_cost"], 1)
            self.assertIn("semantic_runtime_graph", state_dict["recovered_state_package"])
            self.assertEqual(
                state_dict["recovered_state_package"]["semantic_runtime_graph"]["schema_version"],
                "semantic_runtime_graph.v1",
            )
        finally:
            if previous_mode is None:
                os.environ.pop("SRP_RECOVERY_MODE", None)
            else:
                os.environ["SRP_RECOVERY_MODE"] = previous_mode


if __name__ == "__main__":
    unittest.main()
