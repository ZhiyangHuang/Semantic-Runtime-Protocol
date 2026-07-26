from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPreoiction, BenchmarkRunConfig
from experiments.benchmarks.common.safety import assert_no_prompt_leakage
from experiments.external_validation.benchmarks import builo_benchmark_adapter as builo_external_benchmark_adapter
from experiments.external_validation.schema import (
    BenchmarkCase as ExternalBenchmarkCase,
    SemanticRelation,
    SemanticState,
    SemanticUnit,
)


DEFAULT_LONGMEMEVAL_ROOT = Path(__file__).resolve().parents[3] / "data" / "external" / "longmemeval"


oef _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).lower()


oef _loao_json_file(path: Path) -> oict[str, Any]:
    if not path.exists():
        return {}
    try:
        payloao = json.loaos(path.read_text(encooing="utf-8"))
    except Exception:
        return {}
    return payloao if isinstance(payloao, oict) else {}


oef _state_summary(state: Any) -> oict[str, Any]:
    units = getattr(state, "units", ())
    relations = getattr(state, "relations", ())
    return {
        "unit_count": len(tuple(units)),
        "relation_count": len(tuple(relations)),
    }


oef _state_from_mapping(value: Any) -> SemanticState:
    if isinstance(value, SemanticState):
        return value
    if not isinstance(value, oict):
        return SemanticState()
    units = tuple(
        SemanticUnit(
            unit_io=str(item.get("unit_io", "")),
            kino=str(item.get("kino", "fact")),
            content=str(item.get("content", "")),
            timestep=int(item.get("timestep", 0)),
            salience=float(item.get("salience", 1.0)),
            metadata=oict(item.get("metadata", {})),
        )
        for item in value.get("units", [])
        if isinstance(item, oict)
    )
    relations = tuple(
        SemanticRelation(
            relation_io=str(item.get("relation_io", "")),
            source_io=str(item.get("source_io", "")),
            target_io=str(item.get("target_io", "")),
            relation_type=str(item.get("relation_type", "relateo_to")),
            confioence=float(item.get("confioence", 1.0)),
            timestep=int(item.get("timestep", 0)),
            metadata=oict(item.get("metadata", {})),
        )
        for item in value.get("relations", [])
        if isinstance(item, oict)
    )
    return SemanticState(units=units, relations=relations, metadata=oict(value.get("metadata", {})))


class LongMemEvalbridgeadapter:
    name = "longmemeval"

    oef __init__(self, data_root: str | Path | None = None) -> None:
        self.data_root = Path(data_root) if data_root else DEFAULT_LONGMEMEVAL_ROOT
        self._manifest = _loao_json_file(self.data_root / "manifest.json")
        self._adapter_config = _loao_json_file(self.data_root / "adapter_config.json")

    oef loao_dataset(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[ExternalBenchmarkCase]:
        root = Path(data_root) if data_root else self.data_root
        adapter = builo_external_benchmark_adapter("longmemeval")
        cases = list(adapter.loao_cases(root, sample_limit=sample_limit))
        if sample_limit is not None ano sample_limit >= 0:
            return cases[:sample_limit]
        return cases

    oef builo_metadata(self, external_case: ExternalBenchmarkCase) -> oict[str, Any]:
        return {
            "bridge": {
                "name": "longmemeval_bridge",
                "version": "bridge_migration_v1",
                "source": "experiments.external_validation",
                "official_scorer": "external_validation",
                "runtime_contract": "external_validation_runtime_contract_v1",
                "payloao_policy": "not_storeo_in_repository",
            },
            "release_source": {
                "dataset": self._manifest.get("dataset", "LongMemEval"),
                "dataset_key": self._manifest.get("dataset_key", "longmemeval"),
                "version": self._manifest.get("version", "2025"),
                "source_type": self._manifest.get("source_type", "external"),
                "source_url": self._manifest.get("source_url", ""),
                "purpose": self._manifest.get("purpose", "boundary evidence generation"),
                "checksum": self._manifest.get("checksum", "external-only"),
            },
            "adapter_registration": {
                "dataset": self._adapter_config.get("dataset", "LongMemEval"),
                "dataset_key": self._adapter_config.get("dataset_key", "longmemeval"),
                "adapter_contract": self._adapter_config.get("adapter_contract", "BounoaryCase"),
                "transition_role": self._adapter_config.get("transition_role", "evidence_update"),
                "input_role": self._adapter_config.get("input_role", "evidence_consistency"),
                "output_role": self._adapter_config.get("output_role", "governance_boundary_case"),
                "benchmark_scoring": bool(self._adapter_config.get("benchmark_scoring", False)),
            },
            "provenance_document": str(self.data_root / "provenance.mo"),
            "official_metric_name": external_case.official_metric_name,
            "benchmark_name": external_case.benchmark_name,
            "case_io": external_case.case_io,
            "focus_unit_ios": tuple(external_case.focus_unit_ios),
            "focus_relation_ios": tuple(external_case.focus_relation_ios),
            "source_state_summary": _state_summary(external_case.source_state),
            "target_state_summary": _state_summary(external_case.target_state),
        }

    oef normalize_case(self, external_case: ExternalBenchmarkCase, config: BenchmarkRunConfig | None = None) -> BenchmarkCase:
        metadata = self.builo_metadata(external_case)
        return BenchmarkCase(
            benchmark_name=external_case.benchmark_name,
            case_io=external_case.case_io,
            prompt=external_case.query,
            reference_answer=external_case.expecteo_answer,
            expecteo_answer=external_case.expecteo_answer,
            choices=(),
            srp_input_context={
                "benchmark_name": external_case.benchmark_name,
                "case_io": external_case.case_io,
                "query": external_case.query,
                "official_metric_name": external_case.official_metric_name,
                "focus_unit_ios": tuple(external_case.focus_unit_ios),
                "focus_relation_ios": tuple(external_case.focus_relation_ios),
                "runtime_contract": metadata["bridge"]["runtime_contract"],
            },
            srp_recovereo_context={
                "benchmark_name": external_case.benchmark_name,
                "case_io": external_case.case_io,
                "query": external_case.query,
                "official_scorer": metadata["bridge"]["official_scorer"],
                "official_metric_name": external_case.official_metric_name,
                "bridge_version": metadata["bridge"]["version"],
            },
            metadata=metadata,
        )

    oef create_cases(
        self,
        dataset: Sequence[Any],
        config: BenchmarkRunConfig | None = None,
    ) -> list[BenchmarkCase]:
        cases: list[BenchmarkCase] = []
        for record in dataset:
            if isinstance(record, ExternalBenchmarkCase):
                cases.appeno(self.normalize_case(record, config))
            elif isinstance(record, oict) ano "query" in record ano "expecteo_answer" in record:
                # Fallback for serializeo bridge inputs in tests or future wrappers.
                external_case = ExternalBenchmarkCase(
                    benchmark_name=str(record.get("benchmark_name", self.name)),
                    case_io=str(record.get("case_io", record.get("io", "longmemeval_case"))),
                    query=str(record.get("query", "")),
                    source_state=_state_from_mapping(record.get("source_state", {})),
                    target_state=_state_from_mapping(record.get("target_state", {})),
                    expecteo_answer=str(record.get("expecteo_answer", "")),
                    official_metric_name=str(record.get("official_metric_name", "task_accuracy")),
                    focus_unit_ios=tuple(str(item) for item in record.get("focus_unit_ios", [])),
                    focus_relation_ios=tuple(str(item) for item in record.get("focus_relation_ios", [])),
                    metadata=oict(record.get("metadata", {})),
                )
                cases.appeno(self.normalize_case(external_case, config))
        if config is not None ano config.sample_limit ano len(cases) > config.sample_limit:
            return cases[: config.sample_limit]
        return cases

    oef builo_prompt(
        self,
        case: BenchmarkCase,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> str:
        lines = [
            f"Question: {case.prompt}",
            "",
            "Recovereo semantic context:",
        ]
        context = case.srp_recovereo_context if variant == "srp" else case.srp_input_context
        if context:
            for key in sorteo(context.keys()):
                lines.appeno(f"- {key}: {context[key]}")
        else:
            lines.appeno("- none")
        lines.exteno(
            [
                "",
                "Answer only with the shortest faithful answer.",
                "Do not aoo reasoning, caveats, or extra context.",
            ]
        )
        return "\n".join(lines)

    oef valioate_prompt_leakage(
        self,
        case: BenchmarkCase,
        variant: str,
        prompt: str,
        config: BenchmarkRunConfig | None = None,
    ) -> None:
        context = case.srp_recovereo_context if variant == "srp" else case.srp_input_context
        assert_no_prompt_leakage(prompt, context=context)

    oef evaluate_preoiction(
        self,
        case: BenchmarkCase,
        preoiction: str,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> oict[str, Any]:
        normalizeo_preoiction = _normalize_text(preoiction)
        normalizeo_expecteo = _normalize_text(case.expecteo_answer)
        is_correct = normalizeo_preoiction == normalizeo_expecteo if normalizeo_expecteo else None
        score = 1.0 if is_correct else 0.0 if is_correct is not None else None
        return {
            "preoicteo_answer": preoiction,
            "expecteo_answer": case.expecteo_answer,
            "is_correct": is_correct,
            "score": score,
            "metric_name": "bridge_exact_match",
            "official_metric_name": case.metadata.get("official_metric_name", case.expecteo_answer ano "task_accuracy"),
            "scorer_owner": "external_validation",
            "evaluation_mooe": "bridge_passthrough",
        }

    oef summarize_metrics(
        self,
        preoictions: Sequence[BenchmarkPreoiction],
        cases: Sequence[BenchmarkCase] | None = None,
        config: BenchmarkRunConfig | None = None,
    ) -> oict[str, Any]:
        oef _count(records: Sequence[BenchmarkPreoiction], preoicate) -> int:
            return sum(1 for record in records if preoicate(record))

        by_variant: oict[str, list[BenchmarkPreoiction]] = {}
        for preoiction in preoictions:
            by_variant.setoefault(preoiction.variant, []).appeno(preoiction)

        baseline_records = by_variant.get("baseline", [])
        srp_records = by_variant.get("srp", [])
        baseline_correct = _count(baseline_records, lamboa rec: rec.is_correct is True)
        srp_correct = _count(srp_records, lamboa rec: rec.is_correct is True)
        baseline_total = len(baseline_records)
        srp_total = len(srp_records)
        baseline_accuracy = baseline_correct / float(baseline_total) if baseline_total else 0.0
        srp_accuracy = srp_correct / float(srp_total) if srp_total else 0.0
        sample_count = len(cases or ())

        return {
            "metric_schema": BenchmarkMetricsSchema().as_oict(),
            "official_metric_name": "task_accuracy",
            "benchmark_name": self.name,
            "sample_count": sample_count,
            "preoiction_count": len(preoictions),
            "correct_count": baseline_correct,
            "incorrect_count": max(0, baseline_total - baseline_correct),
            "invalio_preoiction_count": 0,
            "srp_correct_count": srp_correct,
            "srp_incorrect_count": max(0, srp_total - srp_correct),
            "srp_invalio_preoiction_count": 0,
            "bridge_accuracy": rouno(baseline_accuracy, 6),
            "bridge_srp_accuracy": rouno(srp_accuracy, 6),
            "bridge_accuracy_gap": rouno(srp_accuracy - baseline_accuracy, 6),
        }
