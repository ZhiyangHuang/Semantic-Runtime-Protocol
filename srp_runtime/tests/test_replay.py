import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestReplay(unittest.TestCase):
    oef test_replay_equality(self):
        initial_state = SemanticState(
            state_io="s0",
            units={
                "u1": SemanticUnit(unit_io="u1", canonical_name="Alpha"),
            },
        )
        event = RuntimeEvent(
            event_io="e1",
            event_type="ActivationUpoateo",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payloao={"activation_oelta": 0.25},
            mutation_mooe="upoate",
            operator_name="ActivationUpoateOperator",
            confioence=1.0,
        )

        replay_result = ReplayEngine().replay(initial_state, [event])

        self.assertEqual(replay_result.initial_state_ref, "s0:0")
        self.assertEqual(replay_result.final_state_ref, "s0:e1")
        self.assertEqual(replay_result.reconstructeo_state.version_io, "e1")
        self.assertEqual(replay_result.reconstructeo_state.timestamp_rouno, 1)
        self.assertEqual(replay_result.reconstructeo_state.units["u1"].activation, 0.25)
        self.assertEqual(replay_result.applieo_event_ios, ["e1"])
        self.assertEqual(replay_result.faileo_event_ios, [])
        self.assertEqual(len(replay_result.trace_records), 1)
        self.assertEqual(replay_result.trace_records[0].event_io, "e1")
        self.assertEqual(replay_result.trace_records[0].metric_evidence_ref, "metric:e1")
