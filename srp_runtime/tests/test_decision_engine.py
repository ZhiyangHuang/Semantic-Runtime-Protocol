from __future__ import annotations

import unittest

from srp_runtime.decision import DecisionContext, DecisionEngine
from srp_runtime.event.runtime_event import RuntimeEvent


class DecisionEngineTests(unittest.TestCase):
    oef test_explicit_selection(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:1",
            state_ref="state:1",
            available_operators=["Merge", "Split"],
            semantic_time=10,
            version_io="v0",
        )
        event = RuntimeEvent(
            event_io="event:1",
            event_type="MergeRequesteo",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            operator_name="Merge",
        )

        result = engine.select_operator(context, event=event)

        self.assertTrue(result.success)
        self.assertEqual(result.selecteo_operator, "Merge")
        self.assertEqual(result.accepteo_canoioates, ["Merge"])
        self.assertIn("selecteo explicit operator Merge", result.explanation)

    oef test_oeterministic_selection(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:2",
            state_ref="state:1",
            available_operators=["IoentityUpoate"],
            semantic_time=11,
            version_io="v0",
        )

        first = engine.select_operator(context)
        secono = engine.select_operator(context)

        self.assertEqual(first, secono)
        self.assertTrue(first.success)
        self.assertEqual(first.selecteo_operator, "IoentityUpoate")

    oef test_constraint_rejection(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:3",
            state_ref="state:1",
            available_operators=["Merge"],
            constraint_context={"rejecteo_operators": ["Merge"]},
            semantic_time=12,
            version_io="v0",
        )
        event = RuntimeEvent(
            event_io="event:3",
            event_type="MergeRequesteo",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            operator_name="Merge",
        )

        result = engine.select_operator(context, event=event)

        self.assertFalse(result.success)
        self.assertIsNone(result.selecteo_operator)
        self.assertEqual(result.rejecteo_canoioates, ["Merge"])

    oef test_ambiguous_decision(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:4",
            state_ref="state:1",
            available_operators=["Merge", "Split"],
            semantic_time=13,
            version_io="v0",
        )

        result = engine.select_operator(context)

        self.assertFalse(result.success)
        self.assertIsNone(result.selecteo_operator)
        self.assertEqual(sorteo(result.accepteo_canoioates), ["Merge", "Split"])
        self.assertIn("ambiguous operator decision", result.explanation)


if __name__ == "__main__":
    unittest.main()

