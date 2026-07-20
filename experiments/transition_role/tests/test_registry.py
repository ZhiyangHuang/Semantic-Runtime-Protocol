from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from experiments.transition_role.validate_registry import (
    validate_adapter_capabilities,
    validate_all,
    validate_external_registry_consistency,
    validate_transition_role_registry,
)


class TransitionRoleRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.roles_path = Path("experiments/transition_role/registry.yaml")
        self.external_path = Path("data/external/registry.json")

    def test_transition_role_registry_is_valid(self) -> None:
        report = validate_transition_role_registry(self.roles_path)
        self.assertTrue(report.valid)
        self.assertEqual(report.details["role_ids"], [
            "evidence_update",
            "temporal_state_evolution",
            "action_proposal",
            "inference_proposal",
        ])
        self.assertTrue(any("inference_proposal" in warning for warning in report.warnings))

    def test_external_registry_consistency_is_valid(self) -> None:
        report = validate_external_registry_consistency(self.external_path, self.roles_path)
        self.assertTrue(report.valid, msg=report.errors)
        self.assertEqual(report.details["source_names"], ["longmemeval", "locomo", "agentbench", "reasoning"])

    def test_adapter_capabilities_match_registry(self) -> None:
        report = validate_adapter_capabilities(self.external_path, self.roles_path)
        self.assertTrue(report.valid, msg=report.errors)

    def test_unknown_transition_role_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_external = Path(tmpdir) / "registry.json"
            payload = json.loads(self.external_path.read_text(encoding="utf-8"))
            payload["sources"][0]["transition_role"] = "unknown_role"
            temp_external.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            report = validate_external_registry_consistency(temp_external, self.roles_path)
            self.assertFalse(report.valid)
            self.assertTrue(any("unknown transition roles" in error for error in report.errors))

    def test_validate_all_passes(self) -> None:
        report = validate_all(self.roles_path, self.external_path)
        self.assertTrue(report.valid, msg=report.errors)


if __name__ == "__main__":
    unittest.main()
