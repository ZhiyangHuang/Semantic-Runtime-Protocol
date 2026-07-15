from __future__ import annotations

import unittest

from experiments.validation.phase_ii_round1 import (
    collect_boundary_stability_observations,
    run_phase_ii_round1_validation_suite,
    run_reproducibility_check,
    summarize_authority_preservation,
    summarize_boundary_stability,
)


class PhaseIIRound1Tests(unittest.TestCase):
    def test_round1_suite_reports_four_boundary_classes(self) -> None:
        output = run_phase_ii_round1_validation_suite()
        report = output["report"]

        self.assertEqual(report["summary"]["boundary_class_count"], 4)
        self.assertEqual(report["summary"]["observation_count"], 16)
        self.assertIn("boundary_stability", report["sections"])
        self.assertIn("reproducibility", report["sections"])
        self.assertIn("authority_preservation", report["sections"])

    def test_boundary_stability_summary_is_complete(self) -> None:
        observations = collect_boundary_stability_observations()
        summary = summarize_boundary_stability(observations)

        self.assertEqual(summary["observation_count"], 16)
        self.assertEqual(len(summary["validated_boundary_classes"]), 4)
        self.assertIn("semantic mutation boundary", summary["boundary_classes"])
        self.assertIn("evidence acceptance boundary", summary["boundary_classes"])
        self.assertIn("history preservation boundary", summary["boundary_classes"])
        self.assertIn("archive enrichment boundary", summary["boundary_classes"])

    def test_reproducibility_check_is_stable(self) -> None:
        reproducibility = run_reproducibility_check()

        self.assertTrue(reproducibility["same_boundary_classes"])
        self.assertTrue(reproducibility["same_observation_count"])
        self.assertTrue(reproducibility["same_summary"])

    def test_authority_preservation_is_kept(self) -> None:
        authority = summarize_authority_preservation()

        self.assertTrue(authority["all_replay_equivalent"])
        self.assertTrue(authority["all_authority_preserved"])
        self.assertTrue(authority["all_evidence_consistent"])
        self.assertEqual(authority["observations_checked"], 16)


if __name__ == "__main__":
    unittest.main()
