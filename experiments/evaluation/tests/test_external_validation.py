from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.config import (
    ExternalValidationConfig,
    load_external_validation_longmemeval_adapter_validation_config,
    load_external_validation_longmemeval_evidence_config,
)
from experiments.external_validation.calibration_report import write_locomo_calibration_aware_outputs_from_source_dir
from experiments.external_validation.benchmarks import LoCoMoAdapter
from experiments.external_validation.runtime_contract import ExternalValidationRuntimeContract, build_runtime_manifest
from experiments.external_validation.runner import build_external_validation_runs, run_external_validation, write_external_validation_outputs


class ExternalValidationTests(unittest.TestCase):
    def test_locomo_adapter_real_json(self) -> None:
        adapter = LoCoMoAdapter()
        cases = adapter.load_cases(Path("data/locomo"), sample_limit=1)
        self.assertGreater(len(cases), 0)
        self.assertTrue(cases[0].case_id.startswith("conv-"))
        self.assertEqual(cases[0].benchmark_name, "locomo")

    def test_build_runs(self) -> None:
        adapter = LoCoMoAdapter()
        config = ExternalValidationConfig(
            benchmark_names=("locomo",),
            baseline_names=("full_context", "vector_rag", "srp"),
            seeds=(11, 23),
            data_root="data/locomo",
            benchmark_sample_limit=1,
        )
        runs = build_external_validation_runs(config)
        self.assertEqual(len(runs), len(adapter.load_cases(Path("data/locomo"), sample_limit=1)) * 2 * 3)
        self.assertEqual(runs[0].baseline_name, "full_context")

    def test_run_roundtrip(self) -> None:
        config = ExternalValidationConfig(
            benchmark_names=("locomo",),
            baseline_names=("full_context", "vector_rag", "srp"),
            seeds=(11,),
            data_root="data/locomo",
            benchmark_sample_limit=1,
        )
        outputs = run_external_validation(config)
        self.assertGreater(outputs["report"]["summary"]["case_count"], 0)
        self.assertIn("pairwise_summary", outputs["report"])

    def test_write_outputs(self) -> None:
        config = ExternalValidationConfig(
            benchmark_names=("locomo",),
            baseline_names=("full_context", "vector_rag", "srp"),
            seeds=(11,),
            data_root="data/locomo",
            benchmark_sample_limit=1,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_external_validation_outputs(Path(tmpdir), config=config, write_root_report=False)
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())

    def test_write_calibration_aware_outputs_from_source_dir(self) -> None:
        source_dir = Path("experiments/results/external_validation_locomo_mvp")
        self.assertTrue((source_dir / "external_validation_records.csv").exists())
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_locomo_calibration_aware_outputs_from_source_dir(
                source_dir,
                Path(tmpdir),
                config={
                    "benchmark_names": ["locomo"],
                    "baseline_names": ["full_context", "sliding_window", "vector_rag", "srp"],
                    "seeds": [11, 23, 37],
                    "data_root": "data/locomo",
                    "source_output_dir": str(source_dir),
                    "output_dir": tmpdir,
                },
            )
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["report_json"]).exists())
            self.assertTrue(Path(outputs["summary_json"]).exists())
            self.assertIn("LoCoMo Calibration-Aware External Validation Report", Path(outputs["report_markdown"]).read_text(encoding="utf-8"))

    def test_write_calibration_aware_outputs_script_contract(self) -> None:
        from experiments.config import load_external_validation_calibration_aware_config

        config = load_external_validation_calibration_aware_config(Path("configs/external_validation_locomo_mvp_calibration_aware.env"))
        self.assertEqual(config.benchmark_names, ("locomo",))
        self.assertEqual(config.baseline_names, ("full_context", "sliding_window", "vector_rag", "srp"))
        self.assertEqual(config.seeds, (11, 23, 37))

    def test_longmemeval_adapter_validation_config(self) -> None:
        config = load_external_validation_longmemeval_adapter_validation_config(
            Path("configs/external_validation_longmemeval_adapter_validation.env")
        )
        self.assertEqual(config.benchmark_name, "longmemeval")
        self.assertEqual(config.baseline_names, ("full_context", "sliding_window", "vector_rag", "srp"))
        self.assertEqual(config.seeds, (11, 23, 37))

    def test_longmemeval_evidence_config_and_runtime_manifest(self) -> None:
        config = load_external_validation_longmemeval_evidence_config(
            Path("configs/external_validation_longmemeval_evidence.env")
        )
        self.assertEqual(config.benchmark_name, "longmemeval")
        self.assertEqual(config.model_endpoint, "http://172.25.253.78:8000")
        self.assertEqual(config.model_name, "Qwen/Qwen3-4B-AWQ")
        self.assertEqual(config.model_tokenizer, "Qwen/Qwen3-4B-AWQ")
        self.assertEqual(config.prompt_template_id, "longmemeval_shared_generation_prompt_v1")
        manifest = build_runtime_manifest(
            benchmark_name=config.benchmark_name,
            baselines=config.baseline_names,
            seeds=config.seeds,
            runtime_contract=ExternalValidationRuntimeContract(
                provider=config.model_provider,
                backend=config.model_backend,
                endpoint=config.model_endpoint,
                model=config.model_name,
                tokenizer=config.model_tokenizer,
                prompt_template_id=config.prompt_template_id,
                temperature=config.temperature,
                max_output_tokens=config.max_output_tokens,
                same_endpoint_across_baselines=config.same_endpoint_across_baselines,
            ),
            source_config_path=config.source_path,
            phase=config.phase,
            data_root=config.data_root,
            sample_limit=config.benchmark_sample_limit,
        )
        self.assertEqual(manifest["model_environment"]["endpoint"], "http://172.25.253.78:8000")
        self.assertEqual(manifest["model_environment"]["tokenizer"], "Qwen/Qwen3-4B-AWQ")
        self.assertEqual(manifest["model_environment"]["prompt_template_id"], "longmemeval_shared_generation_prompt_v1")
        self.assertTrue(manifest["runtime_policy"]["same_endpoint_across_baselines"])


if __name__ == "__main__":
    unittest.main()
