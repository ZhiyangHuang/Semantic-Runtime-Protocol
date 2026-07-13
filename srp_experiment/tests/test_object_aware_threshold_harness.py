import tempfile
import unittest
from pathlib import Path

from srp_experiment.object_aware_threshold_harness import (
    build_threshold_analysis_tasks,
    render_object_aware_threshold_analysis_markdown,
    run_object_aware_threshold_analysis,
    write_object_aware_threshold_analysis_outputs,
)


class TestObjectAwareThresholdHarness(unittest.TestCase):
    def test_threshold_analysis_exposes_three_rq_sections(self):
        results = run_object_aware_threshold_analysis()
        self.assertEqual(
            list(results.keys()),
            [
                "rq2_1_budget_threshold",
                "rq2_2_ambiguity_threshold",
                "rq2_3_support_threshold",
            ],
        )

        budget = results["rq2_1_budget_threshold"]
        ambiguity = results["rq2_2_ambiguity_threshold"]
        support = results["rq2_3_support_threshold"]

        self.assertEqual(budget["research_question"], "RQ2.1 Budget Threshold")
        self.assertEqual(ambiguity["research_question"], "RQ2.2 Ambiguity Threshold")
        self.assertEqual(support["research_question"], "RQ2.3 Support Threshold")

        self.assertEqual(ambiguity["keyword_overlap_levels"], [0.2, 0.4, 0.6, 0.8, 0.95])
        self.assertIn("dbi_mean", budget)
        self.assertIn("decision_boundary_index_mean", ambiguity)
        self.assertIn("decision_flip_distance_mean", support)

        for section in results.values():
            for sweep in section["sweeps"]:
                self.assertIn("dbi", sweep)
                self.assertIn("decision_flip_distance", sweep)
                self.assertIn("topk_changed", sweep)

    def test_threshold_analysis_markdown_and_outputs(self):
        results = run_object_aware_threshold_analysis()
        markdown = render_object_aware_threshold_analysis_markdown(results)
        self.assertIn("# Object-Aware Compression Threshold Analysis", markdown)
        self.assertIn("RQ2.1 Budget Threshold", markdown)
        self.assertIn("RQ2.2 Ambiguity Threshold", markdown)
        self.assertIn("RQ2.3 Support Threshold", markdown)
        self.assertIn("DBI", markdown)
        self.assertIn("Decoy count is held fixed", markdown)

        tasks = build_threshold_analysis_tasks()
        self.assertEqual(len(tasks), 7)
        self.assertEqual([task.name for task in tasks[:2]], ["budget_threshold", "ambiguity_0p2"])

        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_object_aware_threshold_analysis_outputs(results, Path(tmpdir))
            self.assertTrue(output_paths["json"].exists())
            self.assertTrue(output_paths["markdown"].exists())


if __name__ == "__main__":
    unittest.main()
