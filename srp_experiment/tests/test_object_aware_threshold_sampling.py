import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.object_aware_threshold_sampling import (
    render_object_aware_threshold_sampling_markdown,
    run_object_aware_threshold_sampling,
    write_object_aware_threshold_sampling_outputs,
)


class TestObjectAwareThresholdSampling(unittest.TestCase):
    def test_sampling_returns_statistics(self):
        results = run_object_aware_threshold_sampling([1, 2, 3])
        self.assertEqual(results["schema_version"], "object_support_threshold_sampling.v1")
        self.assertEqual(results["seeds"], [1, 2, 3])

        summary = results["summary"]
        self.assertIn("rq2_1_budget_threshold", summary)
        self.assertIn("rq2_2_ambiguity_threshold", summary)
        self.assertIn("rq2_3_support_threshold", summary)

        budget_rows = summary["rq2_1_budget_threshold"]
        self.assertTrue(budget_rows)
        self.assertIn("flip_probability", budget_rows[0])
        self.assertIn("dbi", budget_rows[0])
        self.assertIn("decision_margin", budget_rows[0])
        self.assertIn("ci_low", budget_rows[0]["dbi"])
        self.assertIn("ci_high", budget_rows[0]["dbi"])

    def test_sampling_markdown_and_outputs(self):
        results = run_object_aware_threshold_sampling([1, 2])
        markdown = render_object_aware_threshold_sampling_markdown(results)
        self.assertIn("# Object-Aware Threshold Sampling", markdown)
        self.assertIn("RQ2.1 Budget Threshold", markdown)
        self.assertIn("Flip Probability", markdown)
        self.assertIn("95% CI", markdown)

        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_object_aware_threshold_sampling_outputs(results, Path(tmpdir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["markdown"].exists())


if __name__ == "__main__":
    unittest.main()
