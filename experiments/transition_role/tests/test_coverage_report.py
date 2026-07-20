from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.transition_role.report_coverage import build_role_coverage_report, write_role_coverage_report


class TransitionRoleCoverageReportTests(unittest.TestCase):
    def test_build_role_coverage_report(self) -> None:
        report = build_role_coverage_report()
        self.assertEqual(report.summary["role_count"], 4)
        self.assertGreaterEqual(report.summary["complete_roles"], 1)
        statuses = {item.transition_role: item.coverage_status for item in report.items}
        self.assertEqual(statuses["temporal_state_evolution"], "complete")
        self.assertEqual(statuses["inference_proposal"], "complete")

    def test_write_role_coverage_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_role_coverage_report(tmpdir)
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["report_markdown"]).exists())


if __name__ == "__main__":
    unittest.main()
