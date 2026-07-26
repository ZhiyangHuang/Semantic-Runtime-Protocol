import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestForgettingOperator(unittest.TestCase):
    def _build_state(self) -> SemanticState:
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
                ),
            },
        )
        state.graph.add_unit(state.units["u1"])
        state.graph.add_unit(state.units["u2"])
        state.graph.relation_index["u1"] = ["u2"]
        state.graph.relation_index["u2"] = ["u1"]
        state.units["u1"].relation_ids = ["r:u1->u2"]
        state.units["u2"].relation_ids = ["r:u2->u1"]
        return state

    def test_forgetting_archives_active_representation(self):
        state = self._build_state()
        kernel = RuntimeKernel(state=state)

        event = RuntimeEvent(
            event_id="f1",
            event_type="Forgotten",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u2"],
            payload={
                "target_unit_id": "u2",
                "forget_reason": "low_activation",
                "preserve_evidence": True,
                "evidence_refs": ["trace:f1", "version:v1", "lineage:u2"],
            },
            mutation_mode="update",
            operator_name="ForgettingOperator",
        )

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertEqual(kernel._state.units["u2"].lifecycle_state, "forgotten")
        self.assertEqual(kernel._state.units["u2"].decay_state, "forgotten")
        self.assertEqual(kernel._state.units["u2"].relation_ids, [])
        self.assertEqual(kernel._state.graph.relation_index["u2"], [])
        self.assertNotIn("u2", kernel._state.graph.relation_index["u1"])
        self.assertIn("trace:f1", kernel._state.units["u2"].provenance)
        self.assertIn("u1", kernel._state.units["u2"].semantic_payload["archived_neighbors"])
        self.assertIn("r:u2->u1", kernel._state.units["u2"].semantic_payload["archived_relation_ids"])
        self.assertIn("u2", transition.changed_unit_ids)
        self.assertTrue(transition.metric_evidence is not None)
        self.assertEqual(transition.operator_name, "ForgettingOperator")

    def test_forgetting_requires_evidence(self):
        state = self._build_state()
        event = RuntimeEvent(
            event_id="f2",
            event_type="Forgotten",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u2"],
            payload={
                "target_unit_id": "u2",
                "forget_reason": "low_activation",
                "preserve_evidence": True,
            },
            mutation_mode="update",
            operator_name="ForgettingOperator",
        )

        result = RuntimeKernel(state=state).submit_event(event)

        self.assertEqual(result.status, "rejected")

    def test_merge_approximation_forgetting_recovery_replay_is_deterministic(self):
        initial_state = self._build_state()

        merge_event = RuntimeEvent(
            event_id="m1",
            event_type="Merged",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "merged_unit_id": "merged_1",
                "canonical_name": "alpha-beta",
                "semantic_payload": {
                    "entity_type": "concept",
                    "name": "alpha-beta",
                    "detail": "merged",
                },
            },
            mutation_mode="update",
            operator_name="MergeOperator",
        )
        approximation_event = RuntimeEvent(
            event_id="a1",
            event_type="Approximated",
            schema_version="1",
            causal_parent="m1",
            actor="tester",
            targets=["merged_1"],
            payload={
                "activation_threshold": 0.95,
                "representative_unit_id": "u1",
                "preserve_fields": ["entity_type", "name"],
            },
            mutation_mode="update",
            operator_name="ApproximationOperator",
        )
        forgetting_event = RuntimeEvent(
            event_id="f3",
            event_type="Forgotten",
            schema_version="1",
            causal_parent="a1",
            actor="tester",
            targets=["merged_1"],
            payload={
                "target_unit_id": "merged_1",
                "forget_reason": "low_activation",
                "preserve_evidence": True,
                "evidence_refs": ["trace:m1", "trace:a1", "version:v1"],
            },
            mutation_mode="update",
            operator_name="ForgettingOperator",
        )
        recovery_event = RuntimeEvent(
            event_id="r1",
            event_type="Recovered",
            schema_version="1",
            causal_parent="f3",
            actor="tester",
            targets=["merged_1"],
            payload={
                "target_unit_id": "merged_1",
                "recovery_source": "trace",
                "recovery_mode": "restore",
                "evidence_refs": ["trace:m1", "trace:a1", "trace:f3"],
                "restored_canonical_name": "alpha-beta",
                "restored_aliases": ["alpha", "beta"],
                "restored_lineage": ["u1", "u2", "merged_1"],
                "restored_provenance": ["source:1", "source:2", "trace:m1", "trace:a1", "trace:f3"],
                "restored_semantic_payload": {
                    "entity_type": "concept",
                    "name": "alpha-beta",
                    "detail": "restored",
                },
                "restored_relation_ids": ["r:u1->u2"],
                "restored_neighbors": ["u1"],
                "restored_activation": 0.6,
                "restored_confidence": 0.9,
                "restored_drift_score": 0.0,
                "restored_decay_state": "stable",
                "restored_version_id": "v2",
                "restored_last_used_round": 3,
                "restored_updated_round": 3,
                "restored_lifecycle_state": "active",
            },
            mutation_mode="update",
            operator_name="RecoveryOperator",
        )

        direct_kernel = RuntimeKernel(state=initial_state.snapshot())
        direct_kernel.apply_event(merge_event)
        direct_kernel.apply_event(approximation_event)
        direct_kernel.apply_event(forgetting_event)
        direct_kernel.apply_event(recovery_event)

        replay = ReplayEngine().replay(initial_state, [merge_event, approximation_event, forgetting_event, recovery_event])

        self.assertEqual(replay.reconstructed_state.version_id, direct_kernel._state.version_id)
        self.assertEqual(set(replay.reconstructed_state.units.keys()), set(direct_kernel._state.units.keys()))
        self.assertEqual(replay.reconstructed_state.units["merged_1"].lifecycle_state, "active")
        self.assertIn("trace:f3", replay.reconstructed_state.units["merged_1"].provenance)
        self.assertEqual(replay.reconstructed_state.units["merged_1"].semantic_payload["detail"], "restored")


if __name__ == "__main__":
    unittest.main()
