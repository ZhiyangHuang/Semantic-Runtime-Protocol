from __future__ import annotations

import unittest

from experiments.validation.phase_ii_closure_validation import run_boundary_validation_case, run_phase_ii_closure_validation_suite
from experiments.validation.phase_ii_closure_validation import build_validation_scenarios


class PhaseIICClosureValidationTests(unittest.TestCase):
    def test_suite_covers_four_boundary_classes(self) -> None:
        output = run_phase_ii_closure_validation_suite()
        summary = output["report"]["summary"]

        self.assertEqual(len(summary["validated_boundary_classes"]), 4)
        self.assertIn("semantic mutation boundary", summary["boundary_classes"])
        self.assertIn("evidence acceptance boundary", summary["boundary_classes"])
        self.assertIn("history preservation boundary", summary["boundary_classes"])
        self.assertIn("archive enrichment boundary", summary["boundary_classes"])

    def test_activation_boundary_is_stable_under_workload_variation(self) -> None:
        baseline = run_boundary_validation_case("activation_threshold", 0.5, build_validation_scenarios()[0])
        stressed = run_boundary_validation_case("activation_threshold", 0.5, build_validation_scenarios()[1])

        self.assertFalse(baseline.boundary_shift)
        self.assertFalse(stressed.boundary_shift)
        self.assertTrue(baseline.replay_equivalent)
        self.assertTrue(stressed.replay_equivalent)
        self.assertTrue(baseline.authority_preserved)
        self.assertTrue(stressed.authority_preserved)

    def test_recovery_boundary_can_shift_with_evidence_volume(self) -> None:
        baseline = run_boundary_validation_case("recovery_min_evidence", 4, build_validation_scenarios()[0])
        evidence_heavy = run_boundary_validation_case("recovery_min_evidence", 4, build_validation_scenarios()[3])

        self.assertFalse(baseline.observed_verdict)
        self.assertTrue(evidence_heavy.observed_verdict)
        self.assertFalse(baseline.boundary_shift)
        self.assertTrue(evidence_heavy.boundary_shift)
        self.assertTrue(baseline.replay_equivalent)
        self.assertTrue(evidence_heavy.replay_equivalent)

    def test_history_and_archive_boundaries_preserve_authority(self) -> None:
        preserve_true = run_boundary_validation_case("preserve_evidence", True, build_validation_scenarios()[0])
        archive_true = run_boundary_validation_case("archive_relations", True, build_validation_scenarios()[0])

        self.assertTrue(preserve_true.authority_preserved)
        self.assertTrue(archive_true.authority_preserved)
        self.assertTrue(preserve_true.replay_equivalent)
        self.assertTrue(archive_true.replay_equivalent)
        self.assertFalse(preserve_true.boundary_shift)
        self.assertFalse(archive_true.boundary_shift)

    def test_reproducibility_is_deterministic(self) -> None:
        first = run_phase_ii_closure_validation_suite()
        second = run_phase_ii_closure_validation_suite()

        self.assertEqual(first["report"]["summary"]["validated_boundary_classes"], second["report"]["summary"]["validated_boundary_classes"])
        self.assertEqual(len(first["report"]["observations"]), len(second["report"]["observations"]))


if __name__ == "__main__":
    unittest.main()
