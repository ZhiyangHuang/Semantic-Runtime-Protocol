import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestGarbageCollectionOperator(unittest.TestCase):
    def _build_state(self, forgotten: bool = True) -> SemanticState:
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(
                    unit_id="u1",
                    canonical_name="alpha",
                    activation=0.9,
                    confidence=0.95,
                    semantic_payload={"entity_type": "concept", "name": "alpha", "detail": "source"},
                    provenance=["source:1"],
                    lineage=["u1"],
                ),
                "u2": SemanticUnit(
                    unit_id="u2",
                    canonical_name="beta",
                    activation=0.1,
                    confidence=0.8,
                    semantic_payload={"entity_type": "concept", "name": "beta", "detail": "source"},
                    provenance=["source:2"],
                    lineage=["u2"],
                    lifecycle_state="forgotten" if forgotten else "active",
                ),
            },
        )
        state.graph.add_unit(state.units["u1"])
        state.graph.add_unit(state.units["u2"])
        state.graph.relation_index["u1"] = ["u2"]
        state.graph.relation_index["u2"] = ["u1"]
        state.units["u1"].relation_ids = ["r:u1->u2"]
        state.units["u2"].relation_ids = ["r:u2->u1"]
        state.units["u2"].semantic_payload["archived_neighbors"] = ["u1"]
        state.units["u2"].semantic_payload["archived_relation_ids"] = ["r:u2->u1"]
        return state

    def test_gc_removes_forgotten_unit_from_active_storage(self):
        state = self._build_state(forgotten=True)
        kernel = RuntimeKernel(state=state)

        event = RuntimeEvent(
            event_id="g1",
            event_type="GarbageCollected",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u2"],
            payload={
                "target_unit_id": "u2",
                "retention_policy": "minimal_provenance",
                "gc_mode": "archive_compaction",
                "archive_ref": "archive:g1",
                "evidence_refs": ["trace:f1", "version:v1"],
            },
            mutation_mode="update",
            operator_name="GarbageCollectionOperator",
        )

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertNotIn("u2", kernel._state.units)
        self.assertNotIn("u2", kernel._state.graph.units)
        self.assertNotIn("u2", kernel._state.graph.relation_index)
        self.assertNotIn("u2", kernel._state.graph.relation_index["u1"])
        self.assertIn("u2", transition.changed_unit_ids)
        self.assertEqual(transition.operator_name, "GarbageCollectionOperator")
        self.assertTrue(transition.mutation_summary["irreversible"])
        self.assertIn("archive:g1", transition.mutation_summary["archive_ref"])

    def test_gc_rejects_active_identity_anchor(self):
        state = self._build_state(forgotten=False)
        state.units["u1"].semantic_payload["identity_anchor"] = True
        event = RuntimeEvent(
            event_id="g2",
            event_type="GarbageCollected",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={
                "target_unit_id": "u1",
                "retention_policy": "minimal_provenance",
                "gc_mode": "archive_compaction",
                "evidence_refs": ["trace:g2"],
            },
            mutation_mode="update",
            operator_name="GarbageCollectionOperator",
        )

        result = RuntimeKernel(state=state).submit_event(event)

        self.assertEqual(result.status, "rejected")

    def test_gc_replay_is_deterministic(self):
        initial_state = self._build_state(forgotten=True)
        event = RuntimeEvent(
            event_id="g3",
            event_type="GarbageCollected",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u2"],
            payload={
                "target_unit_id": "u2",
                "retention_policy": "minimal_provenance",
                "gc_mode": "archive_compaction",
                "archive_ref": "archive:g3",
                "evidence_refs": ["trace:g3"],
            },
            mutation_mode="update",
            operator_name="GarbageCollectionOperator",
        )

        direct_kernel = RuntimeKernel(state=initial_state.snapshot())
        direct_kernel.apply_event(event)

        replay = ReplayEngine().replay(initial_state, [event])

        self.assertEqual(replay.reconstructed_state.version_id, direct_kernel._state.version_id)
        self.assertEqual(set(replay.reconstructed_state.units.keys()), set(direct_kernel._state.units.keys()))
        self.assertNotIn("u2", replay.reconstructed_state.units)
        self.assertNotIn("u2", replay.reconstructed_state.graph.units)


if __name__ == "__main__":
    unittest.main()
