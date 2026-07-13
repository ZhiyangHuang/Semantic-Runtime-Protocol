import unittest

from srp_experiment.srp.runtime_representation import build_runtime_representation_v2
from srp_experiment.srp.state import SemanticState


class TestRuntimeRepresentationV2(unittest.TestCase):
    def test_build_runtime_representation_v2_produces_layers_and_projection(self):
        state = SemanticState(
            memory="John bought milk. User: Can I enter? Assistant: No, you cannot enter.",
            constraints=["Only John can enter the room."],
        )

        representation = build_runtime_representation_v2(state, anchor_memory="John bought milk.")
        data = representation.as_dict()
        graph = representation.project_graph()

        self.assertEqual(data["schema_version"], "srr.v2")
        self.assertGreaterEqual(len(data["objects"]), 2)
        self.assertGreaterEqual(len(data["frames"]), 1)
        self.assertGreaterEqual(len(data["conversations"]), 1)
        self.assertIn("provenance_completeness", data["summary"])
        self.assertGreaterEqual(data["summary"]["provenance_completeness"], 0.0)
        self.assertIn("nodes", graph)
        self.assertIn("edges", graph)
        self.assertGreaterEqual(graph["node_count"], len(data["objects"]))
        self.assertGreaterEqual(graph["edge_count"], 0)


if __name__ == "__main__":
    unittest.main()
