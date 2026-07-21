from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPrediction, BenchmarkRunConfig
from experiments.benchmarks.common.safety import assert_no_prompt_leakage


FORBIDDEN_CODE_CONTEXT_KEYS: tuple[str, ...] = (
    "reference_solution",
    "canonical_solution",
    "test_specification",
    "test_code",
    "hidden_test",
    "hidden_tests",
    "solution",
    "gold_solution",
)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


def _hash_text(value: Any) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def _load_records_from_path(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix.lower() == ".jsonl":
        records: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            raw = line.strip()
            if not raw:
                continue
            payload = json.loads(raw)
            if isinstance(payload, dict):
                records.append(payload)
        return records
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("tasks"), list):
            return [item for item in payload["tasks"] if isinstance(item, dict)]
        if isinstance(payload.get("data"), list):
            return [item for item in payload["data"] if isinstance(item, dict)]
        return [payload]
    return []


def _parse_hf_data_root(data_root: str | Path | None) -> tuple[str, str] | None:
    raw = str(data_root or "").strip()
    if not raw.startswith("hf:"):
        return None
    spec = raw[3:]
    parts = [part.strip() for part in spec.split("|") if part.strip()]
    if not parts:
        return None
    dataset_id = parts[0]
    split = "test"
    if len(parts) >= 2 and parts[1]:
        split = parts[1]
    return dataset_id, split


class HumanEvalAdapter:
    name = "humaneval"

    def load_dataset(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[dict[str, Any]]:
        root = Path(data_root) if data_root else Path(__file__).resolve().parents[3] / "data" / "external" / "humaneval"
        candidates = []
        if root.is_file():
            candidates.append(root)
        else:
            candidates.extend(
                [
                    root / "humaneval.jsonl",
                    root / "humaneval.json",
                    root / "tasks.jsonl",
                    root / "tasks.json",
                    root / "samples.jsonl",
                    root / "samples.json",
                ]
            )
        records: list[dict[str, Any]] = []
        for candidate in candidates:
            records = _load_records_from_path(candidate)
            if records:
                break
        if not records:
            hf_spec = _parse_hf_data_root(data_root)
            if hf_spec is not None:
                dataset_id, split = hf_spec
                try:
                    from datasets import load_dataset
                except Exception as exc:  # pragma: no cover - dependency guard
                    raise RuntimeError("datasets package is required for HF-backed HumanEval loading") from exc
                loaded = load_dataset(dataset_id, split=split)
                for record in loaded:
                    payload = dict(record)
                    records.append(payload)
        if sample_limit is not None and sample_limit >= 0:
            return records[:sample_limit]
        return records

    def _normalize_task(self, record: dict[str, Any], index: int) -> dict[str, Any]:
        task_id = str(record.get("task_id", record.get("id", record.get("case_id", f"humaneval_{index}"))))
        prompt = str(record.get("prompt", record.get("question", record.get("problem", "")))).strip()
        entry_point = str(record.get("entry_point", record.get("function_name", ""))).strip()
        reference_solution = str(record.get("reference_solution", record.get("canonical_solution", "")))
        test_specification = str(
            record.get("test_specification", record.get("test_code", record.get("test", record.get("tests", ""))))
        )
        public_test = str(record.get("public_test", record.get("visible_tests", "")))
        metadata = {
            "task_id": task_id,
            "entry_point": entry_point,
            "source_index": index,
            "prompt_digest": _hash_text(prompt),
            "reference_solution_digest": _hash_text(reference_solution) if reference_solution else "",
            "test_specification_digest": _hash_text(test_specification) if test_specification else "",
            "public_test_digest": _hash_text(public_test) if public_test else "",
            "task_source": str(record.get("source", record.get("dataset", "external"))),
            "record_type": str(record.get("record_type", "humaneval_task")),
            "test_specification": test_specification,
            "reference_solution": reference_solution,
            "public_test": public_test,
        }
        srp_input_context = dict(record.get("srp_input_context", {})) or {
            "task_id": task_id,
            "entry_point": entry_point,
            "task_source": metadata["task_source"],
        }
        srp_recovered_context = dict(record.get("srp_recovered_context", {})) or {
            "task_id": task_id,
            "entry_point": entry_point,
            "task_source": metadata["task_source"],
            "execution_policy": "subprocess_isolation_v1",
        }
        return {
            "task_id": task_id,
            "prompt": prompt,
            "entry_point": entry_point,
            "reference_solution": reference_solution,
            "test_specification": test_specification,
            "public_test": public_test,
            "metadata": metadata,
            "srp_input_context": srp_input_context,
            "srp_recovered_context": srp_recovered_context,
        }

    def create_cases(
        self,
        dataset: Sequence[Any],
        config: BenchmarkRunConfig | None = None,
    ) -> list[BenchmarkCase]:
        cases: list[BenchmarkCase] = []
        for index, record in enumerate(dataset):
            if not isinstance(record, dict):
                continue
            normalized = self._normalize_task(record, index)
            cases.append(
                BenchmarkCase(
                    benchmark_name=self.name,
                    case_id=normalized["task_id"],
                    prompt=normalized["prompt"],
                    reference_answer="",
                    expected_answer="",
                    choices=(),
                    srp_input_context=normalized["srp_input_context"],
                    srp_recovered_context=normalized["srp_recovered_context"],
                    metadata={
                        **normalized["metadata"],
                        "entry_point": normalized["entry_point"],
                        "public_test": normalized["public_test"],
                        "test_specification": normalized["metadata"].get("test_specification", ""),
                    },
                )
            )
        return cases

    def build_prompt(
        self,
        case: BenchmarkCase,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> str:
        lines = []
        if variant == "srp" and case.srp_recovered_context:
            lines.append("Recovered semantic context:")
            for key in sorted(case.srp_recovered_context.keys()):
                lines.append(f"- {key}: {case.srp_recovered_context[key]}")
            lines.append("")
        lines.append(case.prompt.strip())
        lines.append("")
        entry_point = str(case.metadata.get("entry_point", "")).strip()
        if entry_point:
            lines.append(f"Implement the function: {entry_point}")
        lines.append("Return only the final Python code.")
        return "\n".join(lines).strip()

    def validate_prompt_leakage(
        self,
        case: BenchmarkCase,
        variant: str,
        prompt: str,
        config: BenchmarkRunConfig | None = None,
    ) -> None:
        context = case.srp_recovered_context if variant == "srp" else case.srp_input_context
        assert_no_prompt_leakage(
            prompt,
            context=context,
            forbidden_context_keys=FORBIDDEN_CODE_CONTEXT_KEYS,
            forbidden_prompt_markers=(
                "reference_solution:",
                "canonical_solution:",
                "test_specification:",
                "test_code:",
                "hidden_test:",
                "hidden_tests:",
            ),
        )

    def extract_code(self, prediction: str) -> tuple[str, str]:
        text = str(prediction or "").strip()
        if not text:
            return "", "empty"
        fenced = re.findall(r"```(?:python)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
        if fenced:
            return fenced[0].strip(), "fenced"
        if "```" in text:
            fragments = [part.strip() for part in text.split("```") if part.strip()]
            if fragments:
                return fragments[0], "fenced"
        return text, "raw"

    def evaluate_execution(
        self,
        case: BenchmarkCase,
        *,
        extraction_status: str,
        generated_code: str,
        execution_result: dict[str, Any],
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        passed = bool(execution_result.get("passed"))
        failure_category = execution_result.get("failure_category")
        failure_message = execution_result.get("failure_message")
        return {
            "passed": passed,
            "score": 1.0 if passed else 0.0,
            "is_correct": passed,
            "metric_name": "pass@1",
            "failure_category": failure_category,
            "failure_message": failure_message,
            "extraction_status": extraction_status,
            "generated_code_digest": _hash_text(generated_code) if generated_code else "",
            "execution_time_seconds": execution_result.get("execution_time_seconds", 0.0),
        }

    def evaluate_prediction(
        self,
        case: BenchmarkCase,
        prediction: str,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        return {
            "passed": False,
            "score": 0.0,
            "is_correct": False,
            "metric_name": "pass@1",
            "prediction_digest": _hash_text(prediction) if prediction else "",
        }

    def summarize_metrics(
        self,
        predictions: Sequence[BenchmarkPrediction],
        cases: Sequence[BenchmarkCase] | None = None,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        by_variant: dict[str, list[BenchmarkPrediction]] = {}
        for prediction in predictions:
            by_variant.setdefault(prediction.variant, []).append(prediction)

        baseline_records = by_variant.get("baseline", [])
        srp_records = by_variant.get("srp", [])

        def _count(records: Sequence[BenchmarkPrediction], predicate) -> int:
            return sum(1 for record in records if predicate(record))

        baseline_passed = _count(baseline_records, lambda rec: rec.is_correct is True)
        srp_passed = _count(srp_records, lambda rec: rec.is_correct is True)
        baseline_total = len(baseline_records)
        srp_total = len(srp_records)
        baseline_pass_at_1 = baseline_passed / float(baseline_total) if baseline_total else 0.0
        srp_pass_at_1 = srp_passed / float(srp_total) if srp_total else 0.0
        failure_categories: dict[str, int] = {}
        execution_failure_count = 0
        syntax_error_count = 0
        runtime_error_count = 0
        timeout_count = 0
        sandbox_error_count = 0
        for prediction in predictions:
            evaluation = dict(prediction.metadata.get("evaluation") or {})
            category = str(evaluation.get("failure_category") or prediction.error or "").strip()
            if category:
                failure_categories[category] = failure_categories.get(category, 0) + 1
                if category in {"syntax_error", "runtime_error", "timeout", "sandbox_error", "failed_assertion"}:
                    execution_failure_count += 1
                if category == "syntax_error":
                    syntax_error_count += 1
                elif category == "runtime_error":
                    runtime_error_count += 1
                elif category == "timeout":
                    timeout_count += 1
                elif category == "sandbox_error":
                    sandbox_error_count += 1

        return {
            "metric_schema": {
                **BenchmarkMetricsSchema(
                    primary_metric_name="pass@1",
                    primary_metric_definition="passed executions divided by total evaluated executions",
                ).as_dict(),
                "primary_metric_name": "pass@1",
            },
            "pass@1": round(baseline_pass_at_1, 6),
            "baseline_pass@1": round(baseline_pass_at_1, 6),
            "srp_pass@1": round(srp_pass_at_1, 6),
            "pass@1_gap": round(srp_pass_at_1 - baseline_pass_at_1, 6),
            "sample_count": len(cases or ()),
            "prediction_count": len(predictions),
            "passed_tasks": baseline_passed,
            "failed_tasks": baseline_total - baseline_passed,
            "baseline_passed_tasks": baseline_passed,
            "srp_passed_tasks": srp_passed,
            "execution_failure_count": execution_failure_count,
            "syntax_error_count": syntax_error_count,
            "runtime_error_count": runtime_error_count,
            "timeout_count": timeout_count,
            "sandbox_error_count": sandbox_error_count,
            "failure_categories": failure_categories,
            "baseline_count": baseline_total,
            "srp_count": srp_total,
            "variant_counts": {"baseline": baseline_total, "srp": srp_total},
        }
