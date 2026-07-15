import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestApproximationOperator(unittest.TestCase):
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
                    semantic_payload={"entity_type": "concept", "name": "alpha"},
                    provenance=["source:1"],
                ),
                "u2": SemanticUnit(
                    unit_id="u2",
                    canonical_name="beta",
                    activation=0.1,
                    confidence=0.8,
                    semantic_payload={"entity_type": "concept", "name": "beta"},
                    provenance=["source:2"],
                ),
            },
        )
        state.graph.add_unit(state.units["u1"])
        state.graph.add_unit(state.units["u2"])
        state.graph.relation_index["u1"] = ["u2"]
        state.graph.relation_index["u2"] = ["u1"]
        return state

    def test_activation_based_approximation_marks_low_activation_units(self):
        state = self._build_state()
        kernel = RuntimeKernel(state=state)
        event = RuntimeEvent(
            event_id="a1",
            event_type="Approximated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "activation_threshold": 0.2,
                "representative_unit_id": "u1",
                "preserve_fields": ["entity_type", "name"],
            },
            mutation_mode="update",
            operator_name="ApproximationOperator",
        )

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertEqual(kernel._state.units["u1"].lifecycle_state, "active")
        self.assertEqual(kernel._state.units["u2"].lifecycle_state, "approximated")
        self.assertEqual(kernel._state.units["u2"].approximation_target, "u1")
        self.assertEqual(kernel._state.units["u2"].decay_state, "approximate")
        self.assertIn("u2", transition.changed_unit_ids)
        self.assertIn("u1", transition.changed_unit_ids)
        self.assertIsNotNone(transition.metric_evidence)
        self.assertEqual(transition.metric_evidence_ref, "metric:a1")
        self.assertGreaterEqual(transition.mutation_summary["approximation_loss"], 0.0)

    def test_identity_fields_are_preserved_during_approximation(self):
        state = self._build_state()
        event = RuntimeEvent(
            event_id="a2",
            event_type="Approximated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "activation_threshold": 0.2,
                "representative_unit_id": "u1",
                "preserve_fields": ["entity_type", "name"],
            },
            mutation_mode="update",
            operator_name="ApproximationOperator",
        )

        RuntimeKernel(state=state).apply_event(event)

        self.assertEqual(state.units["u2"].unit_id, "u2")
        self.assertEqual(state.units["u2"].canonical_name, "beta")
        self.assertIn("source:2", state.units["u2"].provenance)
        self.assertIn("u2", state.units)

    def test_approximation_replay_is_deterministic(self):
        initial_state = self._build_state()
        event = RuntimeEvent(
            event_id="a3",
            event_type="Approximated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={
                "activation_threshold": 0.2,
                "representative_unit_id": "u1",
                "preserve_fields": ["entity_type", "name"],
            },
            mutation_mode="update",
            operator_name="ApproximationOperator",
        )

        direct_kernel = RuntimeKernel(state=initial_state.snapshot())
        direct_kernel.apply_event(event)
        replay = ReplayEngine().replay(initial_state, [event])

        self.assertEqual(replay.reconstructed_state.version_id, direct_kernel._state.version_id)
        self.assertEqual(set(replay.reconstructed_state.units.keys()), set(direct_kernel._state.units.keys()))
        self.assertEqual(replay.reconstructed_state.units["u2"].lifecycle_state, "approximated")
        self.assertEqual(replay.reconstructed_state.units["u2"].approximation_target, "u1")


if __name__ == "__main__":
    unittest.main()
