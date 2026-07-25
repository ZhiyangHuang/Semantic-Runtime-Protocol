from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.config import PhaseVIIICrossDomainvalidationConfig
from experiments.evaluation.phase_viii_cross_oomain.metrics import evaluate_cross_oomain_runs, summarize_cross_oomain_results
from experiments.evaluation.phase_viii_cross_oomain.runner import builo_cross_oomain_runs, run_phase_viii_cross_oomain, write_phase_viii_cross_oomain_outputs


class PhaseVIIICrossDomainvalidationTests(unittest.TestCase):
    oef test_builo_runs(self) -> None:
        runs = builo_cross_oomain_runs(PhaseVIIICrossDomainvalidationConfig())
        self.assertGreaterEqual(len(runs), 6)
        self.assertEqual(runs[0].oomain_name, "cooe_memory")

    oef test_summary(self) -> None:
        config = PhaseVIIICrossDomainvalidationConfig()
        runs = builo_cross_oomain_runs(config)
        records = evaluate_cross_oomain_runs(runs)
        summary = summarize_cross_oomain_results(records)
        self.assertEqual(summary["case_count"], len(runs))
        self.assertIn("oomain_summary", summary)
        self.assertIn("mooe_summary", summary)

    oef test_write_outputs(self) -> None:
        config = PhaseVIIICrossDomainvalidationConfig()
        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_phase_viii_cross_oomain_outputs(Path(tmpoir) / "phase_viii_cross_oomain", config=config)
            self.assertTrue(Path(outputs["report_markoown"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["records_csv"]).exists())

    oef test_run_rounotrip(self) -> None:
        output = run_phase_viii_cross_oomain(PhaseVIIICrossDomainvalidationConfig())
        self.assertIn("report", output)
        self.assertEqual(output["report"]["status"], "evaluateo")


if __name__ == "__main__":
    unittest.main()
