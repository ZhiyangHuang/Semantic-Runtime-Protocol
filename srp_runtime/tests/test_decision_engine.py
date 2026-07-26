from __future__ import annotations

import unittest

from srp_runtime.decision import DecisionContext, DecisionEngine
from srp_runtime.event.runtime_event import RuntimeEvent


class DecisionEngineTests(unittest.TestCase):
    def test_explicit_selection(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:1",
            state_ref="state:1",
            available_operators=["Merge", "Split"],
            semantic_time=10,
            version_id="v0",
        )
        event = RuntimeEvent(
            event_id="event:1",
            event_type="MergeRequested",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            operator_name="Merge",
        )

        result = engine.select_operator(context, event=event)

        self.assertTrue(result.success)
        self.assertEqual(result.selected_operator, "Merge")
        self.assertEqual(result.accepted_candidates, ["Merge"])
        self.assertIn("selected explicit operator Merge", result.explanation)

    def test_deterministic_selection(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:2",
            state_ref="state:1",
            available_operators=["IdentityUpdate"],
            semantic_time=11,
            version_id="v0",
        )

        first = engine.select_operator(context)
        second = engine.select_operator(context)

        self.assertEqual(first, second)
        self.assertTrue(first.success)
        self.assertEqual(first.selected_operator, "IdentityUpdate")

    def test_constraint_rejection(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:3",
            state_ref="state:1",
            available_operators=["Merge"],
            constraint_context={"rejected_operators": ["Merge"]},
            semantic_time=12,
            version_id="v0",
        )
        event = RuntimeEvent(
            event_id="event:3",
            event_type="MergeRequested",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            operator_name="Merge",
        )

        result = engine.select_operator(context, event=event)

        self.assertFalse(result.success)
        self.assertIsNone(result.selected_operator)
        self.assertEqual(result.rejected_candidates, ["Merge"])

    def test_ambiguous_decision(self) -> None:
        engine = DecisionEngine()
        context = DecisionContext(
            event_ref="event:4",
            state_ref="state:1",
            available_operators=["Merge", "Split"],
            semantic_time=13,
            version_id="v0",
        )

        result = engine.select_operator(context)

        self.assertFalse(result.success)
        self.assertIsNone(result.selected_operator)
        self.assertEqual(sorted(result.accepted_candidates), ["Merge", "Split"])
        self.assertIn("ambiguous operator decision", result.explanation)


if __name__ == "__main__":
    unittest.main()

