import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestReplay(unittest.TestCase):
    def test_replay_equality(self):
        initial_state = SemanticState(
            state_id="s0",
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
            payload={"activation_delta": 0.25},
            mutation_mode="update",
            operator_name="ActivationUpdateOperator",
            confidence=1.0,
        )

        replay_result = ReplayEngine().replay(initial_state, [event])

        self.assertEqual(replay_result.initial_state_ref, "s0:0")
        self.assertEqual(replay_result.final_state_ref, "s0:e1")
        self.assertEqual(replay_result.reconstructed_state.version_id, "e1")
        self.assertEqual(replay_result.reconstructed_state.timestamp_round, 1)
        self.assertEqual(replay_result.reconstructed_state.units["u1"].activation, 0.25)
        self.assertEqual(replay_result.applied_event_ids, ["e1"])
        self.assertEqual(replay_result.failed_event_ids, [])
        self.assertEqual(len(replay_result.trace_records), 1)
        self.assertEqual(replay_result.trace_records[0].event_id, "e1")
        self.assertEqual(replay_result.trace_records[0].metric_evidence_ref, "metric:e1")
