import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.trace.trace_builder import TraceBuilder


class TestTrace(unittest.TestCase):
    def test_trace_record(self):
        before = SemanticState(
            state_id="s0",
            units={
                "u1": SemanticUnit(unit_id="u1", canonical_name="Alpha"),
            },
            version_id="s0",
            timestamp_round=0,
        )
        after = SemanticState(
            state_id="s0",
            units={
                "u1": SemanticUnit(unit_id="u1", canonical_name="Alpha"),
            },
            version_id="e1",
            timestamp_round=1,
        )
        event = RuntimeEvent(
            event_id="e1",
            event_type="ActivationUpdated",
            schema_version="1",
            causal_parent="s0",
            actor="tester",
            targets=["u1"],
            payload={"activation_delta": 0.25},
            mutation_mode="update",
            operator_name="ActivationUpdateOperator",
            confidence=1.0,
        )

        transition = TransitionResult(
            transition_id="tr:e1",
            event_id="e1",
            operator_name="ActivationUpdateOperator",
            before_state_ref="s0:s0",
            after_state_ref="s0:e1",
            changed_unit_ids=["u1"],
            changed_relation_ids=[],
            mutation_summary={"explanation": "transition recorded"},
            invariant_checks=["activation.range"],
            metric_evidence_ref="metric:e1",
            metric_evidence={
                "source_id": "u1",
                "target_id": "u1",
                "total_distance": 0.0,
                "component_scores": {
                    "identity_distance": 0.0,
                    "semantic_distance": 0.0,
                    "structural_distance": 0.0,
                    "temporal_distance": 0.0,
                },
                "comparable": True,
                "explanation": "self-comparison",
            },
            success=True,
            timestamp_round=1,
        )

        record = TraceBuilder().record_transition(event, transition)

        self.assertEqual(record.event_id, "e1")
        self.assertEqual(record.transition_id, "tr:e1")
        self.assertEqual(record.before_version, "s0:s0")
        self.assertEqual(record.after_version, "s0:e1")
        self.assertEqual(record.metric_evidence_ref, "metric:e1")
        self.assertEqual(record.mutation_mode, "update")
