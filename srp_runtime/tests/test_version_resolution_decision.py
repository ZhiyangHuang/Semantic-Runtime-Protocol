from __future__ import annotations

import unittest

from srp_runtime.version import ResolutionContext, ResolutionDecisionService


class VersionResolutionDecisionTests(unittest.TestCase):
    def test_resolution_decision_uses_available_actions(self) -> None:
        service = ResolutionDecisionService()
        context = ResolutionContext(
            resolution_id="resolution:1",
            conflict_id="conflict:divergence:v0",
            source_versions=["v0", "v1"],
            evidence_refs=["trace:v1"],
            conflict_type="semantic_divergence",
            available_actions=["AcceptBranch", "MergeProposal"],
            decision_constraints=["deterministic"],
        )

        decision = service.evaluate(context)

        self.assertEqual(decision.resolution_id, "resolution:1")
        self.assertEqual(decision.conflict_id, "conflict:divergence:v0")
        self.assertEqual(decision.selected_action, "AcceptBranch")
        self.assertEqual(decision.rationale_refs, ["trace:v1"])
        self.assertEqual(decision.created_event_intent["event_type"], "SemanticCorrectionRequested")
        self.assertEqual(decision.created_event_intent["target_intent"], "AcceptBranch")

    def test_resolution_decision_falls_back_to_reject_branch(self) -> None:
        service = ResolutionDecisionService()
        context = ResolutionContext(
            resolution_id="resolution:2",
            conflict_id="conflict:duplicate:t1",
        )

        decision = service.evaluate(context)

        self.assertEqual(decision.selected_action, "RejectBranch")
        self.assertEqual(decision.confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
