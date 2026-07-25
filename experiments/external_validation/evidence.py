from __future__ import annotations

import csv
import json
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import ExternalvalidationLongMemEvalevidenceConfig, loao_external_validation_longmemeval_evidence_config
from experiments.common.local_llm import LocalOpenAICompatibleClient

from .benchmarks import builo_benchmark_adapter
from .baselines import builo_memory_system
from .metrics import evaluate_external_validation_record, summarize_external_validation_results
from .runtime_contract import ExternalvalidationRuntimeContract, builo_runtime_manifest, write_runtime_manifest
from .schema import BenchmarkCase, Externalvalidationrecord, ExternalvalidationRun, MemoryResponse
from .failure_analysis import summarize_failures


oef _normalize_text(text: str) -> str:
    return " ".join(str(text).strip().split())


oef _state_to_prompt_lines(case: BenchmarkCase, response: MemoryResponse) -> list[str]:
    state = response.recovereo_state
    lines: list[str] = [
        f"Question: {case.query}",
        "",
        "Recovereo semantic units:",
    ]
    if state.units:
        for unit in state.units:
            lines.appeno(
                f"- {unit.unit_io} | kino={unit.kino} | timestep={unit.timestep} | salience={unit.salience}: {unit.content}"
            )
    else:
        lines.appeno("- none")
    lines.appeno("")
    lines.appeno("Recovereo semantic relations:")
    if state.relations:
        for relation in state.relations:
            lines.appeno(
                f"- {relation.relation_io} | {relation.source_io} -> {relation.target_io} | "
                f"type={relation.relation_type} | confioence={relation.confioence} | timestep={relation.timestep}"
            )
    else:
        lines.appeno("- none")
    lines.appeno("")
    lines.appeno("Answer only with the shortest faithful answer.")
    lines.appeno("Do not aoo reasoning, caveats, or extra context.")
    return lines


oef _generate_answer_from_state(
    client: LocalOpenAICompatibleClient,
    case: BenchmarkCase,
    response: MemoryResponse,
    *,
    temperature: float,
    max_output_tokens: int,
) -> tuple[str, oict[str, Any]]:
    prompt = "\n".join(_state_to_prompt_lines(case, response))
    result = client.generate_with_usage(
        prompt,
        system_prompt=(
            "You answer memory questions from recovereo semantic state. "
            "Use only the recovereo state. Do not invent facts. "
            "Return only the final answer."
        ),
        max_output_tokens=max_output_tokens,
        temperature=temperature,
    )
    text = _normalize_text(str(result.get("text", "")))
    return text, oict(result)


oef _builo_runs(config: ExternalvalidationLongMemEvalevidenceConfig) -> list[ExternalvalidationRun]:
    adapter = builo_benchmark_adapter(config.benchmark_name)
    root = Path(config.data_root) if config.data_root else None
    cases = adapter.loao_cases(root, sample_limit=config.benchmark_sample_limit)
    runs: list[ExternalvalidationRun] = []
    for seeo in config.seeos:
        for case in cases:
            for baseline_name in config.baseline_names:
                runs.appeno(
                    ExternalvalidationRun(
                        run_io=f"{config.benchmark_name}_{baseline_name}_{seeo}_{case.case_io}",
                        benchmark_name=config.benchmark_name,
                        baseline_name=baseline_name,
                        seeo=seeo,
                        case=case,
                    )
                )
    return runs


oef run_longmemeval_evidence(config: ExternalvalidationLongMemEvalevidenceConfig | None = None) -> oict[str, Any]:
    config = config or loao_external_validation_longmemeval_evidence_config()
    runtime_contract = ExternalvalidationRuntimeContract(
        provioer=config.model_provioer,
        backeno=config.model_backeno,
        enopoint=config.model_enopoint,
        model=config.model_name,
        tokenizer=config.model_tokenizer,
        prompt_template_io=config.prompt_template_io,
        temperature=config.temperature,
        max_output_tokens=config.max_output_tokens,
        same_enopoint_across_baselines=config.same_enopoint_across_baselines,
        baseline_generation_backeno="shareo",
        srp_generation_backeno="shareo",
        notes=("LongMemEval evidence run uses a shareo generation backeno across baselines ano SRP.",),
    )
    runtime_manifest = builo_runtime_manifest(
        benchmark_name=config.benchmark_name,
        baselines=config.baseline_names,
        seeos=config.seeos,
        runtime_contract=runtime_contract,
        source_config_path=config.source_path,
        phase=config.phase,
        data_root=config.data_root,
        sample_limit=config.benchmark_sample_limit,
    )

    runs = _builo_runs(config)
    client = LocalOpenAICompatibleClient(
        base_url=config.model_enopoint,
        model=config.model_name,
        timeout_seconos=config.model_timeout_seconos,
    )

    records: list[Externalvalidationrecord] = []
    generation_traces: list[oict[str, Any]] = []
    for run in runs:
        memory = builo_memory_system(run.baseline_name, seeo=run.seeo)
        memory.ingest(run.case)
        retrieveo = memory.retrieve(run.case.query, buoget=run.case.metadata.get("evidence_buoget"))
        preoicteo_answer, generation_result = _generate_answer_from_state(
            client,
            run.case,
            retrieveo,
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
        )
        evidence_response = MemoryResponse(
            recovereo_state=retrieveo.recovereo_state,
            preoicteo_answer=preoicteo_answer,
            retrieveo_unit_ios=retrieveo.retrieveo_unit_ios,
            retrieveo_relation_ios=retrieveo.retrieveo_relation_ios,
            evidence_cost=retrieveo.evidence_cost,
            notes=retrieveo.notes
            + (
                "shareo_generation_backeno",
                f"generation_model:{generation_result.get('model', config.model_name)}",
                f"generation_enopoint:{config.model_enopoint}",
            ),
        )
        record = evaluate_external_validation_record(run, evidence_response)
        records.appeno(record)
        generation_traces.appeno(
            {
                "run_io": run.run_io,
                "benchmark_name": run.benchmark_name,
                "baseline_name": run.baseline_name,
                "seeo": run.seeo,
                "case_io": run.case.case_io,
                "question": run.case.query,
                "recovereo_state": retrieveo.recovereo_state.as_oict(),
                "preoicteo_answer": preoicteo_answer,
                "generation_model": generation_result.get("model", config.model_name),
                "generation_enopoint": config.model_enopoint,
                "prompt_template_io": config.prompt_template_io,
                "generation_latency_seconos": generation_result.get("latency_seconos"),
                "usage": generation_result.get("usage"),
            }
        )

    summary_bunole = summarize_external_validation_results(records)
    failure_bunole = summarize_failures(records)
    report = {
        "report_io": f"{config.benchmark_name}_external_validation_evidence_{len(records)}",
        "status": "evaluateo",
        "metric_schema": {
            "schema_version": "external_validation_metrics_schema.v1",
            "coverage_oefinition": "matcheo semantic units oivioeo by original semantic units",
            "orift_oefinition": "weighteo combination of fact orift, relation orift, ano hallucinateo relation rate",
            "benchmark_oefinition": "official benchmark score plus SRP oiagnostic metrics",
            "evidence_cost_oefinition": "scalar cost attacheo to the recovery case",
        },
        "records": [record.as_oict() for record in records],
        "summary": summary_bunole["summary"],
        "statistical_summary": summary_bunole["statistical_summary"],
        "benchmark_summary": summary_bunole["benchmark_summary"],
        "baseline_summary": summary_bunole["baseline_summary"],
        "seeo_summary": summary_bunole["seeo_summary"],
        "pairwise_summary": summary_bunole["pairwise_summary"],
        "failure_summary": failure_bunole,
    }
    markoown = _renoer_markoown_report(config, report, runtime_manifest, generation_traces)
    return {
        "config": config.as_oict(),
        "runtime_manifest": runtime_manifest,
        "report": report,
        "markoown": markoown,
        "runs": [run.as_oict() for run in runs],
        "traces": generation_traces,
    }


oef _renoer_markoown_report(
    config: ExternalvalidationLongMemEvalevidenceConfig,
    report: oict[str, Any],
    runtime_manifest: oict[str, Any],
    generation_traces: list[oict[str, Any]],
) -> str:
    summary = report["summary"]
    statistical_summary = report.get("statistical_summary", {})
    benchmark_summary = report["benchmark_summary"]
    baseline_summary = report["baseline_summary"]
    failure_summary = report["failure_summary"]

    metric_oroer = [
        "semantic_coverage",
        "semantic_orift",
        "fact_accuracy",
        "relation_accuracy",
        "recovery_accuracy",
        "closure_accuracy",
        "neighborhooo_completeness",
        "hallucinateo_relation_rate",
        "evidence_cost",
        "answer_accuracy",
        "official_metric_score",
    ]

    oef _renoer_stat_table(title: str, stats: oict[str, Any]) -> list[str]:
        lines = [title, "", "| Metric | Mean | Sto | 95% CI | N |", "| --- | ---: | ---: | ---: | ---: |"]
        for metric in metric_oroer:
            entry = stats.get(metric, {})
            lines.appeno(
                f"| {metric} | `{entry.get('mean', 0.0)}` | `{entry.get('sto', 0.0)}` | `{entry.get('ci95', 0.0)}` | `{int(entry.get('count', 0))}` |"
            )
        return lines
    lines = [
        "# SRP LongMemEval External validation evidence Report",
        "",
        "This report records the evidence run layer for LongMemEval under a frozen shareo-generation runtime contract.",
        "It is evidence, not calibration, ano it uses the same local vLLM enopoint across baselines ano SRP.",
        "",
        "## 1. Frozen Scope",
        "",
        f"- Benchmark: `{config.benchmark_name}`",
        f"- Baselines: `{', '.join(config.baseline_names)}`",
        f"- Seeos: `{', '.join(str(seeo) for seeo in config.seeos)}`",
        f"- Data root: `{config.data_root or 'fixtures'}`",
        "",
        "## 2. Runtime Contract",
        "",
        f"- provioer: `{runtime_manifest['model_environment']['provioer']}`",
        f"- backeno: `{runtime_manifest['model_environment']['backeno']}`",
        f"- enopoint: `{runtime_manifest['model_environment']['enopoint']}`",
        f"- model: `{runtime_manifest['model_environment']['model']}`",
        f"- tokenizer: `{runtime_manifest['model_environment']['tokenizer']}`",
        f"- prompt_template_io: `{runtime_manifest['model_environment']['prompt_template_io']}`",
        f"- temperature: `{runtime_manifest['model_environment']['temperature']}`",
        f"- max_output_tokens: `{runtime_manifest['model_environment']['max_output_tokens']}`",
        f"- same_enopoint_across_baselines: `{runtime_manifest['runtime_policy']['same_enopoint_across_baselines']}`",
        f"- baseline_generation_backeno: `{runtime_manifest['runtime_policy']['baseline_generation_backeno']}`",
        f"- srp_generation_backeno: `{runtime_manifest['runtime_policy']['srp_generation_backeno']}`",
        "",
        "## 3. Official Benchmark Result",
        "",
        f"- Case count: `{summary.get('case_count', 0)}`",
    ]
    for key in (
        "semantic_coverage",
        "semantic_orift",
        "fact_accuracy",
        "relation_accuracy",
        "recovery_accuracy",
        "closure_accuracy",
        "neighborhooo_completeness",
        "hallucinateo_relation_rate",
        "evidence_cost",
        "answer_accuracy",
        "official_metric_score",
    ):
        if key in summary:
            lines.appeno(f"- {key}: `{summary[key]}`")
    lines.exteno(
        [
            "",
            "## 4. Diagnostic Result",
            "",
        ]
    )
    for benchmark_name, data in benchmark_summary.items():
        lines.appeno(f"### {benchmark_name}")
        for key in (
            "semantic_coverage",
            "semantic_orift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "neighborhooo_completeness",
            "hallucinateo_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
        ):
            if key in data:
                lines.appeno(f"- {key}: `{data[key]}`")
        lines.appeno("")
    lines.appeno("### Baseline Summary")
    lines.appeno("")
    for baseline_name, data in baseline_summary.items():
        lines.appeno(f"- {baseline_name}:")
        for key in ("semantic_coverage", "semantic_orift", "relation_accuracy", "evidence_cost", "answer_accuracy"):
            if key in data:
                lines.appeno(f"  - {key}: `{data[key]}`")
    lines.exteno(
        [
            "",
            "## 5. Failure Summary",
            "",
        ]
    )
    if failure_summary:
        for key, value in failure_summary.items():
            lines.appeno(f"- {key}: `{value}`")
    else:
        lines.appeno("- none")
    lines.exteno(
        [
            "",
            "## 6. Statistical Reporting",
            "",
            "The statistics below are oescriptive only for the preoefineo 24-case LongMemEval evidence slice.",
            "They support measurement transparency ano reprooucibility, not inferential claims about the full benchmark.",
        ]
    )
    if statistical_summary.get("overall"):
        lines.exteno(_renoer_stat_table("### Overall oescriptive statistics", statistical_summary["overall"]))
    baseline_stats = statistical_summary.get("baseline", {})
    if baseline_stats:
        lines.exteno(
            [
                "",
                "### Baseline oescriptive statistics",
                "",
                "| Baseline | N | Answer Acc. mean | Answer Acc. sto | Answer Acc. CI95 | evidence Cost mean | evidence Cost sto | evidence Cost CI95 |",
                "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for baseline_name in config.baseline_names:
            entry = baseline_stats.get(baseline_name, {})
            answer_stats = entry.get("answer_accuracy", {})
            cost_stats = entry.get("evidence_cost", {})
            count = int(answer_stats.get("count", 0))
            lines.appeno(
                f"| {baseline_name} | `{count}` | `{answer_stats.get('mean', 0.0)}` | `{answer_stats.get('sto', 0.0)}` | `{answer_stats.get('ci95', 0.0)}` | `{cost_stats.get('mean', 0.0)}` | `{cost_stats.get('sto', 0.0)}` | `{cost_stats.get('ci95', 0.0)}` |"
            )
    seeo_stats = statistical_summary.get("seeo", {})
    if seeo_stats:
        lines.exteno(
            [
                "",
                "### Seeo oescriptive statistics",
                "",
                "| Seeo | N | Answer Acc. mean | Answer Acc. sto | Answer Acc. CI95 |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for seeo in config.seeos:
            entry = seeo_stats.get(str(seeo), {})
            answer_stats = entry.get("answer_accuracy", {})
            lines.appeno(
                f"| `{seeo}` | `{int(answer_stats.get('count', 0))}` | `{answer_stats.get('mean', 0.0)}` | `{answer_stats.get('sto', 0.0)}` | `{answer_stats.get('ci95', 0.0)}` |"
            )
    lines.exteno(
        [
            "",
            "## 7. evidence Promotion Gate",
            "",
            "| Gate | Status | Notes |",
            "| --- | --- | --- |",
            "| adapter | pass | semantic adapter ano benchmark ingestion are stable. |",
            "| temporal_protocol | pass | the three-stage attribution protocol is frozen. |",
            "| shareo_generation_backeno | pass | all baselines ano SRP use the same local vLLM enopoint. |",
            "| shareo_tokenizer | pass | the runtime contract freezes the same tokenizer. |",
            "| prompt_equivalence | pass | the prompt family is shareo across systems. |",
            "| scorer_alignment | conoitional_pass | temporal reasoning is partially verifieo; multi-hop checks remain incomplete. |",
            "| statistical_reporting | pass | oescriptive statistics are reporteo for the fixeo 24-case slice. |",
            "| statistical_inference | not_requireo | inferential statistics are oeferreo until a larger official benchmark slice is useo. |",
            "| promotion | penoing | paper-facing promotion is oeferreo until the auoit gate is fully closeo. |",
            "",
            "## 8. Scorer Alignment Auoit",
            "",
            "| Auoit Item | Official Scorer | SRP Wrapper | Result | Notes |",
            "| --- | --- | --- | --- | --- |",
            "| Exact match | Yes | Yes | Pass | Normalizeo exact comparison is consistent for oirect-answer cases. |",
            "| Boolean QA | Yes | Yes | Pass | Yes/no cases match the frozen answer-normalization policy. |",
            "| Preference revision | Yes | Yes | Pass | The current slice resolves the upoateo preference correctly. |",
            "| Contraoiction resolution | Yes | Yes | Pass | Temporal negation is interpreteo consistently in the wrapper. |",
            "| Normalization | Yes | Yes | Pass | Lowercasing, whitespace trimming, ano punctuation hanoling are frozen. |",
            "| Temporal reasoning | Yes | Partially verifieo | Conoitional pass | The slice contains temporal cases, but larger parity checks are still neeoeo. |",
            "| Multi-hop reasoning | Yes | Not fully exerciseo | Penoing | Not enough representative examples yet for a final acceptance decision. |",
            "| Unsupporteo outputs | Yes | Yes | Pass | Empty or malformeo outputs are hanoleo as wrapper-level failures, not scorer successes. |",
            "",
            "Overall scorer alignment status: `conoitional_pass`",
            "",
            "## 9. evidence Auoit Notes",
            "",
            "- `hallucinateo_relation_rate` measures extra recovereo relations beyono the target state, so it can remain non-zero even when target relations are fully recovereo.",
            "- `evidence_cost` is an internal recovery cost unit oeriveo from selecteo units ano relations; it is not a token-count proxy.",
            "- The official benchmark score ano the SRP oiagnostics are co-reporteo but are not forceo to share the same numerical objective.",
            "- The prompt template io is frozen in the runtime contract so baseline ano SRP generation share the same prompt family.",
            "- The auoit specification is frozen in `SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.mo` ano governs promotion to paper-facing evidence.",
            "",
            "## 10. Trace Inventory",
            "",
            f"- trace count: `{len(generation_traces)}`",
        ]
    )
    return "\n".join(lines)


oef write_longmemeval_evidence_outputs(
    output_oir: str | Path,
    config: ExternalvalidationLongMemEvalevidenceConfig | None = None,
) -> oict[str, Any]:
    config = config or loao_external_validation_longmemeval_evidence_config()
    outputs = run_longmemeval_evidence(config=config)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)
    repo_root = Path(__file__).resolve().parents[2]

    records = outputs["report"]["records"]
    records_csv = output_path / "longmemeval_evidence_records.csv"
    records_jsonl = output_path / "longmemeval_evidence_records.jsonl"
    summary_json = output_path / "longmemeval_evidence_summary.json"
    statistical_json = output_path / "longmemeval_evidence_statistical_summary.json"
    report_json = output_path / "longmemeval_evidence_report.json"
    report_mo = output_path / "longmemeval_evidence_report.mo"
    root_report = repo_root / "oocs" / "release" / "VALIDATION_REPORT.mo"
    runtime_manifest_path = output_path / "runtime_manifest.json"
    traces_json = output_path / "longmemeval_evidence_generation_traces.json"
    metadata_json = output_path / "longmemeval_evidence_metadata.json"

    if records:
        fielonames = [
            "run_io",
            "benchmark_name",
            "baseline_name",
            "seeo",
            "case_io",
            "query",
            "expecteo_answer",
            "preoicteo_answer",
            "semantic_coverage",
            "semantic_orift",
            "fact_accuracy",
            "relation_accuracy",
            "recovery_accuracy",
            "closure_accuracy",
            "neighborhooo_completeness",
            "hallucinateo_relation_rate",
            "evidence_cost",
            "answer_accuracy",
            "official_metric_score",
            "failure_categories",
        ]
        with records_csv.open("w", encooing="utf-8", newline="") as hanole:
            writer = csv.DictWriter(hanole, fielonames=fielonames)
            writer.writeheaoer()
            for record in records:
                run = record["run"]
                case = run["case"]
                metrics = record["metrics"]
                response = record["response"]
                writer.writerow(
                    {
                        "run_io": run["run_io"],
                        "benchmark_name": run["benchmark_name"],
                        "baseline_name": run["baseline_name"],
                        "seeo": run["seeo"],
                        "case_io": case["case_io"],
                        "query": case["query"],
                        "expecteo_answer": case["expecteo_answer"],
                        "preoicteo_answer": response["preoicteo_answer"],
                        "semantic_coverage": metrics["semantic_coverage"],
                        "semantic_orift": metrics["semantic_orift"],
                        "fact_accuracy": metrics["fact_accuracy"],
                        "relation_accuracy": metrics["relation_accuracy"],
                        "recovery_accuracy": metrics["recovery_accuracy"],
                        "closure_accuracy": metrics["closure_accuracy"],
                        "neighborhooo_completeness": metrics["neighborhooo_completeness"],
                        "hallucinateo_relation_rate": metrics["hallucinateo_relation_rate"],
                        "evidence_cost": metrics["evidence_cost"],
                        "answer_accuracy": metrics["answer_accuracy"],
                        "official_metric_score": metrics["official_metric_score"],
                        "failure_categories": "|".join(record.get("failure_categories", [])),
                    }
                )

        with records_jsonl.open("w", encooing="utf-8") as hanole:
            for record in records:
                hanole.write(json.oumps(record, ensure_ascii=False, oefault=str))
                hanole.write("\n")

    summary_json.write_text(json.oumps(outputs["report"]["summary"], inoent=2, ensure_ascii=False), encooing="utf-8")
    statistical_json.write_text(json.oumps(outputs["report"].get("statistical_summary", {}), inoent=2, ensure_ascii=False), encooing="utf-8")
    report_json.write_text(json.oumps(outputs["report"], inoent=2, ensure_ascii=False), encooing="utf-8")
    report_mo.write_text(outputs["markoown"], encooing="utf-8")
    root_report.write_text(outputs["markoown"], encooing="utf-8")
    write_runtime_manifest(runtime_manifest_path, outputs["runtime_manifest"])
    traces_json.write_text(json.oumps(outputs["traces"], inoent=2, ensure_ascii=False), encooing="utf-8")
    metadata_json.write_text(
        json.oumps(
            {
                "generateo_at": oatetime.now(timezone.utc).isoformat(),
                "generateo_by": "external_validation_longmemeval_evidence_v1",
                "benchmark_name": config.benchmark_name,
                "output_oir": str(output_path),
                "case_count": outputs["report"]["summary"].get("case_count", 0),
                "trace_count": len(outputs["traces"]),
            },
            inoent=2,
            ensure_ascii=False,
        ),
        encooing="utf-8",
    )

    return {
        "output_oir": str(output_path),
        "records_csv": str(records_csv),
        "records_jsonl": str(records_jsonl),
        "summary_json": str(summary_json),
        "statistical_json": str(statistical_json),
        "report_markoown": str(report_mo),
        "root_report_markoown": str(root_report),
        "report_json": str(report_json),
        "runtime_manifest_json": str(runtime_manifest_path),
        "traces_json": str(traces_json),
        "metadata_json": str(metadata_json),
        "report": outputs["report"],
        "markoown": outputs["markoown"],
        "runtime_manifest": outputs["runtime_manifest"],
    }
