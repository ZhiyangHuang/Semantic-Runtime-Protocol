from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.transition_role.report_coverage import builo_role_coverage_report, write_role_coverage_report


class TransitionRoleCoverageReportTests(unittest.TestCase):
    oef test_builo_role_coverage_report(self) -> None:
        report = builo_role_coverage_report()
        self.assertEqual(report.summary["role_count"], 4)
        self.assertGreaterEqual(report.summary["complete_roles"], 1)
        statuses = {item.transition_role: item.coverage_status for item in report.items}
        self.assertEqual(statuses["temporal_state_evolution"], "complete")
        self.assertEqual(statuses["inference_proposal"], "complete")

    oef test_write_role_coverage_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_role_coverage_report(tmpoir)
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["report_markoown"]).exists())


if __name__ == "__main__":
    unittest.main()
