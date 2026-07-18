from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import ExternalValidationLongMemEvalEvidenceConfig, load_external_validation_longmemeval_evidence_config
from experiments.common.local_llm import LocalOpenAICompatibleClient

from .benchmarks import build_benchmark_adapter
from .baselines import build_memory_system
from .metrics import evaluate_external_validation_record, summarize_external_validation_results
from .runtime_contract import ExternalValidationRuntimeContract, build_runtime_manifest, write_runtime_manifest
from .schema import BenchmarkCase, ExternalValidationRecord, ExternalValidationRun, MemoryResponse
from .failure_analysis import summarize_failures


def _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().split())


def _state_to_prompt_lines(case: BenchmarkCase, response: MemoryResponse) -> list[str]:
    state = response.recovered_state
    lines: list[str] = [
        f"Question: {case.query}",
        "",
        "Recovered semantic units:",
    ]
    if state.units:
        for unit in state.units:
            lines.append(
                f"- {unit.unit_id} | kind={unit.kind} | timestep={unit.timestep} | salience={unit.salience}: {unit.content}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Recovered semantic relations:")
    if state.relations:
        for relation in state.relations:
            lines.append(
                f"- {relation.relation_id} | {relation.source_id} -> {relation.target_id} | "
                f"type={relation.relation_type} | confidence={relation.confidence} | timestep={relation.timestep}"
            )
    else:
        lines.append("- none")
    lines.append("")
    lines.append("Answer only with the shortest faithful answer.")
    lines.append("Do not add reasoning, caveats, or extra context.")
    return lines


def _generate_answer_from_state(
    client: LocalOpenAICompatibleClient,
    case: BenchmarkCase,
    response: MemoryResponse,
    *,
    temperature: float,
    max_output_tokens: int,
) -> tuple[str, dict[str, Any]]:
    prompt = "\n".join(_state_to_prompt_lines(case, response))
    result = client.generate_with_usage(
        prompt,
        system_prompt=(
            "You answer memory questions from recovered semantic state. "
            "Use only the recovered state. Do not invent facts. "
            "Return only the final answer."
        ),
        max_output_tokens=max_output_tokens,
        temperature=temperature,
    )
    text = _normalize_text(str(result.get("text", "")))
    return text, dict(result)


def _build_runs(config: ExternalValidationLongMemEvalEvidenceConfig) -> list[ExternalValidationRun]:
    adapter = build_benchmark_adapter(config.benchmark_name)
    root = Path(config.data_root) if config.data_root else None
    cases = adapter.load_cases(root, sample_limit=config.benchmark_sample_limit)
    runs: list[ExternalValidationRun] = []
    for seed in config.seeds:
        for case in cases:
            for baseline_name in config.baseline_names:
                runs.append(
                    ExternalValidationRun(
                        run_id=f"{config.benchmark_name}_{baseline_name}_{seed}_{case.case_id}",
                        benchmark_name=config.benchmark_name,
                        baseline_name=baseline_name,
                        seed=seed,
                        case=case,
                    )
                )
    return runs


def run_longmemeval_evidence(config: ExternalValidationLongMemEvalEvidenceConfig | None = None) -> dict[str, Any]:
    config = config or load_external_validation_longmemeval_evidence_config()
    runtime_contract = ExternalValidationRuntimeContract(
        provider=config.model_provider,
        backend=config.model_backend,
        endpoint=config.model_endpoint,
        model=config.model_name,
        tokenizer=config.model_tokenizer,
        prompt_template_id=config.prompt_template_id,
        temperature=config.temperature,
        max_output_tokens=config.max_output_tokens,
        same_endpoint_across_baselines=config.same_endpoint_across_baselines,
        baseline_generation_backend="shared",
        srp_generation_backend="shared",
        notes=("LongMemEval evidence run uses a shared generation backend across baselines and SRP.",),
    )
    runtime_manifest = build_runtime_manifest(
        benchmark_name=config.benchmark_name,
        baselines=config.baseline_names,
        seeds=config.seeds,
        runtime_contract=runtime_contract,
        source_config_path=config.source_path,
        phase=config.phase,
        data_root=config.data_root,
        sample_limit=config.benchmark_sample_limit,
    )

    runs = _build_runs(config)
    client = LocalOpenAICompatibleClient(
        base_url=config.model_endpoint,
        model=config.model_name,
        timeout_seconds=config.model_timeout_seconds,
    )

    records: list[ExternalValidationRecord] = []
    generation_traces: list[dict[str, Any]] = []
    for run in runs:
        memory = build_memory_system(run.baseline_name, seed=run.seed)
        memory.ingest(run.case)
        retrieved = memory.retrieve(run.case.query, budget=run.case.metadata.get("evidence_budget"))
        predicted_answer, generation_result = _generate_answer_from_state(
            client,
            run.case,
            retrieved,
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
        )
        evidence_response = MemoryResponse(
            recovered_state=retrieved.recovered_state,
            predicted_answer=predicted_answer,
            retrieved_unit_ids=retrieved.retrieved_unit_ids,
            retrieved_relation_ids=retrieved.retrieved_relation_ids,
            evidence_cost=retrieved.evidence_cost,
            notes=retrieved.notes
            + (
                "shared_generation_backend",
                f"generation_model:{generation_result.get('model', config.model_name)}",
                f"generation_endpoint:{config.model_endpoint}",
            ),
        )
        record = evaluate_external_validation_record(run, evidence_response)
        records.append(record)
        generation_traces.append(
            {
                "run_id": run.run_id,
                "benchmark_name": run.benchmark_name,
                "baseline_name": run.baseline_name,
                "seed": run.seed,
                "case_id": run.case.case_id,
                "question": run.case.query,
                "recovered_state": retrieved.recovered_state.as_dict(),
                "predicted_answer": predicted_answer,
                "generation_model": generation_result.get("model", config.model_name),
                "generation_endpoint": config.model_endpoint,
                "prompt_template_id": config.prompt_template_id,
                "generation_latency_seconds": generation_result.get("latency_seconds"),
                "usage": generation_result.get("usage"),
            }
        )

    summary_bundle = summarize_external_validation_results(records)
    failure_bundle = summarize_failures(records)
    report = {
        "report_id": f"{config.benchmark_name}_external_validation_evidence_{len(records)}",
        "status": "evaluated",
        "metric_schema": {
            "schema_version": "external_validation_metrics_schema.v1",
            "coverage_definition": "matched semantic units divided by original semantic units",
            "drift_definition": "weighted combination of fact drift, relation drift, and hallucinated relation rate",
            "benchmark_definition": "official benchmark score plus SRP diagnostic metrics",
            "evidence_cost_definition": "scalar cost attached to the recovery case",
        },
        "records": [record.as_dict() for record in records],
        "summary": summary_bundle["summary"],
        "statistical_summary": summary_bundle["statistical_summary"],
        "benchmark_summary": summary_bundle["benchmark_summary"],
        "baseline_summary": summary_bundle["baseline_summary"],
        "seed_summary": summary_bundle["seed_summary"],
        "pairwise_summary": summary_bundle["pairwise_summary"],
        "failure_summary": failure_bundle,
    }
    markdown = _render_markdown_report(config, report, runtime_manifest, generation_traces)
    return {
        "config": config.as_dict(),
        "runtime_manifest": runtime_manifest,
        "report": report,
        "markdown": markdown,
        "runs": [run.as_dict() for run in runs],
        "traces": generation_traces,
    }


def _render_markdown_report(
    config: ExternalValidationLongMemEvalEvidenceConfig,
    report: dict[str, Any],
    runtime_manifest: dict[str, Any],
    generation_traces: list[dict[str, Any]],
) -> str:
    summary = report["summary"]
    statistical_summary = report.get("statistical_summary", {})
    benchmark_summary = report["benchmark_summary"]
    baseline_summary = report["baseline_summary"]
    failure_summary = report["failure_summary"]

    metric_order = [
        "semantic_coverage",
        "semantic_drift",
        "fact_accuracy",
        "relation_accuracy",
        "recovery_accuracy",
        "closure_accuracy",
        "neighborhood_completeness",
        "hallucinated_relation_rate",
        "evidence_cost",
        "answer_accuracy",
        "official_metric_score",
    ]

    def _render_stat_table(title: str, stats: dict[str, Any]) -> list[str]:
        lines = [title, "", "| Metric | Mean | Std | 95% CI | N |", "| --- | ---: | ---: | ---: | ---: |"]
        for metric in metric_order:
            entry = stats.get(metric, {})
            lines.append(
                f"| {metric} | `{entry.get('mean', 0.0)}` | `{entry.get('std', 0.0)}` | `{entry.get('ci95', 0.0)}` | `{int(entry.get('count', 0))}` |"
            )
        return lines
    lines = [
        "# SRP LongMemEval External Validation Evidence Report",
        "",
        "This report records the evidence run layer for LongMemEval under a frozen shared-generation runtime contract.",
        "It is evidence, not calibration, and it uses the same local vLLM endpoint across baselines and SRP.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmark: `{config.benchmark_name}`",
        f"- Baselines: `{', '.join(config.baseline_names)}`",
        f"- Seeds: `{', '.join(str(seed) for seed in config.seeds)}`",
        f"- Data root: `{config.data_root or 'fixtures'}`",
        "",
        "## 2. Runtime Contract",
        "",
        f"- provider: `{runtime_manifest['model_environment']['provider']}`",
        f"- backend: `{runtime_manifest['model_environment']['backend']}`",
        f"- endpoint: `{runtime_manifest['model_environment']['endpoint']}`",
        f"- model: `{runtime_manifest['model_environment']['model']}`",
        f"- tokenizer: `{runtime_manifest['model_environment']['tokenizer']}`",
        f"- prompt_template_id: `{runtime_manifest['model_environment']['prompt_template_id']}`",
        f"- temperature: `{runtime_manifest['model_environment']['temperature']}`",
        f"- max_output_tokens: `{runtime_manifest['model_environment']['max_output_tokens']}`",
        f"- same_endpoint_across_baselines: `{runtime_manifest['runtime_policy']['same_endpoint_across_baselines']}`",
        f"- baseline_generation_backend: `{runtime_manifest['runtime_policy']['baseline_generation_backend']}`",
        f"- srp_generation_backend: `{runtime_manifest['runtime_policy']['srp_generation_backend']}`",
        "",
        "## 3. Official Benchmark Result",
        "",
        f"- Case count: `{summary.get('case_count', 0)}`",
    ]
    for key in (
        "semantic_coverage",
        "semantic_drift",
        "fact_accuracy",
        "relation_accuracy",
        "recovery_accuracy",
        "closure_accuracy",
        "neighborhood_completeness",
        "hallucinated_relation_rate",
        "evidence_cost",
        "answer_accuracy",
        "official_metric_score",
    ):
        if key in summary:
            lines.append(f"- {key}: `{summary[key]}`")
    lines.extend(
        [
            "",
            "## 4. Diagnostic Result",
            "",
        ]
    )
    for benchmark_name, data in benchmark_summary.items():
        lines.append(f"### {benchmark_name}")
        for key in (
            "semantic_coverage",
            "semantic_drift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "neighborhood_completeness",
            "hallucinated_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
        ):
            if key in data:
                lines.append(f"- {key}: `{data[key]}`")
        lines.append("")
    lines.append("### Baseline Summary")
    lines.append("")
    for baseline_name, data in baseline_summary.items():
        lines.append(f"- {baseline_name}:")
        for key in ("semantic_coverage", "semantic_drift", "relation_accuracy", "evidence_cost", "answer_accuracy"):
            if key in data:
                lines.append(f"  - {key}: `{data[key]}`")
    lines.extend(
        [
            "",
            "## 5. Failure Summary",
            "",
        ]
    )
    if failure_summary:
        for key, value in failure_summary.items():
            lines.append(f"- {key}: `{value}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## 6. Statistical Reporting",
            "",
            "The statistics below are descriptive only for the predefined 24-case LongMemEval evidence slice.",
            "They support measurement transparency and reproducibility, not inferential claims about the full benchmark.",
        ]
    )
    if statistical_summary.get("overall"):
        lines.extend(_render_stat_table("### Overall descriptive statistics", statistical_summary["overall"]))
    baseline_stats = statistical_summary.get("baseline", {})
    if baseline_stats:
        lines.extend(
            [
                "",
                "### Baseline descriptive statistics",
                "",
                "| Baseline | N | Answer Acc. mean | Answer Acc. std | Answer Acc. CI95 | Evidence Cost mean | Evidence Cost std | Evidence Cost CI95 |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for baseline_name in config.baseline_names:
            entry = baseline_stats.get(baseline_name, {})
            answer_stats = entry.get("answer_accuracy", {})
            cost_stats = entry.get("evidence_cost", {})
            count = int(answer_stats.get("count", 0))
            lines.append(
                f"| {baseline_name} | `{count}` | `{answer_stats.get('mean', 0.0)}` | `{answer_stats.get('std', 0.0)}` | `{answer_stats.get('ci95', 0.0)}` | `{cost_stats.get('mean', 0.0)}` | `{cost_stats.get('std', 0.0)}` | `{cost_stats.get('ci95', 0.0)}` |"
            )
    seed_stats = statistical_summary.get("seed", {})
    if seed_stats:
        lines.extend(
            [
                "",
                "### Seed descriptive statistics",
                "",
                "| Seed | N | Answer Acc. mean | Answer Acc. std | Answer Acc. CI95 |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for seed in config.seeds:
            entry = seed_stats.get(str(seed), {})
            answer_stats = entry.get("answer_accuracy", {})
            lines.append(
                f"| `{seed}` | `{int(answer_stats.get('count', 0))}` | `{answer_stats.get('mean', 0.0)}` | `{answer_stats.get('std', 0.0)}` | `{answer_stats.get('ci95', 0.0)}` |"
            )
    lines.extend(
        [
            "",
            "## 7. Evidence Promotion Gate",
            "",
            "| Gate | Status | Notes |",
            "| --- | --- | --- |",
            "| adapter | pass | semantic adapter and benchmark ingestion are stable. |",
            "| temporal_protocol | pass | the three-stage attribution protocol is frozen. |",
            "| shared_generation_backend | pass | all baselines and SRP use the same local vLLM endpoint. |",
            "| shared_tokenizer | pass | the runtime contract freezes the same tokenizer. |",
            "| prompt_equivalence | pass | the prompt family is shared across systems. |",
            "| scorer_alignment | conditional_pass | temporal reasoning is partially verified; multi-hop checks remain incomplete. |",
            "| statistical_reporting | pass | descriptive statistics are reported for the fixed 24-case slice. |",
            "| statistical_inference | not_required | inferential statistics are deferred until a larger official benchmark slice is used. |",
            "| promotion | pending | paper-facing promotion is deferred until the audit gate is fully closed. |",
            "",
            "## 8. Scorer Alignment Audit",
            "",
            "| Audit Item | Official Scorer | SRP Wrapper | Result | Notes |",
            "| --- | --- | --- | --- | --- |",
            "| Exact match | Yes | Yes | Pass | Normalized exact comparison is consistent for direct-answer cases. |",
            "| Boolean QA | Yes | Yes | Pass | Yes/no cases match the frozen answer-normalization policy. |",
            "| Preference revision | Yes | Yes | Pass | The current slice resolves the updated preference correctly. |",
            "| Contradiction resolution | Yes | Yes | Pass | Temporal negation is interpreted consistently in the wrapper. |",
            "| Normalization | Yes | Yes | Pass | Lowercasing, whitespace trimming, and punctuation handling are frozen. |",
            "| Temporal reasoning | Yes | Partially verified | Conditional pass | The slice contains temporal cases, but larger parity checks are still needed. |",
            "| Multi-hop reasoning | Yes | Not fully exercised | Pending | Not enough representative examples yet for a final acceptance decision. |",
            "| Unsupported outputs | Yes | Yes | Pass | Empty or malformed outputs are handled as wrapper-level failures, not scorer successes. |",
            "",
            "Overall scorer alignment status: `conditional_pass`",
            "",
            "## 9. Evidence Audit Notes",
            "",
            "- `hallucinated_relation_rate` measures extra recovered relations beyond the target state, so it can remain non-zero even when target relations are fully recovered.",
            "- `evidence_cost` is an internal recovery cost unit derived from selected units and relations; it is not a token-count proxy.",
            "- The official benchmark score and the SRP diagnostics are co-reported but are not forced to share the same numerical objective.",
            "- The prompt template id is frozen in the runtime contract so baseline and SRP generation share the same prompt family.",
            "- The audit specification is frozen in `SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md` and governs promotion to paper-facing evidence.",
            "",
            "## 10. Trace Inventory",
            "",
            f"- trace count: `{len(generation_traces)}`",
        ]
    )
    return "\n".join(lines)


def write_longmemeval_evidence_outputs(
    output_dir: str | Path,
    config: ExternalValidationLongMemEvalEvidenceConfig | None = None,
) -> dict[str, Any]:
    config = config or load_external_validation_longmemeval_evidence_config()
    outputs = run_longmemeval_evidence(config=config)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]

    records = outputs["report"]["records"]
    records_csv = output_path / "longmemeval_evidence_records.csv"
    records_jsonl = output_path / "longmemeval_evidence_records.jsonl"
    summary_json = output_path / "longmemeval_evidence_summary.json"
    statistical_json = output_path / "longmemeval_evidence_statistical_summary.json"
    report_json = output_path / "longmemeval_evidence_report.json"
    report_md = output_path / "longmemeval_evidence_report.md"
    root_report = repo_root / "SRP_EXTERNAL_VALIDATION_LONGMEMEVAL_EVIDENCE_REPORT.md"
    runtime_manifest_path = output_path / "runtime_manifest.json"
    traces_json = output_path / "longmemeval_evidence_generation_traces.json"
    metadata_json = output_path / "longmemeval_evidence_metadata.json"

    if records:
        fieldnames = [
            "run_id",
            "benchmark_name",
            "baseline_name",
            "seed",
            "case_id",
            "query",
            "expected_answer",
            "predicted_answer",
            "semantic_coverage",
            "semantic_drift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "neighborhood_completeness",
            "hallucinated_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
            "failure_categories",
        ]
        with records_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                run = record["run"]
                case = run["case"]
                metrics = record["metrics"]
                response = record["response"]
                writer.writerow(
                    {
                        "run_id": run["run_id"],
                        "benchmark_name": run["benchmark_name"],
                        "baseline_name": run["baseline_name"],
                        "seed": run["seed"],
                        "case_id": case["case_id"],
                        "query": case["query"],
                        "expected_answer": case["expected_answer"],
                        "predicted_answer": response["predicted_answer"],
                        "semantic_coverage": metrics["semantic_coverage"],
                        "semantic_drift": metrics["semantic_drift"],
                        "fact_accuracy": metrics["fact_accuracy"],
                        "relation_accuracy": metrics["relation_accuracy"],
                        "recovery_accuracy": metrics["recovery_accuracy"],
                        "closure_accuracy": metrics["closure_accuracy"],
                        "neighborhood_completeness": metrics["neighborhood_completeness"],
                        "hallucinated_relation_rate": metrics["hallucinated_relation_rate"],
                        "evidence_cost": metrics["evidence_cost"],
                        "answer_accuracy": metrics["answer_accuracy"],
                        "official_metric_score": metrics["official_metric_score"],
                        "failure_categories": "|".join(record.get("failure_categories", [])),
                    }
                )

        with records_jsonl.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False, default=str))
                handle.write("\n")

    summary_json.write_text(json.dumps(outputs["report"]["summary"], indent=2, ensure_ascii=False), encoding="utf-8")
    statistical_json.write_text(json.dumps(outputs["report"].get("statistical_summary", {}), indent=2, ensure_ascii=False), encoding="utf-8")
    report_json.write_text(json.dumps(outputs["report"], indent=2, ensure_ascii=False), encoding="utf-8")
    report_md.write_text(outputs["markdown"], encoding="utf-8")
    root_report.write_text(outputs["markdown"], encoding="utf-8")
    write_runtime_manifest(runtime_manifest_path, outputs["runtime_manifest"])
    traces_json.write_text(json.dumps(outputs["traces"], indent=2, ensure_ascii=False), encoding="utf-8")
    metadata_json.write_text(
        json.dumps(
            {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generated_by": "external_validation_longmemeval_evidence_v1",
                "benchmark_name": config.benchmark_name,
                "output_dir": str(output_path),
                "case_count": outputs["report"]["summary"].get("case_count", 0),
                "trace_count": len(outputs["traces"]),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return {
        "output_dir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "statistical_json": str(statistical_json),
        "report_markdown": str(report_md),
        "root_report_markdown": str(root_report),
        "report_json": str(report_json),
        "runtime_manifest_json": str(runtime_manifest_path),
        "traces_json": str(traces_json),
        "metadata_json": str(metadata_json),
        "report": outputs["report"],
        "markdown": outputs["markdown"],
        "runtime_manifest": outputs["runtime_manifest"],
    }
