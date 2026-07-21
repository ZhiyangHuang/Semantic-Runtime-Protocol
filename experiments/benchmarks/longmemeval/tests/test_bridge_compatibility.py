from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.benchmarks.longmemeval.adapter import LongMemEvalBridgeAdapter
from experiments.benchmarks.longmemeval.config import LongMemEvalBridgeConfig
from experiments.benchmarks.longmemeval.runner import LongMemEvalBridgeRunner
from experiments.external_validation.runtime_contract import ExternalValidationRuntimeContract


class LongMemEvalBridgeCompatibilityTests(unittest.TestCase):
    def test_official_scorer_and_runtime_contract_ownership_remain_external_validation(self) -> None:
        adapter = LongMemEvalBridgeAdapter()
        external_case = adapter.load_dataset(sample_limit=1)[0]
        bridge_case = adapter.normalize_case(external_case)
        metadata = bridge_case.metadata

        self.assertEqual(metadata["bridge"]["official_scorer"], "external_validation")
        self.assertEqual(metadata["bridge"]["runtime_contract"], "external_validation_runtime_contract_v1")
        self.assertEqual(metadata["bridge"]["payload_policy"], "not_stored_in_repository")
        self.assertEqual(metadata["adapter_registration"]["benchmark_scoring"], False)

        runtime_contract = ExternalValidationRuntimeContract()
        self.assertEqual(runtime_contract.provider, "local_vllm")
        self.assertEqual(runtime_contract.backend, "vllm")
        self.assertEqual(runtime_contract.prompt_template_id, "longmemeval_shared_generation_prompt_v1")

    def test_external_source_registration_is_metadata_only(self) -> None:
        manifest_path = Path("data/external/longmemeval/manifest.json")
        provenance_path = Path("data/external/longmemeval/provenance.md")
        adapter_config_path = Path("data/external/longmemeval/adapter_config.json")

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        adapter_config = json.loads(adapter_config_path.read_text(encoding="utf-8"))
        provenance = provenance_path.read_text(encoding="utf-8")

        self.assertEqual(manifest["payload"], "not stored in repository")
        self.assertIn("does not store the benchmark payload", provenance)
        self.assertEqual(adapter_config["benchmark_scoring"], False)
        self.assertEqual(adapter_config["output_role"], "governance_boundary_case")

    def test_bridge_runner_uses_shared_artifact_contract_without_new_scorer(self) -> None:
        config = LongMemEvalBridgeConfig(
            bridge_name="longmemeval",
            bridge_version="bridge_migration_v1",
            bridge_output_dir="experiments/results/longmemeval_full_v1",
            source_path="tests/bridge.env",
        )
        runner = LongMemEvalBridgeRunner(config=config)
        self.assertFalse(hasattr(runner, "compute_score"))
        self.assertFalse(hasattr(runner, "score"))
        self.assertEqual(runner.config.bridge_name, "longmemeval")
        self.assertEqual(runner.config.bridge_output_dir, "experiments/results/longmemeval_full_v1")


if __name__ == "__main__":
    unittest.main()

