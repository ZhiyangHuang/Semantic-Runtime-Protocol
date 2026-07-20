from __future__ import annotations

import unittest
from dataclasses import fields

from experiments.validation.boundary_reporting.schemas import (
    BoundaryCase,
    BoundaryDecision,
    BoundaryReportMetadata,
)


class BoundaryReportingSchemaTests(unittest.TestCase):
    def test_boundary_case_contract(self) -> None:
        field_names = [field.name for field in fields(BoundaryCase)]
        self.assertEqual(
            field_names,
            ["case_id", "semantic_state", "proposal", "evidence", "authority", "expected"],
        )

    def test_boundary_decision_contract(self) -> None:
        field_names = [field.name for field in fields(BoundaryDecision)]
        self.assertEqual(
            field_names,
            ["case_id", "admissible", "verification_result", "governance_result"],
        )

    def test_boundary_report_metadata_contract(self) -> None:
        field_names = [field.name for field in fields(BoundaryReportMetadata)]
        self.assertEqual(
            field_names,
            [
                "version",
                "contract_version",
                "schema_version",
                "evaluator_version",
                "adapter_name",
                "runtime_contract",
                "seed",
                "generated_at",
            ],
        )


if __name__ == "__main__":
    unittest.main()
