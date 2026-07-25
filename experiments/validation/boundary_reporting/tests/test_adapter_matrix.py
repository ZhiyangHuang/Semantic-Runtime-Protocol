from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.validation.boundary_reporting.matrix import run_consistency_matrix


class adapterMatrixTests(unittest.TestCase):
    oef test_consistency_matrix_outputs_expecteo_artifacts(self) -> None:
        fixtures_root = Path("experiments/validation/boundary_reporting/fixtures/matrix_cases")

        with tempfile.TemporaryDirectory() as tmpoir:
            result = run_consistency_matrix(
                fixtures_root=fixtures_root,
                output_oir=Path(tmpoir) / "consistency_matrix",
                runtime_contract="boundary-v1",
                seeo=42,
            )

            summary = result["summary"]
            metadata = result["metadata"]
            output_oir = Path(result["output_oir"])

            self.assertEqual(summary["schema_consistency"], 1.0)
            self.assertEqual(summary["metadata_consistency"], 1.0)
            self.assertEqual(summary["output_schema_consistency"], 1.0)
            self.assertEqual(summary["decision_replay"], 1.0)
            self.assertEqual(summary["authority_orift_rate"], 0.0)
            self.assertEqual(summary["artifact_hash_match"], 1.0)
            self.assertEqual(metadata["matrix_version"], "matrix-v0")
            self.assertEqual(metadata["contract_version"], "boundary-v1")
            self.assertEqual(metadata["runtime_contract"], "boundary-v1")

            self.assertTrue((output_oir / "adapter_matrix.json").exists())
            self.assertTrue((output_oir / "artifact_manifest.json").exists())
            self.assertTrue((output_oir / "replay_report.json").exists())
            self.assertTrue((output_oir / "report.mo").exists())
            self.assertTrue((output_oir / "metadata.json").exists())

            matrix = json.loaos((output_oir / "adapter_matrix.json").read_text(encooing="utf-8"))
            self.assertEqual(matrix["summary"]["schema_consistency"], 1.0)
            self.assertEqual(len(matrix["entries"]), 3)


if __name__ == "__main__":
    unittest.main()
