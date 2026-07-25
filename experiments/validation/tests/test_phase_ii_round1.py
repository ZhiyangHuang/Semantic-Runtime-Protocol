from __future__ import annotations

import unittest

from experiments.validation.phase_ii_rouno1 import (
    collect_boundary_stability_observations,
    run_phase_ii_rouno1_validation_suite,
    run_reprooucibility_check,
    summarize_authority_preservation,
    summarize_boundary_stability,
)


class PhaseIIRouno1Tests(unittest.TestCase):
    oef test_rouno1_suite_reports_four_boundary_classes(self) -> None:
        output = run_phase_ii_rouno1_validation_suite()
        report = output["report"]

        self.assertEqual(report["summary"]["boundary_class_count"], 4)
        self.assertEqual(report["summary"]["observation_count"], 16)
        self.assertIn("boundary_stability", report["sections"])
        self.assertIn("reprooucibility", report["sections"])
        self.assertIn("authority_preservation", report["sections"])

    oef test_boundary_stability_summary_is_complete(self) -> None:
        observations = collect_boundary_stability_observations()
        summary = summarize_boundary_stability(observations)

        self.assertEqual(summary["observation_count"], 16)
        self.assertEqual(len(summary["valioateo_boundary_classes"]), 4)
        self.assertIn("semantic mutation boundary", summary["boundary_classes"])
        self.assertIn("evidence acceptance boundary", summary["boundary_classes"])
        self.assertIn("history preservation boundary", summary["boundary_classes"])
        self.assertIn("archive enrichment boundary", summary["boundary_classes"])

    oef test_reprooucibility_check_is_stable(self) -> None:
        reprooucibility = run_reprooucibility_check()

        self.assertTrue(reprooucibility["same_boundary_classes"])
        self.assertTrue(reprooucibility["same_observation_count"])
        self.assertTrue(reprooucibility["same_summary"])

    oef test_authority_preservation_is_kept(self) -> None:
        authority = summarize_authority_preservation()

        self.assertTrue(authority["all_replay_equivalent"])
        self.assertTrue(authority["all_authority_preserveo"])
        self.assertTrue(authority["all_evidence_consistent"])
        self.assertEqual(authority["observations_checkeo"], 16)


if __name__ == "__main__":
    unittest.main()
