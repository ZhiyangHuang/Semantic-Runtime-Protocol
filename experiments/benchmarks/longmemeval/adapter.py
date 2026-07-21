from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPrediction, BenchmarkRunConfig
from experiments.benchmarks.common.safety import assert_no_prompt_leakage
from experiments.external_validation.benchmarks import build_benchmark_adapter as build_external_benchmark_adapter
from experiments.external_validation.schema import (
    BenchmarkCase as ExternalBenchmarkCase,
    SemanticRelation,
    SemanticState,
    SemanticUnit,
)


DEFAULT_LONGMEMEVAL_ROOT = Path(__file__).resolve().parents[3] / "data" / "external" / "longmemeval"


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def _load_json_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _state_summary(state: Any) -> dict[str, Any]:
    units = getattr(state, "units", ())
    relations = getattr(state, "relations", ())
    return {
        "unit_count": len(tuple(units)),
        "relation_count": len(tuple(relations)),
    }


def _state_from_mapping(value: Any) -> SemanticState:
    if isinstance(value, SemanticState):
        return value
    if not isinstance(value, dict):
        return SemanticState()
    units = tuple(
        SemanticUnit(
            unit_id=str(item.get("unit_id", "")),
            kind=str(item.get("kind", "fact")),
            content=str(item.get("content", "")),
            timestep=int(item.get("timestep", 0)),
            salience=float(item.get("salience", 1.0)),
            metadata=dict(item.get("metadata", {})),
        )
        for item in value.get("units", [])
        if isinstance(item, dict)
    )
    relations = tuple(
        SemanticRelation(
            relation_id=str(item.get("relation_id", "")),
            source_id=str(item.get("source_id", "")),
            target_id=str(item.get("target_id", "")),
            relation_type=str(item.get("relation_type", "related_to")),
            confidence=float(item.get("confidence", 1.0)),
            timestep=int(item.get("timestep", 0)),
            metadata=dict(item.get("metadata", {})),
        )
        for item in value.get("relations", [])
        if isinstance(item, dict)
    )
    return SemanticState(units=units, relations=relations, metadata=dict(value.get("metadata", {})))


class LongMemEvalBridgeAdapter:
    name = "longmemeval"

    def __init__(self, data_root: str | Path | None = None) -> None:
        self.data_root = Path(data_root) if data_root else DEFAULT_LONGMEMEVAL_ROOT
        self._manifest = _load_json_file(self.data_root / "manifest.json")
        self._adapter_config = _load_json_file(self.data_root / "adapter_config.json")

    def load_dataset(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[ExternalBenchmarkCase]:
        root = Path(data_root) if data_root else self.data_root
        adapter = build_external_benchmark_adapter("longmemeval")
        cases = list(adapter.load_cases(root, sample_limit=sample_limit))
        if sample_limit is not None and sample_limit >= 0:
            return cases[:sample_limit]
        return cases

    def build_metadata(self, external_case: ExternalBenchmarkCase) -> dict[str, Any]:
        return {
            "bridge": {
                "name": "longmemeval_bridge",
                "version": "bridge_migration_v1",
                "source": "experiments.external_validation",
                "official_scorer": "external_validation",
                "runtime_contract": "external_validation_runtime_contract_v1",
                "payload_policy": "not_stored_in_repository",
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
                "adapter_contract": self._adapter_config.get("adapter_contract", "BoundaryCase"),
                "transition_role": self._adapter_config.get("transition_role", "evidence_update"),
                "input_role": self._adapter_config.get("input_role", "evidence_consistency"),
                "output_role": self._adapter_config.get("output_role", "governance_boundary_case"),
                "benchmark_scoring": bool(self._adapter_config.get("benchmark_scoring", False)),
            },
            "provenance_document": str(self.data_root / "provenance.md"),
            "official_metric_name": external_case.official_metric_name,
            "benchmark_name": external_case.benchmark_name,
            "case_id": external_case.case_id,
            "focus_unit_ids": tuple(external_case.focus_unit_ids),
            "focus_relation_ids": tuple(external_case.focus_relation_ids),
            "source_state_summary": _state_summary(external_case.source_state),
            "target_state_summary": _state_summary(external_case.target_state),
        }

    def normalize_case(self, external_case: ExternalBenchmarkCase, config: BenchmarkRunConfig | None = None) -> BenchmarkCase:
        metadata = self.build_metadata(external_case)
        return BenchmarkCase(
            benchmark_name=external_case.benchmark_name,
            case_id=external_case.case_id,
            prompt=external_case.query,
            reference_answer=external_case.expected_answer,
            expected_answer=external_case.expected_answer,
            choices=(),
            srp_input_context={
                "benchmark_name": external_case.benchmark_name,
                "case_id": external_case.case_id,
                "query": external_case.query,
                "official_metric_name": external_case.official_metric_name,
                "focus_unit_ids": tuple(external_case.focus_unit_ids),
                "focus_relation_ids": tuple(external_case.focus_relation_ids),
                "runtime_contract": metadata["bridge"]["runtime_contract"],
            },
            srp_recovered_context={
                "benchmark_name": external_case.benchmark_name,
                "case_id": external_case.case_id,
                "query": external_case.query,
                "official_scorer": metadata["bridge"]["official_scorer"],
                "official_metric_name": external_case.official_metric_name,
                "bridge_version": metadata["bridge"]["version"],
            },
            metadata=metadata,
        )

    def create_cases(
        self,
        dataset: Sequence[Any],
        config: BenchmarkRunConfig | None = None,
    ) -> list[BenchmarkCase]:
        cases: list[BenchmarkCase] = []
        for record in dataset:
            if isinstance(record, ExternalBenchmarkCase):
                cases.append(self.normalize_case(record, config))
            elif isinstance(record, dict) and "query" in record and "expected_answer" in record:
                # Fallback for serialized bridge inputs in tests or future wrappers.
                external_case = ExternalBenchmarkCase(
                    benchmark_name=str(record.get("benchmark_name", self.name)),
                    case_id=str(record.get("case_id", record.get("id", "longmemeval_case"))),
                    query=str(record.get("query", "")),
                    source_state=_state_from_mapping(record.get("source_state", {})),
                    target_state=_state_from_mapping(record.get("target_state", {})),
                    expected_answer=str(record.get("expected_answer", "")),
                    official_metric_name=str(record.get("official_metric_name", "task_accuracy")),
                    focus_unit_ids=tuple(str(item) for item in record.get("focus_unit_ids", [])),
                    focus_relation_ids=tuple(str(item) for item in record.get("focus_relation_ids", [])),
                    metadata=dict(record.get("metadata", {})),
                )
                cases.append(self.normalize_case(external_case, config))
        if config is not None and config.sample_limit and len(cases) > config.sample_limit:
            return cases[: config.sample_limit]
        return cases

    def build_prompt(
        self,
        case: BenchmarkCase,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> str:
        lines = [
            f"Question: {case.prompt}",
            "",
            "Recovered semantic context:",
        ]
        context = case.srp_recovered_context if variant == "srp" else case.srp_input_context
        if context:
            for key in sorted(context.keys()):
                lines.append(f"- {key}: {context[key]}")
        else:
            lines.append("- none")
        lines.extend(
            [
                "",
                "Answer only with the shortest faithful answer.",
                "Do not add reasoning, caveats, or extra context.",
            ]
        )
        return "\n".join(lines)

    def validate_prompt_leakage(
        self,
        case: BenchmarkCase,
        variant: str,
        prompt: str,
        config: BenchmarkRunConfig | None = None,
    ) -> None:
        context = case.srp_recovered_context if variant == "srp" else case.srp_input_context
        assert_no_prompt_leakage(prompt, context=context)

    def evaluate_prediction(
        self,
        case: BenchmarkCase,
        prediction: str,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        normalized_prediction = _normalize_text(prediction)
        normalized_expected = _normalize_text(case.expected_answer)
        is_correct = normalized_prediction == normalized_expected if normalized_expected else None
        score = 1.0 if is_correct else 0.0 if is_correct is not None else None
        return {
            "predicted_answer": prediction,
            "expected_answer": case.expected_answer,
            "is_correct": is_correct,
            "score": score,
            "metric_name": "bridge_exact_match",
            "official_metric_name": case.metadata.get("official_metric_name", case.expected_answer and "task_accuracy"),
            "scorer_owner": "external_validation",
            "evaluation_mode": "bridge_passthrough",
        }

    def summarize_metrics(
        self,
        predictions: Sequence[BenchmarkPrediction],
        cases: Sequence[BenchmarkCase] | None = None,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        def _count(records: Sequence[BenchmarkPrediction], predicate) -> int:
            return sum(1 for record in records if predicate(record))

        by_variant: dict[str, list[BenchmarkPrediction]] = {}
        for prediction in predictions:
            by_variant.setdefault(prediction.variant, []).append(prediction)

        baseline_records = by_variant.get("baseline", [])
        srp_records = by_variant.get("srp", [])
        baseline_correct = _count(baseline_records, lambda rec: rec.is_correct is True)
        srp_correct = _count(srp_records, lambda rec: rec.is_correct is True)
        baseline_total = len(baseline_records)
        srp_total = len(srp_records)
        baseline_accuracy = baseline_correct / float(baseline_total) if baseline_total else 0.0
        srp_accuracy = srp_correct / float(srp_total) if srp_total else 0.0
        sample_count = len(cases or ())

        return {
            "metric_schema": BenchmarkMetricsSchema().as_dict(),
            "official_metric_name": "task_accuracy",
            "benchmark_name": self.name,
            "sample_count": sample_count,
            "prediction_count": len(predictions),
            "correct_count": baseline_correct,
            "incorrect_count": max(0, baseline_total - baseline_correct),
            "invalid_prediction_count": 0,
            "srp_correct_count": srp_correct,
            "srp_incorrect_count": max(0, srp_total - srp_correct),
            "srp_invalid_prediction_count": 0,
            "bridge_accuracy": round(baseline_accuracy, 6),
            "bridge_srp_accuracy": round(srp_accuracy, 6),
            "bridge_accuracy_gap": round(srp_accuracy - baseline_accuracy, 6),
        }
