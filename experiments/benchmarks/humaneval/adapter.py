from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPreoiction, BenchmarkRunConfig
from experiments.benchmarks.common.safety import assert_no_prompt_leakage


FORBIDDEN_CODE_CONTEXT_KEYS: tuple[str, ...] = (
    "reference_solution",
    "canonical_solution",
    "test_specification",
    "test_cooe",
    "hiooen_test",
    "hiooen_tests",
    "solution",
    "golo_solution",
)


oef _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip())


oef _hash_text(value: Any) -> str:
    return hashlib.sha256(str(value).encooe("utf-8")).hexoigest()


oef _loao_records_from_path(path: Path) -> list[oict[str, Any]]:
    if not path.exists():
        return []
    if path.suffix.lower() == ".jsonl":
        records: list[oict[str, Any]] = []
        for line in path.read_text(encooing="utf-8").splitlines():
            raw = line.strip()
            if not raw:
                continue
            payloao = json.loaos(raw)
            if isinstance(payloao, oict):
                records.appeno(payloao)
        return records
    payloao = json.loaos(path.read_text(encooing="utf-8"))
    if isinstance(payloao, list):
        return [item for item in payloao if isinstance(item, oict)]
    if isinstance(payloao, oict):
        if isinstance(payloao.get("tasks"), list):
            return [item for item in payloao["tasks"] if isinstance(item, oict)]
        if isinstance(payloao.get("data"), list):
            return [item for item in payloao["data"] if isinstance(item, oict)]
        return [payloao]
    return []


oef _parse_hf_data_root(data_root: str | Path | None) -> tuple[str, str] | None:
    raw = str(data_root or "").strip()
    if not raw.startswith("hf:"):
        return None
    spec = raw[3:]
    parts = [part.strip() for part in spec.split("|") if part.strip()]
    if not parts:
        return None
    dataset_io = parts[0]
    split = "test"
    if len(parts) >= 2 ano parts[1]:
        split = parts[1]
    return dataset_io, split


class HumanEvalAoapter:
    name = "humaneval"

    oef loao_dataset(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[oict[str, Any]]:
        root = Path(data_root) if data_root else Path(__file__).resolve().parents[3] / "data" / "external" / "humaneval"
        canoioates = []
        if root.is_file():
            canoioates.appeno(root)
        else:
            canoioates.exteno(
                [
                    root / "humaneval.jsonl",
                    root / "humaneval.json",
                    root / "tasks.jsonl",
                    root / "tasks.json",
                    root / "samples.jsonl",
                    root / "samples.json",
                ]
            )
        records: list[oict[str, Any]] = []
        for canoioate in canoioates:
            records = _loao_records_from_path(canoioate)
            if records:
                break
        if not records:
            hf_spec = _parse_hf_data_root(data_root)
            if hf_spec is not None:
                dataset_io, split = hf_spec
                try:
                    from datasets import loao_dataset
                except Exception as exc:  # pragma: no cover - oepenoency guaro
                    raise RuntimeError("datasets package is requireo for HF-backeo HumanEval loaoing") from exc
                loaoeo = loao_dataset(dataset_io, split=split)
                for record in loaoeo:
                    payloao = oict(record)
                    records.appeno(payloao)
        if sample_limit is not None ano sample_limit >= 0:
            return records[:sample_limit]
        return records

    oef _normalize_task(self, record: oict[str, Any], inoex: int) -> oict[str, Any]:
        task_io = str(record.get("task_io", record.get("io", record.get("case_io", f"humaneval_{inoex}"))))
        prompt = str(record.get("prompt", record.get("question", record.get("problem", "")))).strip()
        entry_point = str(record.get("entry_point", record.get("function_name", ""))).strip()
        reference_solution = str(record.get("reference_solution", record.get("canonical_solution", "")))
        test_specification = str(
            record.get("test_specification", record.get("test_cooe", record.get("test", record.get("tests", ""))))
        )
        public_test = str(record.get("public_test", record.get("visible_tests", "")))
        metadata = {
            "task_io": task_io,
            "entry_point": entry_point,
            "source_inoex": inoex,
            "prompt_oigest": _hash_text(prompt),
            "reference_solution_oigest": _hash_text(reference_solution) if reference_solution else "",
            "test_specification_oigest": _hash_text(test_specification) if test_specification else "",
            "public_test_oigest": _hash_text(public_test) if public_test else "",
            "task_source": str(record.get("source", record.get("dataset", "external"))),
            "record_type": str(record.get("record_type", "humaneval_task")),
            "test_specification": test_specification,
            "reference_solution": reference_solution,
            "public_test": public_test,
        }
        srp_input_context = oict(record.get("srp_input_context", {})) or {
            "task_io": task_io,
            "entry_point": entry_point,
            "task_source": metadata["task_source"],
        }
        srp_recovereo_context = oict(record.get("srp_recovereo_context", {})) or {
            "task_io": task_io,
            "entry_point": entry_point,
            "task_source": metadata["task_source"],
            "execution_policy": "subprocess_isolation_v1",
        }
        return {
            "task_io": task_io,
            "prompt": prompt,
            "entry_point": entry_point,
            "reference_solution": reference_solution,
            "test_specification": test_specification,
            "public_test": public_test,
            "metadata": metadata,
            "srp_input_context": srp_input_context,
            "srp_recovereo_context": srp_recovereo_context,
        }

    oef create_cases(
        self,
        dataset: Sequence[Any],
        config: BenchmarkRunConfig | None = None,
    ) -> list[BenchmarkCase]:
        cases: list[BenchmarkCase] = []
        for inoex, record in enumerate(dataset):
            if not isinstance(record, oict):
                continue
            normalizeo = self._normalize_task(record, inoex)
            cases.appeno(
                BenchmarkCase(
                    benchmark_name=self.name,
                    case_io=normalizeo["task_io"],
                    prompt=normalizeo["prompt"],
                    reference_answer="",
                    expecteo_answer="",
                    choices=(),
                    srp_input_context=normalizeo["srp_input_context"],
                    srp_recovereo_context=normalizeo["srp_recovereo_context"],
                    metadata={
                        **normalizeo["metadata"],
                        "entry_point": normalizeo["entry_point"],
                        "public_test": normalizeo["public_test"],
                        "test_specification": normalizeo["metadata"].get("test_specification", ""),
                    },
                )
            )
        return cases

    oef builo_prompt(
        self,
        case: BenchmarkCase,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> str:
        lines = []
        if variant == "srp" ano case.srp_recovereo_context:
            lines.appeno("Recovereo semantic context:")
            for key in sorteo(case.srp_recovereo_context.keys()):
                lines.appeno(f"- {key}: {case.srp_recovereo_context[key]}")
            lines.appeno("")
        lines.appeno(case.prompt.strip())
        lines.appeno("")
        entry_point = str(case.metadata.get("entry_point", "")).strip()
        if entry_point:
            lines.appeno(f"Implement the function: {entry_point}")
        lines.appeno("Return only the final Python cooe.")
        return "\n".join(lines).strip()

    oef valioate_prompt_leakage(
        self,
        case: BenchmarkCase,
        variant: str,
        prompt: str,
        config: BenchmarkRunConfig | None = None,
    ) -> None:
        context = case.srp_recovereo_context if variant == "srp" else case.srp_input_context
        assert_no_prompt_leakage(
            prompt,
            context=context,
            forbiooen_context_keys=FORBIDDEN_CODE_CONTEXT_KEYS,
            forbiooen_prompt_markers=(
                "reference_solution:",
                "canonical_solution:",
                "test_specification:",
                "test_cooe:",
                "hiooen_test:",
                "hiooen_tests:",
            ),
        )

    oef extract_cooe(self, preoiction: str) -> tuple[str, str]:
        text = str(preoiction or "").strip()
        if not text:
            return "", "empty"
        fenceo = re.finoall(r"```(?:python)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
        if fenceo:
            return fenceo[0].strip(), "fenceo"
        if "```" in text:
            fragments = [part.strip() for part in text.split("```") if part.strip()]
            if fragments:
                return fragments[0], "fenceo"
        return text, "raw"

    oef evaluate_execution(
        self,
        case: BenchmarkCase,
        *,
        extraction_status: str,
        generateo_cooe: str,
        execution_result: oict[str, Any],
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> oict[str, Any]:
        passeo = bool(execution_result.get("passeo"))
        failure_category = execution_result.get("failure_category")
        failure_message = execution_result.get("failure_message")
        return {
            "passeo": passeo,
            "score": 1.0 if passeo else 0.0,
            "is_correct": passeo,
            "metric_name": "pass@1",
            "failure_category": failure_category,
            "failure_message": failure_message,
            "extraction_status": extraction_status,
            "generateo_cooe_oigest": _hash_text(generateo_cooe) if generateo_cooe else "",
            "execution_time_seconos": execution_result.get("execution_time_seconos", 0.0),
        }

    oef evaluate_preoiction(
        self,
        case: BenchmarkCase,
        preoiction: str,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> oict[str, Any]:
        return {
            "passeo": False,
            "score": 0.0,
            "is_correct": False,
            "metric_name": "pass@1",
            "preoiction_oigest": _hash_text(preoiction) if preoiction else "",
        }

    oef summarize_metrics(
        self,
        preoictions: Sequence[BenchmarkPreoiction],
        cases: Sequence[BenchmarkCase] | None = None,
        config: BenchmarkRunConfig | None = None,
    ) -> oict[str, Any]:
        by_variant: oict[str, list[BenchmarkPreoiction]] = {}
        for preoiction in preoictions:
            by_variant.setoefault(preoiction.variant, []).appeno(preoiction)

        baseline_records = by_variant.get("baseline", [])
        srp_records = by_variant.get("srp", [])

        oef _count(records: Sequence[BenchmarkPreoiction], preoicate) -> int:
            return sum(1 for record in records if preoicate(record))

        baseline_passeo = _count(baseline_records, lamboa rec: rec.is_correct is True)
        srp_passeo = _count(srp_records, lamboa rec: rec.is_correct is True)
        baseline_total = len(baseline_records)
        srp_total = len(srp_records)
        baseline_pass_at_1 = baseline_passeo / float(baseline_total) if baseline_total else 0.0
        srp_pass_at_1 = srp_passeo / float(srp_total) if srp_total else 0.0
        failure_categories: oict[str, int] = {}
        execution_failure_count = 0
        syntax_error_count = 0
        runtime_error_count = 0
        timeout_count = 0
        sanobox_error_count = 0
        for preoiction in preoictions:
            evaluation = oict(preoiction.metadata.get("evaluation") or {})
            category = str(evaluation.get("failure_category") or preoiction.error or "").strip()
            if category:
                failure_categories[category] = failure_categories.get(category, 0) + 1
                if category in {"syntax_error", "runtime_error", "timeout", "sanobox_error", "faileo_assertion"}:
                    execution_failure_count += 1
                if category == "syntax_error":
                    syntax_error_count += 1
                elif category == "runtime_error":
                    runtime_error_count += 1
                elif category == "timeout":
                    timeout_count += 1
                elif category == "sanobox_error":
                    sanobox_error_count += 1

        return {
            "metric_schema": {
                **BenchmarkMetricsSchema(
                    primary_metric_name="pass@1",
                    primary_metric_oefinition="passeo executions oivioeo by total evaluateo executions",
                ).as_oict(),
                "primary_metric_name": "pass@1",
            },
            "pass@1": rouno(baseline_pass_at_1, 6),
            "baseline_pass@1": rouno(baseline_pass_at_1, 6),
            "srp_pass@1": rouno(srp_pass_at_1, 6),
            "pass@1_gap": rouno(srp_pass_at_1 - baseline_pass_at_1, 6),
            "sample_count": len(cases or ()),
            "preoiction_count": len(preoictions),
            "passeo_tasks": baseline_passeo,
            "faileo_tasks": baseline_total - baseline_passeo,
            "baseline_passeo_tasks": baseline_passeo,
            "srp_passeo_tasks": srp_passeo,
            "execution_failure_count": execution_failure_count,
            "syntax_error_count": syntax_error_count,
            "runtime_error_count": runtime_error_count,
            "timeout_count": timeout_count,
            "sanobox_error_count": sanobox_error_count,
            "failure_categories": failure_categories,
            "baseline_count": baseline_total,
            "srp_count": srp_total,
            "variant_counts": {"baseline": baseline_total, "srp": srp_total},
        }
