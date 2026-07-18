import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.reconstruction_policy_harness import (
    build_reconstruction_policy_suites,
    render_reconstruction_policy_summary_markdown,
    run_reconstruction_policy_comparison,
    summarize_reconstruction_policy_comparison,
    write_reconstruction_policy_outputs,
)


class TestReconstructionPolicyHarness(unittest.TestCase):
    def test_reconstruction_policy_harness_exposes_fixed_suite_names(self):
        suites = build_reconstruction_policy_suites()
        self.assertEqual([suite.name for suite in suites], ["unrestricted", "constrained", "minimal"])
        self.assertEqual(suites[0].reconstruction_policy, "unrestricted")
        self.assertEqual(suites[1].reconstruction_policy, "constrained")
        self.assertEqual(suites[2].reconstruction_policy, "minimal")

    def test_reconstruction_policy_harness_runs_all_modes(self):
        records = run_reconstruction_policy_comparison(["unrestricted", "constrained", "minimal"], cycles=1)
        self.assertEqual(len(records), 3)
        policies = {record["reconstruction_policy_suite"]: record["reconstruction_policy"] for record in records}
        self.assertEqual(policies["unrestricted"], "unrestricted")
        self.assertEqual(policies["constrained"], "constrained")
        self.assertEqual(policies["minimal"], "minimal")
        self.assertTrue(all("experiment_result" in record for record in records))

    def test_reconstruction_policy_summary_and_outputs(self):
        records = run_reconstruction_policy_comparison(["unrestricted", "minimal"], cycles=1)
        summary = summarize_reconstruction_policy_comparison(records)
        self.assertEqual(summary["records"], 2)
        self.assertIn("unrestricted", summary["suites"])
        self.assertIn("reconstruction_precision", summary["suites"]["unrestricted"])
        markdown = render_reconstruction_policy_summary_markdown(summary)
        self.assertIn("# Reconstruction Policy Comparison", markdown)
        self.assertIn("Reconstruction Selectivity", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_reconstruction_policy_outputs(records, Path(tmpdir))
            self.assertTrue(output_paths["jsonl"].exists())
            self.assertTrue(output_paths["csv"].exists())
            self.assertTrue(output_paths["markdown"].exists())
            self.assertTrue(output_paths["summary"].exists())


if __name__ == "__main__":
    unittest.main()
