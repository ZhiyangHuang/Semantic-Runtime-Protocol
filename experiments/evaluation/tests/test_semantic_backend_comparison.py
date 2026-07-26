from __future__ import annotations

import unittest

from experiments.config import SemanticBackendComparisonConfig
from experiments.evaluation.semantic_backend_comparison.runner import run_semantic_backend_comparison


class SemanticBackendComparisonTests(unittest.TestCase):
    def test_comparison_produces_report(self) -> None:
        config = SemanticBackendComparisonConfig(local_model_enabled=False, fallback_to_heuristic=True)
        output = run_semantic_backend_comparison(config=config)

        report = output["report"]
        self.assertEqual(report["summary"]["case_count"], 10)
        self.assertEqual(len(report["records"]), 10)
        self.assertIn("agreement_rate", report["summary"])
        self.assertIn("vector_false_acceptance", report["summary"])
        self.assertIn("variant_false_rejection", report["summary"])
        self.assertIn("authority_violation_case_count", report["summary"])
        self.assertIn("authority_violation_final_accept_rate", report["summary"])
        self.assertIn("review_rate", report["summary"])
        self.assertIn("semantic evidence backend", output["markdown"])

    def test_report_contains_authority_separation(self) -> None:
        config = SemanticBackendComparisonConfig(local_model_enabled=False, fallback_to_heuristic=True)
        output = run_semantic_backend_comparison(config=config)

        self.assertIn("The local model does not mutate state", output["markdown"])
        self.assertIn("The local model does not approve deployment", output["markdown"])
        self.assertIn("Authority violation cases", output["markdown"])
        self.assertIn("Escalation Routing", output["markdown"])

    def test_write_outputs(self) -> None:
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from experiments.evaluation.semantic_backend_comparison.runner import write_semantic_backend_comparison_outputs

        with TemporaryDirectory() as tmpdir:
            outputs = write_semantic_backend_comparison_outputs(Path(tmpdir) / "semantic_backend_comparison")
            self.assertTrue(Path(outputs["records_csv"]).exists())
            self.assertTrue(Path(outputs["records_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["figures"]["backend_summary_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["backend_summary_pdf"]).exists())


if __name__ == "__main__":
    unittest.main()
