from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Sequence

from experiments.benchmarks.common import BenchmarkCase, BenchmarkMetricsSchema, BenchmarkPrediction, BenchmarkRunConfig
from experiments.benchmarks.common.safety import assert_no_prompt_leakage


CHOICE_LABELS = ("A", "B", "C", "D", "E", "F")


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def _choice_labels(count: int) -> tuple[str, ...]:
    return CHOICE_LABELS[: max(0, min(count, len(CHOICE_LABELS)))]


def _first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


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
        if isinstance(payload.get("data"), list):
            return [item for item in payload["data"] if isinstance(item, dict)]
        return [payload]
    return []


def _parse_hf_data_root(data_root: str | Path | None) -> tuple[str, tuple[str, ...], str] | None:
    raw = str(data_root or "").strip()
    if not raw.startswith("hf:"):
        return None
    spec = raw[3:]
    parts = [part.strip() for part in spec.split("|") if part.strip()]
    if not parts:
        return None
    dataset_id = parts[0]
    configs: tuple[str, ...] = ()
    split = "validation"
    if len(parts) >= 2 and parts[1]:
        configs = tuple(item.strip() for item in parts[1].split(",") if item.strip())
    if len(parts) >= 3 and parts[2]:
        split = parts[2]
    return dataset_id, configs, split


class MMLUAdapter:
    name = "mmlu"

    def load_dataset(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[dict[str, Any]]:
        root = Path(data_root) if data_root else Path(__file__).resolve().parents[3] / "data" / "mmlu"
        candidates = [
            root / "mmlu.jsonl",
            root / "mmlu.json",
            root / "cases.jsonl",
            root / "cases.json",
            root / "samples.jsonl",
            root / "samples.json",
        ]
        records: list[dict[str, Any]] = []
        for candidate in candidates:
            records = _load_records_from_path(candidate)
            if records:
                break
        if not records:
            hf_spec = _parse_hf_data_root(data_root)
            if hf_spec is not None:
                dataset_id, configs, split = hf_spec
                try:
                    from datasets import load_dataset
                except Exception as exc:  # pragma: no cover - dependency guard
                    raise RuntimeError("datasets package is required for HF-backed MMLU loading") from exc
                if not configs:
                    configs = ("abstract_algebra", "anatomy", "astronomy", "business_ethics", "clinical_knowledge")
                for subject in configs:
                    subject_records = load_dataset(dataset_id, subject, split=split)
                    for record in subject_records:
                        payload = dict(record)
                        payload.setdefault("subject", subject)
                        records.append(payload)
        if sample_limit is not None and sample_limit >= 0:
            return records[:sample_limit]
        return records

    def create_cases(
        self,
        dataset: Sequence[Any],
        config: BenchmarkRunConfig | None = None,
    ) -> list[BenchmarkCase]:
        cases: list[BenchmarkCase] = []
        allowed_subjects = set()
        if config is not None:
            allowed_subjects = {str(subject) for subject in config.execution_parameters.get("subjects", ()) if subject}

        for index, record in enumerate(dataset):
            if not isinstance(record, dict):
                continue
            subject = str(record.get("subject", record.get("category", "")))
            if allowed_subjects and subject and subject not in allowed_subjects:
                continue
            choices = tuple(str(choice) for choice in record.get("choices", []) if str(choice).strip())
            if not choices:
                continue
            labels = _choice_labels(len(choices))
            answer = self.normalize_answer(
                _first_present(record.get("answer"), record.get("answer_key"), record.get("answerKey"), record.get("label")),
                labels,
                choices,
            )
            question = str(record.get("question", record.get("prompt", ""))).strip()
            prompt = self.format_prompt(
                question=question,
                choices=choices,
                subject=subject,
                srp_context={},
                variant="baseline",
            )
            metadata = {
                "subject": subject,
                "split": str(record.get("split", "test")),
                "source_index": index,
                "choice_labels": labels,
                "reference_choice_text": record.get("reference_choice_text", ""),
                "question": question,
            }
            srp_context = dict(record.get("srp_context", {})) or {
                "subject": subject,
                "question": question,
                "choices": choices,
            }
            recovered_context = dict(record.get("recovered_context", {})) or {
                "subject": subject,
                "question": question,
                "choices": choices,
                "choice_labels": labels,
            }
            cases.append(
                BenchmarkCase(
                    benchmark_name=self.name,
                    case_id=str(record.get("id", record.get("case_id", f"mmlu_{index}"))),
                    prompt=question,
                    reference_answer=str(record.get("reference_choice_text", choices[labels.index(answer)] if answer in labels and labels.index(answer) < len(choices) else "")),
                    expected_answer=answer,
                    choices=choices,
                    srp_input_context=srp_context,
                    srp_recovered_context=recovered_context,
                    metadata=metadata,
                )
            )
        return cases

    def format_prompt(
        self,
        question: str,
        choices: Sequence[str],
        subject: str = "",
        srp_context: dict[str, Any] | None = None,
        variant: str = "baseline",
    ) -> str:
        labels = _choice_labels(len(choices))
        lines = []
        if subject:
            lines.append(f"Subject: {subject}")
        if variant == "srp" and srp_context:
            lines.append("Recovered semantic context:")
            for key in sorted(srp_context.keys()):
                lines.append(f"- {key}: {srp_context[key]}")
        lines.append(question.strip())
        lines.append("")
        for label, choice in zip(labels, choices):
            lines.append(f"{label}. {choice}")
        lines.append("")
        lines.append("Answer with the single best choice label only.")
        return "\n".join(lines)

    def build_prompt(
        self,
        case: BenchmarkCase,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> str:
        return self.format_prompt(
            question=case.metadata.get("question", case.prompt),
            choices=case.choices,
            subject=str(case.metadata.get("subject", "")),
            srp_context=case.srp_recovered_context if variant == "srp" else case.srp_input_context,
            variant=variant,
        )

    def validate_prompt_leakage(
        self,
        case: BenchmarkCase,
        variant: str,
        prompt: str,
        config: BenchmarkRunConfig | None = None,
    ) -> None:
        context = case.srp_recovered_context if variant == "srp" else case.srp_input_context
        assert_no_prompt_leakage(prompt, context=context)

    def extract_choice(self, prediction: str, choices: Sequence[str]) -> str | None:
        text = str(prediction).strip()
        if not text:
            return None
        labels = _choice_labels(len(choices))
        upper_text = text.upper()
        for label in labels:
            if re.search(rf"(?<![A-Z]){label}(?![A-Z])", upper_text):
                return label
        normalized_text = _normalize_text(text)
        normalized_choices = {_normalize_text(choice): label for label, choice in zip(labels, choices)}
        if normalized_text in normalized_choices:
            return normalized_choices[normalized_text]
        for label, choice in zip(labels, choices):
            if _normalize_text(choice) and _normalize_text(choice) in normalized_text:
                return label
        return None

    def normalize_answer(
        self,
        answer: Any,
        labels: Sequence[str] | None = None,
        choices: Sequence[str] | None = None,
    ) -> str:
        labels = tuple(labels or CHOICE_LABELS)
        text = str(answer).strip()
        if not text:
            return ""
        upper = text.upper()
        if upper in labels:
            return upper
        if text.isdigit():
            index = int(text)
            if 0 <= index < len(labels):
                return labels[index]
            if 1 <= index <= len(labels):
                return labels[index - 1]
        if choices is not None:
            extracted = self.extract_choice(text, choices)
            if extracted:
                return extracted
        return upper[:1] if upper[:1] in labels else upper

    def evaluate_prediction(
        self,
        case: BenchmarkCase,
        prediction: str,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        predicted_choice = self.extract_choice(prediction, case.choices)
        expected_choice = self.normalize_answer(case.expected_answer, _choice_labels(len(case.choices)), case.choices)
        is_correct = predicted_choice is not None and predicted_choice == expected_choice
        invalid_output = predicted_choice is None
        return {
            "predicted_choice": predicted_choice,
            "expected_choice": expected_choice,
            "is_correct": is_correct,
            "score": 1.0 if is_correct else 0.0,
            "invalid_output": invalid_output,
            "metric_name": "accuracy",
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

        def _count(records: Sequence[BenchmarkPrediction], predicate) -> int:
            return sum(1 for record in records if predicate(record))

        baseline_records = by_variant.get("baseline", [])
        srp_records = by_variant.get("srp", [])
        baseline_correct = _count(baseline_records, lambda rec: rec.is_correct is True)
        baseline_invalid = _count(baseline_records, lambda rec: bool((rec.metadata.get("evaluation") or {}).get("invalid_output")))
        srp_correct = _count(srp_records, lambda rec: rec.is_correct is True)
        srp_invalid = _count(srp_records, lambda rec: bool((rec.metadata.get("evaluation") or {}).get("invalid_output")))

        baseline_total = len(baseline_records)
        srp_total = len(srp_records)
        baseline_accuracy = baseline_correct / float(baseline_total) if baseline_total else 0.0
        srp_accuracy = srp_correct / float(srp_total) if srp_total else 0.0

        return {
            "metric_schema": BenchmarkMetricsSchema().as_dict(),
            "accuracy": round(baseline_accuracy, 6),
            "baseline_accuracy": round(baseline_accuracy, 6),
            "srp_accuracy": round(srp_accuracy, 6),
            "accuracy_gap": round(srp_accuracy - baseline_accuracy, 6),
            "sample_count": len(cases or ()),
            "prediction_count": len(predictions),
            "correct_count": baseline_correct,
            "incorrect_count": max(0, baseline_total - baseline_correct),
            "invalid_output_count": baseline_invalid,
            "srp_correct_count": srp_correct,
            "srp_incorrect_count": max(0, srp_total - srp_correct),
            "srp_invalid_output_count": srp_invalid,
            "official_metric_name": "accuracy",
            "benchmark_name": self.name,
        }
