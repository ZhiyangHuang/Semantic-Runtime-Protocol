from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.validation.boundary_reporting.adapters import resolve_adapter
from experiments.validation.boundary_reporting.evaluator import evaluate_cases
from experiments.validation.boundary_reporting.generator import load_cases_from_jsonl
from experiments.validation.boundary_reporting.matrix import run_consistency_matrix
from experiments.validation.boundary_reporting.reporter import generate_report
from experiments.validation.boundary_reporting.schemas import BoundaryReportMetadata


class ArtifactHashStabilityTests(unittest.TestCase):
    def test_same_inputs_same_report_hash(self) -> None:
        fixtures_root = Path("experiments/validation/boundary_reporting/fixtures/matrix_cases")

        with tempfile.TemporaryDirectory() as tmpdir:
            first = run_consistency_matrix(
                fixtures_root=fixtures_root,
                output_dir=Path(tmpdir) / "first",
                runtime_contract="boundary-v1",
                seed=42,
            )
            second = run_consistency_matrix(
                fixtures_root=fixtures_root,
                output_dir=Path(tmpdir) / "second",
                runtime_contract="boundary-v1",
                seed=42,
            )

            self.assertEqual(first["metadata"]["matrix_hash"], second["metadata"]["matrix_hash"])
            self.assertEqual(first["metadata"]["adapter_hash"], second["metadata"]["adapter_hash"])
            self.assertEqual(first["summary"], second["summary"])

    def test_adapter_name_changes_report_hash(self) -> None:
        fixture = Path("experiments/validation/boundary_reporting/fixtures/matrix_cases/slice_a.jsonl")
        raw_cases = load_cases_from_jsonl(fixture)
        cases = resolve_adapter("fixture")(raw_cases, "boundary-v1")
        decisions = evaluate_cases(cases)

        with tempfile.TemporaryDirectory() as tmpdir:
            base_dir = Path(tmpdir) / "base"
            alt_dir = Path(tmpdir) / "alt"

            base_metadata = BoundaryReportMetadata(
                version="boundary-report-v0",
                contract_version="boundary-v1",
                schema_version="1.0",
                evaluator_version="0.1",
                adapter_name="fixture",
                runtime_contract="boundary-v1",
                seed=42,
                generated_at="2026-07-19T00:00:00Z",
            )
            alt_metadata = BoundaryReportMetadata(
                version="boundary-report-v0",
                contract_version="boundary-v1",
                schema_version="1.0",
                evaluator_version="0.1",
                adapter_name="fixture-alt",
                runtime_contract="boundary-v1",
                seed=42,
                generated_at="2026-07-19T00:00:00Z",
            )

            base = generate_report(cases, decisions, base_dir, base_metadata, replay_consistency=1.0)
            alt = generate_report(cases, decisions, alt_dir, alt_metadata, replay_consistency=1.0)

            self.assertNotEqual(base["report_hash"], alt["report_hash"])
            self.assertNotEqual(
                json.loads((base_dir / "metadata.json").read_text(encoding="utf-8"))["report_hash"],
                json.loads((alt_dir / "metadata.json").read_text(encoding="utf-8"))["report_hash"],
            )


if __name__ == "__main__":
    unittest.main()
