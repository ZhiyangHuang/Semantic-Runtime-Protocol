import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.operators.activation import ActivationUpdateOperator
from srp_runtime.operators.identity import IdentityUpdateOperator
from srp_runtime.operators.relation import RelationUpdateOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestOperators(unittest.TestCase):
    def test_identity_operator_preserves_unit_id(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(
                    unit_id="u1",
                    canonical_name="car",
                    aliases=["auto"],
                ),
            },
        )
        event = RuntimeEvent(
            event_id="e1",
            event_type="Canonicalized",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={
                "canonical_name": "automobile",
                "alias": "car",
                "provenance": ["source:1"],
                "lineage": ["v1"],
                "updated_round": 1,
            },
            mutation_mode="update",
            operator_name="IdentityUpdateOperator",
        )

        result = IdentityUpdateOperator().apply(state, event)

        self.assertTrue(result.success)
        self.assertEqual(result.before_state_ref, "s0:s0")
        self.assertEqual(result.after_state_ref, "s0:s0")
        self.assertEqual(state.units["u1"].unit_id, "u1")
        self.assertEqual(state.units["u1"].canonical_name, "automobile")
        self.assertIn("car", state.units["u1"].aliases)
        self.assertIn("auto", state.units["u1"].aliases)
        self.assertIn("source:1", state.units["u1"].provenance)
        self.assertIn("v1", state.units["u1"].lineage)

    def test_activation_operator_updates_activation_and_time(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            timestamp_round=10,
            units={
                "u1": SemanticUnit(unit_id="u1", canonical_name="alpha", activation=0.8),
            },
        )
        event = RuntimeEvent(
            event_id="e2",
            event_type="ActivationUpdated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={
                "activation_delta": -0.2,
                "confidence": 0.7,
            },
            mutation_mode="update",
            operator_name="ActivationUpdateOperator",
        )

        result = ActivationUpdateOperator().apply(state, event)

        self.assertTrue(result.success)
        self.assertAlmostEqual(state.units["u1"].activation, 0.6)
        self.assertAlmostEqual(state.units["u1"].confidence, 0.7)
        self.assertEqual(state.units["u1"].updated_round, 11)

    def test_relation_operator_adds_relation(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(unit_id="u1", canonical_name="alpha"),
                "u2": SemanticUnit(unit_id="u2", canonical_name="beta"),
            },
        )
        state.graph.add_unit(state.units["u1"])
        state.graph.add_unit(state.units["u2"])
        event = RuntimeEvent(
            event_id="e3",
            event_type="RelationUpdated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={"relation_ids": ["r1"]},
            mutation_mode="update",
            operator_name="RelationUpdateOperator",
        )

        result = RelationUpdateOperator().apply(state, event)

        self.assertTrue(result.success)
        self.assertIn("r1", state.units["u1"].relation_ids)
        self.assertIn("u2", state.graph.relation_index["u1"])
