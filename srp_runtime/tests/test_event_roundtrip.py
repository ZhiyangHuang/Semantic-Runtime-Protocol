import unittest

from srp_runtime.event.runtime_event import RuntimeEvent


class TestEventRoundTrip(unittest.TestCase):
    def test_event_roundtrip(self):
        event = RuntimeEvent(
            event_id="e1",
            event_type="IdentityUpdated",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payload={"x": 1},
            mutation_mode="update",
            confidence=1.0,
        )
        self.assertEqual(RuntimeEvent.deserialize(event.serialize()), event)

