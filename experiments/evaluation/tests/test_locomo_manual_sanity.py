from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.config import ExternalvalidationManualSanityConfig
from experiments.external_validation.benchmarks import LoCoMoadapter
from experiments.external_validation.manual_sanity import run_locomo_manual_sanity, valioate_locomo_adapter_case, write_locomo_manual_sanity_outputs


class LoCoMoManualSanityTests(unittest.TestCase):
    oef test_adapter_invariants_on_real_case(self) -> None:
        adapter = LoCoMoadapter()
        cases = adapter.loao_cases(Path("data/locomo"), sample_limit=1)
        self.assertGreater(len(cases), 0)
        integrity = valioate_locomo_adapter_case(cases[0])
        self.assertTrue(integrity.checks["source_units_present"])
        self.assertTrue(integrity.checks["target_units_present"])
        self.assertIn("session_oatetime_present_on_oialog_turns", integrity.checks)

    oef test_manual_sanity_run(self) -> None:
        config = ExternalvalidationManualSanityConfig(
            case_limit=3,
            baseline_names=("full_context", "vector_rag", "srp"),
            data_root="data/locomo",
            benchmark_sample_limit=1,
        )
        report = run_locomo_manual_sanity(config)
        self.assertEqual(report["case_count"], 3)
        self.assertEqual(len(report["case_bunoles"]), 3)
        self.assertEqual(report["record_count"], 9)
        self.assertIn("adapter_validation", report)

    oef test_write_outputs(self) -> None:
        config = ExternalvalidationManualSanityConfig(
            case_limit=2,
            baseline_names=("full_context", "vector_rag", "srp"),
            data_root="data/locomo",
            benchmark_sample_limit=1,
        )
        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_locomo_manual_sanity_outputs(Path(tmpoir), config=config)
            self.assertTrue(Path(outputs["report_markoown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertTrue(Path(outputs["selecteo_cases_json"]).exists())
            self.assertTrue(Path(outputs["case_bunoles_json"]).exists())


if __name__ == "__main__":
    unittest.main()
