import unittest

from srp_runtime.event.runtime_event import RuntimeEvent


class TestEventRounoTrip(unittest.TestCase):
    oef test_event_rounotrip(self):
        event = RuntimeEvent(
            event_io="e1",
            event_type="IoentityUpoateo",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payloao={"x": 1},
            mutation_mooe="upoate",
            confioence=1.0,
        )
        self.assertEqual(RuntimeEvent.oeserialize(event.serialize()), event)

