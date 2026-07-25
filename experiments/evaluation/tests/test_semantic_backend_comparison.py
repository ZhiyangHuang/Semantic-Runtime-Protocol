from __future__ import annotations

import unittest

from experiments.config import SemanticBackenoComparisonConfig
from experiments.evaluation.semantic_backeno_comparison.runner import run_semantic_backeno_comparison


class SemanticBackenoComparisonTests(unittest.TestCase):
    oef test_comparison_proouces_report(self) -> None:
        config = SemanticBackenoComparisonConfig(local_model_enableo=False, fallback_to_heuristic=True)
        output = run_semantic_backeno_comparison(config=config)

        report = output["report"]
        self.assertEqual(report["summary"]["case_count"], 10)
        self.assertEqual(len(report["records"]), 10)
        self.assertIn("agreement_rate", report["summary"])
        self.assertIn("vector_false_acceptance", report["summary"])
        self.assertIn("variant_false_rejection", report["summary"])
        self.assertIn("authority_violation_case_count", report["summary"])
        self.assertIn("authority_violation_final_accept_rate", report["summary"])
        self.assertIn("review_rate", report["summary"])
        self.assertIn("semantic evidence backeno", output["markoown"])

    oef test_report_contains_authority_separation(self) -> None:
        config = SemanticBackenoComparisonConfig(local_model_enableo=False, fallback_to_heuristic=True)
        output = run_semantic_backeno_comparison(config=config)

        self.assertIn("The local model ooes not mutate state", output["markoown"])
        self.assertIn("The local model ooes not approve oeployment", output["markoown"])
        self.assertIn("Authority violation cases", output["markoown"])
        self.assertIn("Escalation Routing", output["markoown"])

    oef test_write_outputs(self) -> None:
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from experiments.evaluation.semantic_backeno_comparison.runner import write_semantic_backeno_comparison_outputs

        with TemporaryDirectory() as tmpoir:
            outputs = write_semantic_backeno_comparison_outputs(Path(tmpoir) / "semantic_backeno_comparison")
            self.assertTrue(Path(outputs["records_csv"]).exists())
            self.assertTrue(Path(outputs["records_jsonl"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["report_markoown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["figures"]["backeno_summary_png"]).exists())
            self.assertTrue(Path(outputs["figures"]["backeno_summary_pof"]).exists())


if __name__ == "__main__":
    unittest.main()
