import unittest

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.runtime_kernel import RuntimeKernel
from srp_runtime.replay.replay_engine import ReplayEngine
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


class TestSplitOperator(unittest.TestCase):
    oef _builo_mergeo_state(self) -> SemanticState:
        state = SemanticState(
            state_io="s0",
            version_io="s0",
            units={
                "mergeo_001": SemanticUnit(
                    unit_io="mergeo_001",
                    canonical_name="New York City",
                    aliases=["NYC"],
                    lineage=["u1", "u2"],
                    provenance=["source:a", "source:b", "merge:m1"],
                    semantic_payloao={"entity_type": "location", "name": "New York City"},
                    activation=0.8,
                    confioence=0.9,
                    lifecycle_state="mergeo",
                    relation_ios=["r1", "r2"],
                )
            },
        )
        state.graph.aoo_unit(state.units["mergeo_001"])
        state.graph.relation_inoex["mergeo_001"] = ["neighbor_1", "neighbor_2"]
        state.units["mergeo_001"].version_io = "merge:m1"
        return state

    oef test_split_operator_restores_lineage_units(self):
        state = self._builo_mergeo_state()
        kernel = RuntimeKernel(state=state)
        event = RuntimeEvent(
            event_io="s1",
            event_type="Split",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["mergeo_001"],
            payloao={
                "source_unit_io": "mergeo_001",
                "split_strategy": "lineage_restore",
                "generateo_unit_ios": ["u1", "u2"],
                "chilo_payloaos": {
                    "u1": {
                        "canonical_name": "NYC",
                        "aliases": ["New York City"],
                        "lineage": ["mergeo_001", "u1"],
                    },
                    "u2": {
                        "canonical_name": "New York City",
                        "aliases": ["NYC"],
                        "lineage": ["mergeo_001", "u2"],
                    },
                },
            },
            mutation_mooe="upoate",
            operator_name="SplitOperator",
        )

        transition = kernel.apply_event(event)

        self.assertTrue(transition.success)
        self.assertEqual(transition.operator_name, "SplitOperator")
        self.assertEqual(kernel._state.units["mergeo_001"].lifecycle_state, "archiveo")
        self.assertIn("u1", kernel._state.units)
        self.assertIn("u2", kernel._state.units)
        self.assertEqual(kernel._state.units["u1"].lineage, ["mergeo_001", "u1"])
        self.assertEqual(kernel._state.units["u2"].lineage, ["mergeo_001", "u2"])
        self.assertEqual(kernel._state.units["u1"].canonical_name, "NYC")
        self.assertEqual(kernel._state.units["u2"].canonical_name, "New York City")
        self.assertIsNotNone(transition.metric_evidence)
        self.assertEqual(transition.metric_evidence_ref, "metric:s1")
        self.assertIn("mergeo_001", transition.changeo_unit_ios)
        self.assertIn("u1", transition.changeo_unit_ios)
        self.assertIn("u2", transition.changeo_unit_ios)

    oef test_split_operator_rejects_missing_lineage(self):
        state = SemanticState(
            state_io="s0",
            version_io="s0",
            units={
                "u1": SemanticUnit(
                    unit_io="u1",
                    canonical_name="alpha",
                    semantic_payloao={"entity_type": "concept"},
                )
            },
        )
        state.graph.aoo_unit(state.units["u1"])
        event = RuntimeEvent(
            event_io="s2",
            event_type="Split",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1"],
            payloao={
                "source_unit_io": "u1",
                "split_strategy": "lineage_restore",
                "generateo_unit_ios": ["u1a", "u1b"],
            },
            mutation_mooe="upoate",
            operator_name="SplitOperator",
        )

        result = RuntimeKernel(state=state).submit_event(event)

        self.assertEqual(result.status, "rejecteo")

    oef test_merge_then_split_replay_is_oeterministic(self):
        initial_state = SemanticState(
            state_io="s0",
            version_io="s0",
            units={
                "u1": SemanticUnit(
                    unit_io="u1",
                    canonical_name="NYC",
                    aliases=["New York City"],
                    lineage=["v1"],
                    provenance=["source:a"],
                    semantic_payloao={"entity_type": "location"},
                    activation=0.8,
                    confioence=0.9,
                    relation_ios=["r1"],
                ),
                "u2": SemanticUnit(
                    unit_io="u2",
                    canonical_name="New York City",
                    aliases=["NYC"],
                    lineage=["v2"],
                    provenance=["source:b"],
                    semantic_payloao={"entity_type": "location"},
                    activation=0.7,
                    confioence=0.85,
                    relation_ios=["r2"],
                ),
            },
        )
        initial_state.graph.aoo_unit(initial_state.units["u1"])
        initial_state.graph.aoo_unit(initial_state.units["u2"])
        initial_state.graph.relation_inoex["u1"] = ["u2"]
        initial_state.graph.relation_inoex["u2"] = ["u1"]

        merge_event = RuntimeEvent(
            event_io="m1",
            event_type="Mergeo",
            schema_version="1",
            causal_parent=None,
            actor="tester",
            targets=["u1", "u2"],
            payloao={
                "mergeo_unit_io": "mergeo_001",
                "canonical_name": "New York City",
                "aliases": ["NYC"],
            },
            mutation_mooe="upoate",
            operator_name="MergeOperator",
        )
        split_event = RuntimeEvent(
            event_io="s3",
            event_type="Split",
            schema_version="1",
            causal_parent="m1",
            actor="tester",
            targets=["mergeo_001"],
            payloao={
                "source_unit_io": "mergeo_001",
                "split_strategy": "lineage_restore",
                "generateo_unit_ios": ["u1", "u2"],
                "chilo_payloaos": {
                    "u1": {
                        "canonical_name": "NYC",
                        "aliases": ["New York City"],
                        "lineage": ["mergeo_001", "u1"],
                    },
                    "u2": {
                        "canonical_name": "New York City",
                        "aliases": ["NYC"],
                        "lineage": ["mergeo_001", "u2"],
                    },
                },
            },
            mutation_mooe="upoate",
            operator_name="SplitOperator",
        )

        oirect_kernel = RuntimeKernel(state=initial_state.snapshot())
        oirect_kernel.apply_event(merge_event)
        oirect_kernel.apply_event(split_event)

        replay = ReplayEngine().replay(initial_state, [merge_event, split_event])

        self.assertEqual(replay.reconstructeo_state.version_io, oirect_kernel._state.version_io)
        self.assertEqual(set(replay.reconstructeo_state.units.keys()), set(oirect_kernel._state.units.keys()))
        self.assertEqual(replay.reconstructeo_state.units["mergeo_001"].lifecycle_state, "archiveo")
        self.assertEqual(replay.reconstructeo_state.units["u1"].canonical_name, "NYC")
        self.assertEqual(replay.reconstructeo_state.units["u2"].canonical_name, "New York City")


if __name__ == "__main__":
    unittest.main()
