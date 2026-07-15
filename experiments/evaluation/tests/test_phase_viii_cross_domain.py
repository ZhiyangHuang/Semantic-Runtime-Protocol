from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.config import PhaseVIIICrossDomainValidationConfig
from experiments.evaluation.phase_viii_cross_domain.metrics import evaluate_cross_domain_runs, summarize_cross_domain_results
from experiments.evaluation.phase_viii_cross_domain.runner import build_cross_domain_runs, run_phase_viii_cross_domain, write_phase_viii_cross_domain_outputs


class PhaseVIIICrossDomainValidationTests(unittest.TestCase):
    def test_build_runs(self) -> None:
        runs = build_cross_domain_runs(PhaseVIIICrossDomainValidationConfig())
        self.assertGreaterEqual(len(runs), 6)
        self.assertEqual(runs[0].domain_name, "code_memory")

    def test_summary(self) -> None:
        config = PhaseVIIICrossDomainValidationConfig()
        runs = build_cross_domain_runs(config)
        records = evaluate_cross_domain_runs(runs)
        summary = summarize_cross_domain_results(records)
        self.assertEqual(summary["case_count"], len(runs))
        self.assertIn("domain_summary", summary)
        self.assertIn("mode_summary", summary)

    def test_write_outputs(self) -> None:
        config = PhaseVIIICrossDomainValidationConfig()
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_phase_viii_cross_domain_outputs(Path(tmpdir) / "phase_viii_cross_domain", config=config)
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["records_csv"]).exists())

    def test_run_roundtrip(self) -> None:
        output = run_phase_viii_cross_domain(PhaseVIIICrossDomainValidationConfig())
        self.assertIn("report", output)
        self.assertEqual(output["report"]["status"], "evaluated")


if __name__ == "__main__":
    unittest.main()
