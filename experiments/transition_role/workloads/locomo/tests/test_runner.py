from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.transition_role.workloads.locomo.runner import build_locomo_role_coverage_run, write_locomo_role_coverage_bundle


class LoCoMoRoleCoverageTests(unittest.TestCase):
    def test_build_role_coverage_run(self) -> None:
        run = build_locomo_role_coverage_run(data_root=Path("data/locomo"))
        self.assertEqual(run.role_manifest["transition_role"]["id"], "temporal_state_evolution")
        self.assertEqual(run.role_manifest["transition_role"]["workload"], "LoCoMo")
        self.assertIn("official_metric_score", run.official_summary)
        self.assertIn("semantic_coverage", run.srp_diagnostics)

    def test_write_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_locomo_role_coverage_bundle(tmpdir, data_root=Path("data/locomo"))
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["role_manifest_json"]).exists())


if __name__ == "__main__":
    unittest.main()
