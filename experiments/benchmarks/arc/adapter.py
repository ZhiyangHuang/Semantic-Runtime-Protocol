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
    split = "test"
    if len(parts) >= 2 and parts[1]:
        configs = tuple(item.strip() for item in parts[1].split(",") if item.strip())
    if len(parts) >= 3 and parts[2]:
        split = parts[2]
    return dataset_id, configs, split


class ARCAdapter:
    name = "arc"

    def load_dataset(self, data_root: str | Path | None = None, sample_limit: int | None = None) -> list[dict[str, Any]]:
        root = Path(data_root) if data_root else Path(__file__).resolve().parents[3] / "data" / "arc"
        candidates = [
            root / "arc.jsonl",
            root / "arc.json",
            root / "cases.jsonl",
            root / "cases.json",
            root / "arc_easy.jsonl",
            root / "arc_easy.json",
            root / "arc_challenge.jsonl",
            root / "arc_challenge.json",
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
                    raise RuntimeError("datasets package is required for HF-backed ARC loading") from exc
                if not configs:
                    configs = ("ARC-Easy",)
                for subset in configs:
                    subset_records = load_dataset(dataset_id, subset, split=split)
                    for record in subset_records:
                        payload = dict(record)
                        payload.setdefault("subset", subset)
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
        allowed_subsets = set()
        if config is not None:
            allowed_subsets = {str(subset) for subset in config.execution_parameters.get("subsets", ()) if subset}

        for index, record in enumerate(dataset):
            if not isinstance(record, dict):
                continue
            subset = str(record.get("subset", record.get("challenge", record.get("split", ""))))
            if allowed_subsets and subset and subset not in allowed_subsets:
                continue
            raw_choices = record.get("choices", [])
            if isinstance(raw_choices, dict):
                choice_texts = raw_choices.get("text", [])
                choice_labels = raw_choices.get("label", [])
                choices = tuple(str(choice) for choice in choice_texts if str(choice).strip())
                labels = tuple(str(label).strip().upper() for label in choice_labels if str(label).strip())
            else:
                choices = tuple(str(choice) for choice in raw_choices if str(choice).strip())
                labels = _choice_labels(len(choices))
            if not choices:
                continue
            if not labels:
                labels = _choice_labels(len(choices))
            answer = self.normalize_answer(
                _first_present(record.get("answer"), record.get("answerKey"), record.get("answer_key")),
                labels,
                choices,
            )
            question = str(record.get("question", record.get("prompt", ""))).strip()
            metadata = {
                "subset": subset or str(record.get("split", "test")),
                "source_index": index,
                "choice_labels": labels,
                "question": question,
                "challenge": subset,
                "split": str(record.get("split", "test")),
            }
            srp_context = dict(record.get("srp_context", {})) or {
                "subset": subset,
                "question": question,
                "choices": choices,
            }
            recovered_context = dict(record.get("recovered_context", {})) or {
                "subset": subset,
                "question": question,
                "choices": choices,
                "choice_labels": labels,
            }
            if answer in labels and labels.index(answer) < len(choices):
                reference_text = choices[labels.index(answer)]
            else:
                reference_text = str(record.get("reference_choice_text", ""))
            cases.append(
                BenchmarkCase(
                    benchmark_name=self.name,
                    case_id=str(record.get("id", record.get("item_id", record.get("case_id", f"arc_{index}")))),
                    prompt=question,
                    reference_answer=reference_text,
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
        subset: str = "",
        srp_context: dict[str, Any] | None = None,
        variant: str = "baseline",
    ) -> str:
        labels = _choice_labels(len(choices))
        lines = []
        if subset:
            lines.append(f"Subset: {subset}")
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
            subset=str(case.metadata.get("subset", "")),
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
            normalized_choice = _normalize_text(choice)
            if normalized_choice and normalized_choice in normalized_text:
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
        sample_count = len(cases or ())

        return {
            "metric_schema": BenchmarkMetricsSchema().as_dict(),
            "accuracy": round(baseline_accuracy, 6),
            "baseline_accuracy": round(baseline_accuracy, 6),
            "srp_accuracy": round(srp_accuracy, 6),
            "accuracy_gap": round(srp_accuracy - baseline_accuracy, 6),
            "sample_count": sample_count,
            "prediction_count": len(predictions),
            "correct_count": baseline_correct,
            "incorrect_count": max(0, baseline_total - baseline_correct),
            "invalid_prediction_count": baseline_invalid,
            "srp_correct_count": srp_correct,
            "srp_incorrect_count": max(0, srp_total - srp_correct),
            "srp_invalid_prediction_count": srp_invalid,
            "official_metric_name": "accuracy",
            "benchmark_name": self.name,
        }
