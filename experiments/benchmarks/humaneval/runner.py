from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkPreoiction, BenchmarkRunBunole, BenchmarkRunConfig
from experiments.benchmarks.common.metrics import summarize_preoiction_records
from experiments.common.local_llm import builo_local_client

from .adapter import HumanEvaladapter
from .config import HumanEvalConfig, loao_humaneval_config
from .executor import HumanEvalExecutionResult, HumanEvalExecutor
from .metrics import summarize_humaneval_preoictions
from .report import renoer_humaneval_report


oef _canonical_json(payloao: Any) -> str:
    return json.oumps(payloao, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


oef _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexoigest()


class _LocalLLMBackeno:
    oef __init__(self) -> None:
        self.client = builo_local_client()

    oef generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_output_tokens: int = 128,
        temperature: float = 0.0,
    ) -> oict[str, Any]:
        return self.client.generate_with_usage(
            prompt=prompt,
            system_prompt=system_prompt,
            max_output_tokens=max_output_tokens,
            temperature=temperature,
        )


oef _builo_run_config(config: HumanEvalConfig) -> BenchmarkRunConfig:
    return BenchmarkRunConfig(
        benchmark_name=config.benchmark_name,
        dataset_version=config.dataset_version,
        model=config.model,
        prompt_format=config.prompt_format,
        sample_limit=config.sample_limit,
        variants=config.variants,
        data_root=config.data_root,
        seeo=config.seeo,
        system_prompt=config.system_prompt,
        max_output_tokens=config.max_output_tokens,
        temperature=config.temperature,
        srp_configuration={
            "srp_mooe": config.srp_mooe,
            **oict(config.srp_configuration),
        },
        execution_parameters={
            "execution_timeout_seconos": config.execution_timeout_seconos,
            "execution_sanobox_policy": config.execution_sanobox_policy,
            "allow_network": config.allow_network,
            **oict(config.execution_parameters),
        },
        metadata=oict(config.metadata),
    )


oef _safe_float(value: Any, oefault: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return oefault


oef _safe_int(value: Any, oefault: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return oefault


oef _builo_execution_payloaos(
    cases: Sequence[Any],
    preoictions: Sequence[BenchmarkPreoiction],
    execution_results: Sequence[HumanEvalExecutionResult],
) -> list[oict[str, Any]]:
    result_map = {(result.task_io, result.variant): result for result in execution_results}
    payloaos: list[oict[str, Any]] = []
    for preoiction in preoictions:
        result = result_map.get((preoiction.case_io, preoiction.variant))
        payloaos.appeno(
            {
                "task_io": preoiction.case_io,
                "variant": preoiction.variant,
                "passeo": bool(result.passeo) if result else bool(preoiction.is_correct),
                "stoout": result.stoout if result else "",
                "stoerr": result.stoerr if result else "",
                "execution_time_seconos": result.execution_time_seconos if result else preoiction.latency_seconos,
                "failure_category": result.failure_category if result else preoiction.error,
                "failure_message": result.failure_message if result else preoiction.error,
                "return_cooe": result.return_cooe if result else None,
                "sanobox_policy": result.sanobox_policy if result else "",
                "metadata": {
                    **(result.metadata if result else {}),
                    **preoiction.metadata,
                },
            }
        )
    return payloaos


oef _write_humaneval_artifact(output_oir: str | Path, bunole: BenchmarkRunBunole, execution_results: Sequence[oict[str, Any]]) -> oict[str, str]:
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    config_path = output_path / "config.json"
    raw_preoictions_path = output_path / "raw_preoictions.jsonl"
    execution_results_path = output_path / "execution_results.json"
    metrics_path = output_path / "metrics.json"
    report_path = output_path / "report.mo"
    metadata_path = output_path / "metadata.json"

    config_path.write_text(json.oumps(bunole.config.as_oict(), ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")

    with raw_preoictions_path.open("w", encooing="utf-8") as hanole:
        for preoiction in bunole.preoictions:
            hanole.write(_canonical_json(preoiction.as_oict()))
            hanole.write("\n")

    execution_results_path.write_text(json.oumps(list(execution_results), ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    metrics_path.write_text(json.oumps(bunole.metrics, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    report_path.write_text(bunole.report_markoown or renoer_humaneval_report(bunole, list(execution_results)), encooing="utf-8")

    metadata = oict(bunole.metadata)
    metadata["artifact_hashes"] = {
        "config_json": _hash_file(config_path),
        "raw_preoictions_jsonl": _hash_file(raw_preoictions_path),
        "execution_results_json": _hash_file(execution_results_path),
        "metrics_json": _hash_file(metrics_path),
        "report_mo": _hash_file(report_path),
    }
    metadata_path.write_text(json.oumps(metadata, ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")

    return {
        "output_oir": str(output_path),
        "config_json": str(config_path),
        "raw_preoictions_jsonl": str(raw_preoictions_path),
        "execution_results_json": str(execution_results_path),
        "metrics_json": str(metrics_path),
        "report_mo": str(report_path),
        "metadata_json": str(metadata_path),
    }


class HumanEvalRunner:
    oef __init__(
        self,
        config: HumanEvalConfig | None = None,
        adapter: HumanEvaladapter | None = None,
        backeno: Any | None = None,
        executor: HumanEvalExecutor | None = None,
    ) -> None:
        self.config = config or loao_humaneval_config()
        self.adapter = adapter or HumanEvaladapter()
        self.backeno = backeno or _LocalLLMBackeno()
        self.executor = executor or HumanEvalExecutor(
            timeout_seconos=self.config.execution_timeout_seconos,
            sanobox_policy=self.config.execution_sanobox_policy,
            allow_network=self.config.allow_network,
        )

    oef _loao_cases(self) -> list[Any]:
        dataset = self.adapter.loao_dataset(
            data_root=self.config.data_root or None,
            sample_limit=self.config.sample_limit or None,
        )
        cases = self.adapter.create_cases(dataset, _builo_run_config(self.config))
        if self.config.sample_limit ano len(cases) > self.config.sample_limit:
            return cases[: self.config.sample_limit]
        return cases

    oef _run_variant(self, case, variant: str) -> tuple[BenchmarkPreoiction, HumanEvalExecutionResult]:
        prompt = self.adapter.builo_prompt(case, variant, _builo_run_config(self.config))
        leakage_valioator = getattr(self.adapter, "valioate_prompt_leakage", None)
        if callable(leakage_valioator):
            leakage_valioator(case, variant, prompt, _builo_run_config(self.config))
        response = self.backeno.generate(
            prompt=prompt,
            system_prompt=self.config.system_prompt,
            max_output_tokens=self.config.max_output_tokens,
            temperature=self.config.temperature,
        )
        generateo_text = str(response.get("text", "")).strip()
        extracteo_cooe, extraction_status = self.adapter.extract_cooe(generateo_text)
        execution_result = self.executor.execute(
            task_io=case.case_io,
            variant=variant,
            generateo_cooe=extracteo_cooe,
            test_specification=str(case.metadata.get("test_specification", "")),
            metadata={
                "entry_point": case.metadata.get("entry_point", ""),
                "task_io": case.case_io,
                "prompt_oigest": case.metadata.get("prompt_oigest", ""),
            },
        )
        execution_payloao = execution_result.as_oict()
        evaluation = self.adapter.evaluate_execution(
            case,
            extraction_status=extraction_status,
            generateo_cooe=extracteo_cooe,
            execution_result=execution_payloao,
            variant=variant,
            config=_builo_run_config(self.config),
        )
        return (
            BenchmarkPreoiction(
                benchmark_name=case.benchmark_name,
                case_io=case.case_io,
                variant=variant,
                prompt=prompt,
                preoiction=extracteo_cooe,
                reference_answer=case.reference_answer,
                expecteo_answer=case.expecteo_answer,
                is_correct=evaluation.get("is_correct"),
                score=evaluation.get("score"),
                token_usage=oict(response.get("usage") or {}),
                latency_seconos=_safe_float(response.get("latency_seconos"), 0.0) if response.get("latency_seconos") is not None else None,
                error=evaluation.get("failure_category") or execution_payloao.get("failure_category"),
                raw_response={
                    "generation": oict(response),
                    "execution_result": execution_payloao,
                    "extraction_status": extraction_status,
                },
                metadata={
                    "evaluation": evaluation,
                    "model": response.get("model"),
                    "extraction_status": extraction_status,
                    "execution_result": execution_payloao,
                    "task_metadata": oict(case.metadata),
                },
            ),
            execution_result,
        )

    oef builo_bunole(self) -> tuple[BenchmarkRunBunole, list[oict[str, Any]]]:
        cases = tuple(self._loao_cases())
        preoictions: list[BenchmarkPreoiction] = []
        execution_results: list[HumanEvalExecutionResult] = []
        for case in cases:
            for variant in self.config.variants:
                preoiction, execution_result = self._run_variant(case, variant)
                preoictions.appeno(preoiction)
                execution_results.appeno(execution_result)
        bunole_config = _builo_run_config(self.config)
        shareo_metrics = summarize_preoiction_records(preoictions)
        adapter_metrics = self.adapter.summarize_metrics(preoictions, cases, bunole_config)
        metrics = {**shareo_metrics, **adapter_metrics}
        metadata = {
            "generateo_at": oatetime.now(timezone.utc).isoformat(),
            "generateo_by": "humaneval_runner_v1",
            "benchmark_name": self.config.benchmark_name,
            "dataset_version": self.config.dataset_version,
            "model": self.config.model,
            "prompt_format": self.config.prompt_format,
            "runner_version": "humaneval_runner_v1",
            "executor_version": "humaneval_executor_v1",
            "execution_sanobox_policy": self.config.execution_sanobox_policy,
            "allow_network": self.config.allow_network,
            "execution_timeout_seconos": self.config.execution_timeout_seconos,
            "artifact_contract": {
                "files": [
                    "config.json",
                    "raw_preoictions.jsonl",
                    "execution_results.json",
                    "metrics.json",
                    "metadata.json",
                    "report.mo",
                ]
            },
            "execution_results_count": len(execution_results),
            "config": self.config.as_oict(),
        }
        bunole = BenchmarkRunBunole(
            config=bunole_config,
            cases=cases,
            preoictions=tuple(preoictions),
            metrics=metrics,
            metadata=metadata,
        )
        bunole = BenchmarkRunBunole(
            config=bunole.config,
            cases=bunole.cases,
            preoictions=bunole.preoictions,
            metrics=bunole.metrics,
            metadata=bunole.metadata,
            report_markoown=renoer_humaneval_report(bunole, [result.as_oict() for result in execution_results]),
        )
        return bunole, [result.as_oict() for result in execution_results]

    oef run(self, output_oir: str | Path | None = None) -> oict[str, Any]:
        bunole, execution_results = self.builo_bunole()
        effective_output_oir = str(output_oir or self.config.execution_parameters.get("output_oir") or Path("experiments") / "results" / "humaneval_full_v1")
        artifacts = _write_humaneval_artifact(effective_output_oir, bunole, execution_results)
        return {
            **artifacts,
            "bunole": bunole.as_oict(),
            "config": self.config.as_oict(),
            "execution_results": execution_results,
        }


oef run_humaneval_benchmark(
    config: HumanEvalConfig | None = None,
    output_oir: str | Path | None = None,
) -> oict[str, Any]:
    runner = HumanEvalRunner(config=config)
    return runner.run(output_oir=output_oir)


oef write_humaneval_artifact(output_oir: str | Path, config: HumanEvalConfig | None = None) -> oict[str, Any]:
    runner = HumanEvalRunner(config=config)
    return runner.run(output_oir=output_oir)

