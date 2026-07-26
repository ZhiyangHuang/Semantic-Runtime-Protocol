import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestMergeOperator(unittest.TestCase):
    def _build_merge_state(self) -> SemanticState:
        state = SemanticState(
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
        state.graph.add_unit(state.units["u1"])
        state.graph.add_unit(state.units["u2"])
        state.graph.relation_index["u1"] = ["u2"]
        state.graph.relation_index["u2"] = ["u1"]
        return state

    def test_merge_operator_merges_candidate_units(self):
        state = self._build_merge_state()
        kernel = RuntimeKernel(state=state)
        event = RuntimeEvent(
            event_id="m1",
            event_type="Merged",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "merged_unit_id": "u3",
                "canonical_name": "New York City",
                "aliases": ["NYC"],
                "provenance": ["merge:1"],
            },
            mutation_mode="update",
            operator_name="MergeOperator",
        )

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertEqual(transition.operator_name, "MergeOperator")
        self.assertIn("u3", kernel._state.units)
        self.assertEqual(kernel._state.units["u3"].canonical_name, "New York City")
        self.assertIn("u1", kernel._state.units["u3"].lineage)
        self.assertIn("u2", kernel._state.units["u3"].lineage)
        self.assertIn("NYC", kernel._state.units["u3"].aliases)
        self.assertEqual(kernel._state.units["u1"].lifecycle_state, "merged")
        self.assertEqual(kernel._state.units["u2"].lifecycle_state, "merged")
        self.assertIsNotNone(transition.metric_evidence)
        self.assertEqual(transition.metric_evidence_ref, "metric:m1")
        self.assertIn("u3", transition.changed_unit_ids)

    def test_merge_operator_rejects_identity_conflict(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(
                    unit_id="u1",
                    canonical_name="Apple",
                    semantic_payload={"entity_type": "company"},
                ),
                "u2": SemanticUnit(
                    unit_id="u2",
                    canonical_name="Apple",
                    semantic_payload={"entity_type": "fruit"},
                ),
            },
        )
        state.graph.add_unit(state.units["u1"])
        state.graph.add_unit(state.units["u2"])
        event = RuntimeEvent(
            event_id="m2",
            event_type="Merged",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "merged_unit_id": "u3",
                "canonical_name": "Apple",
            },
            mutation_mode="update",
            operator_name="MergeOperator",
        )

        result = RuntimeKernel(state=state).submit_event(event)

        self.assertEqual(result.status, "rejected")
        self.assertTrue(
            any(
                violation == "merge requires matching entity_type across source units"
                for violation in RuntimeKernel(state=state).validate_event(event).violations
            )
        )

    def test_merge_replay_is_deterministic(self):
        initial_state = self._build_merge_state()
        event = RuntimeEvent(
            event_id="m3",
            event_type="Merged",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "merged_unit_id": "u3",
                "canonical_name": "New York City",
            },
            mutation_mode="update",
            operator_name="MergeOperator",
        )

        direct_kernel = RuntimeKernel(state=initial_state.snapshot())
        direct_kernel.apply_event(event)
        replay = ReplayEngine().replay(initial_state, [event])

        self.assertEqual(replay.reconstructed_state.version_id, direct_kernel._state.version_id)
        self.assertEqual(set(replay.reconstructed_state.units.keys()), set(direct_kernel._state.units.keys()))
        self.assertEqual(replay.reconstructed_state.units["u3"].canonical_name, "New York City")
        self.assertEqual(replay.reconstructed_state.units["u3"].lineage, direct_kernel._state.units["u3"].lineage)


if __name__ == "__main__":
    unittest.main()
