import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestSplitOperator(unittest.TestCase):
    def _build_merged_state(self) -> SemanticState:
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "merged_001": SemanticUnit(
                    unit_id="merged_001",
                    canonical_name="New York City",
                    aliases=["NYC"],
                    lineage=["u1", "u2"],
                    provenance=["source:a", "source:b", "merge:m1"],
                    semantic_payload={"entity_type": "location", "name": "New York City"},
                    activation=0.8,
                    confidence=0.9,
                    lifecycle_state="merged",
                    relation_ids=["r1", "r2"],
                )
            },
        )
        state.graph.add_unit(state.units["merged_001"])
        state.graph.relation_index["merged_001"] = ["neighbor_1", "neighbor_2"]
        state.units["merged_001"].version_id = "merge:m1"
        return state

    def test_split_operator_restores_lineage_units(self):
        state = self._build_merged_state()
        kernel = RuntimeKernel(state=state)
        event = RuntimeEvent(
            event_id="s1",
            event_type="Split",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["merged_001"],
            payload={
                "source_unit_id": "merged_001",
                "split_strategy": "lineage_restore",
                "generated_unit_ids": ["u1", "u2"],
                "child_payloads": {
                    "u1": {
                        "canonical_name": "NYC",
                        "aliases": ["New York City"],
                        "lineage": ["merged_001", "u1"],
                    },
                    "u2": {
                        "canonical_name": "New York City",
                        "aliases": ["NYC"],
                        "lineage": ["merged_001", "u2"],
                    },
                },
            },
            mutation_mode="update",
            operator_name="SplitOperator",
        )

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertEqual(transition.operator_name, "SplitOperator")
        self.assertEqual(kernel._state.units["merged_001"].lifecycle_state, "archived")
        self.assertIn("u1", kernel._state.units)
        self.assertIn("u2", kernel._state.units)
        self.assertEqual(kernel._state.units["u1"].lineage, ["merged_001", "u1"])
        self.assertEqual(kernel._state.units["u2"].lineage, ["merged_001", "u2"])
        self.assertEqual(kernel._state.units["u1"].canonical_name, "NYC")
        self.assertEqual(kernel._state.units["u2"].canonical_name, "New York City")
        self.assertIsNotNone(transition.metric_evidence)
        self.assertEqual(transition.metric_evidence_ref, "metric:s1")
        self.assertIn("merged_001", transition.changed_unit_ids)
        self.assertIn("u1", transition.changed_unit_ids)
        self.assertIn("u2", transition.changed_unit_ids)

    def test_split_operator_rejects_missing_lineage(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(
                    unit_id="u1",
                    canonical_name="alpha",
                    semantic_payload={"entity_type": "concept"},
                )
            },
        )
        state.graph.add_unit(state.units["u1"])
        event = RuntimeEvent(
            event_id="s2",
            event_type="Split",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={
                "source_unit_id": "u1",
                "split_strategy": "lineage_restore",
                "generated_unit_ids": ["u1a", "u1b"],
            },
            mutation_mode="update",
            operator_name="SplitOperator",
        )

        result = RuntimeKernel(state=state).submit_event(event)

        self.assertEqual(result.status, "rejected")

    def test_merge_then_split_replay_is_deterministic(self):
        initial_state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(
                    unit_id="u1",
                    canonical_name="NYC",
                    aliases=["New York City"],
                    lineage=["v1"],
                    provenance=["source:a"],
                    semantic_payload={"entity_type": "location"},
                    activation=0.8,
                    confidence=0.9,
                    relation_ids=["r1"],
                ),
                "u2": SemanticUnit(
                    unit_id="u2",
                    canonical_name="New York City",
                    aliases=["NYC"],
                    lineage=["v2"],
                    provenance=["source:b"],
                    semantic_payload={"entity_type": "location"},
                    activation=0.7,
                    confidence=0.85,
                    relation_ids=["r2"],
                ),
            },
        )
        initial_state.graph.add_unit(initial_state.units["u1"])
        initial_state.graph.add_unit(initial_state.units["u2"])
        initial_state.graph.relation_index["u1"] = ["u2"]
        initial_state.graph.relation_index["u2"] = ["u1"]

        merge_event = RuntimeEvent(
            event_id="m1",
            event_type="Merged",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "merged_unit_id": "merged_001",
                "canonical_name": "New York City",
                "aliases": ["NYC"],
            },
            mutation_mode="update",
            operator_name="MergeOperator",
        )
        split_event = RuntimeEvent(
            event_id="s3",
            event_type="Split",
            schema_version="1",
            causal_parent="m1",
            actor="tester",
            targets=["merged_001"],
            payload={
                "source_unit_id": "merged_001",
                "split_strategy": "lineage_restore",
                "generated_unit_ids": ["u1", "u2"],
                "child_payloads": {
                    "u1": {
                        "canonical_name": "NYC",
                        "aliases": ["New York City"],
                        "lineage": ["merged_001", "u1"],
                    },
                    "u2": {
                        "canonical_name": "New York City",
                        "aliases": ["NYC"],
                        "lineage": ["merged_001", "u2"],
                    },
                },
            },
            mutation_mode="update",
            operator_name="SplitOperator",
        )

        direct_kernel = RuntimeKernel(state=initial_state.snapshot())
        direct_kernel.apply_event(merge_event)
        direct_kernel.apply_event(split_event)

        replay = ReplayEngine().replay(initial_state, [merge_event, split_event])

        self.assertEqual(replay.reconstructed_state.version_id, direct_kernel._state.version_id)
        self.assertEqual(set(replay.reconstructed_state.units.keys()), set(direct_kernel._state.units.keys()))
        self.assertEqual(replay.reconstructed_state.units["merged_001"].lifecycle_state, "archived")
        self.assertEqual(replay.reconstructed_state.units["u1"].canonical_name, "NYC")
        self.assertEqual(replay.reconstructed_state.units["u2"].canonical_name, "New York City")


if __name__ == "__main__":
    unittest.main()
