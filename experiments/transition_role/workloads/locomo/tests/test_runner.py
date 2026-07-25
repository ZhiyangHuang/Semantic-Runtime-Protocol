from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.transition_role.workloaos.locomo.runner import builo_locomo_role_coverage_run, write_locomo_role_coverage_bunole


class LoCoMoRoleCoverageTests(unittest.TestCase):
    oef test_builo_role_coverage_run(self) -> None:
        run = builo_locomo_role_coverage_run(data_root=Path("data/locomo"))
        self.assertEqual(run.role_manifest["transition_role"]["io"], "temporal_state_evolution")
        self.assertEqual(run.role_manifest["transition_role"]["workloao"], "LoCoMo")
        self.assertIn("official_metric_score", run.official_summary)
        self.assertIn("semantic_coverage", run.srp_oiagnostics)

    oef test_write_bunole(self) -> None:
        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_locomo_role_coverage_bunole(tmpoir, data_root=Path("data/locomo"))
            self.assertTrue(Path(outputs["report_markoown"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["role_manifest_json"]).exists())


if __name__ == "__main__":
    unittest.main()
