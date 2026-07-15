import unittest

from srp_runtime.constraints.constraint_engine import ConstraintEngine
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestConstraints(unittest.TestCase):
    def test_identity_violation(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(unit_id="u1", canonical_name="Alpha"),
            },
        )
        event = RuntimeEvent(
            event_id="e1",
            event_type="ActivationUpdated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={"unit_id": "u2", "activation_delta": 0.1},
            mutation_mode="update",
            operator_name="ActivationUpdateOperator",
        )

        result = ConstraintEngine().validate(state, event)

        self.assertFalse(result.accepted)
        self.assertIn("unit_id cannot change during an update", result.violations)

    def test_dangling_relation_violation(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(unit_id="u1", canonical_name="Alpha"),
            },
        )
        event = RuntimeEvent(
            event_id="e2",
            event_type="RelationUpdated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payload={"relation_ids": ["r1"]},
            mutation_mode="update",
            operator_name="RelationUpdateOperator",
        )

        result = ConstraintEngine().validate(state, event)

        self.assertFalse(result.accepted)
        self.assertTrue(
            any(
                violation.startswith("missing target units:")
                or violation.startswith("relation endpoint missing:")
                for violation in result.violations
            )
        )

    def test_invalid_lifecycle_transition(self):
        state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(
                    unit_id="u1",
                    canonical_name="Alpha",
                    lifecycle_state="forgotten",
                ),
            },
        )
        event = RuntimeEvent(
            event_id="e3",
            event_type="ActivationUpdated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={"lifecycle_state": "active", "activation_delta": 0.1},
            mutation_mode="update",
            operator_name="ActivationUpdateOperator",
        )

        result = ConstraintEngine().validate(state, event)

        self.assertFalse(result.accepted)
        self.assertIn(
            "forgotten units require recovery before becoming active",
            result.violations,
        )

