import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestKernelTransition(unittest.TestCase):
    def test_kernel_transition_and_trace(self):
        initial_state = SemanticState(
            state_id="s0",
            version_id="s0",
            units={
                "u1": SemanticUnit(unit_id="u1", canonical_name="Alpha"),
            },
        )
        kernel = RuntimeKernel(state=initial_state)
        event = RuntimeEvent(
            event_id="e1",
            event_type="ActivationUpdated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={"activation_delta": 0.25},
            mutation_mode="update",
            operator_name="ActivationUpdateOperator",
            confidence=1.0,
        )

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertEqual(kernel.get_state().version_id, "e1")
        self.assertEqual(kernel.get_state().timestamp_round, 1)
        self.assertEqual(kernel.get_state().unit_ids, ["u1"])
        self.assertAlmostEqual(kernel._state.units["u1"].activation, 0.25)
        self.assertIsNotNone(transition.metric_evidence)
        self.assertEqual(transition.metric_evidence_ref, "metric:e1")

        trace_records = kernel.trace_records
        self.assertEqual(len(trace_records), 1)
        self.assertEqual(trace_records[0].event_id, "e1")
        self.assertEqual(trace_records[0].before_version, "s0:s0")
        self.assertEqual(trace_records[0].after_version, "s0:e1")
        self.assertEqual(trace_records[0].metric_evidence_ref, "metric:e1")
