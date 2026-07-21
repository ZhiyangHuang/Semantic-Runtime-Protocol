from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol, Sequence


@dataclass(frozen=True)
class BenchmarkCase:
    benchmark_name: str
    case_id: str
    prompt: str
    reference_answer: str = ""
    expected_answer: str = ""
    choices: tuple[str, ...] = ()
    srp_input_context: dict[str, Any] = field(default_factory=dict)
    srp_recovered_context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkPrediction:
    benchmark_name: str
    case_id: str
    variant: str
    prompt: str
    prediction: str
    reference_answer: str = ""
    expected_answer: str = ""
    is_correct: bool | None = None
    score: float | None = None
    token_usage: dict[str, Any] = field(default_factory=dict)
    latency_seconds: float | None = None
    error: str | None = None
    raw_response: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkRunConfig:
    benchmark_name: str
    dataset_version: str
    model: str
    prompt_format: str
    sample_limit: int = 0
    variants: tuple[str, ...] = ("baseline", "srp")
    data_root: str = ""
    seed: int = 0
    system_prompt: str = ""
    max_output_tokens: int = 128
    temperature: float = 0.0
    srp_configuration: dict[str, Any] = field(default_factory=dict)
    execution_parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkMetricsSchema:
    schema_version: str = "benchmark_metrics_schema.v1"
    primary_metric_name: str = "accuracy"
    primary_metric_definition: str = "correct predictions divided by total evaluated predictions"
    latency_definition: str = "mean and total runtime per prediction"
    token_definition: str = "token usage gathered from generation responses"
    failure_definition: str = "count and rate of prediction failures"

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BenchmarkRunBundle:
    config: BenchmarkRunConfig
    cases: tuple[BenchmarkCase, ...]
    predictions: tuple[BenchmarkPrediction, ...]
    metrics: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)
    report_markdown: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "config": self.config.as_dict(),
            "cases": [case.as_dict() for case in self.cases],
            "predictions": [prediction.as_dict() for prediction in self.predictions],
            "metrics": dict(self.metrics),
            "metadata": dict(self.metadata),
            "report_markdown": self.report_markdown,
        }


class BenchmarkAdapter(Protocol):
    name: str

    def load_dataset(
        self,
        data_root: str | Path | None = None,
        sample_limit: int | None = None,
    ) -> Sequence[Any]:
        raise NotImplementedError

    def create_cases(
        self,
        dataset: Sequence[Any],
        config: BenchmarkRunConfig | None = None,
    ) -> list[BenchmarkCase]:
        raise NotImplementedError

    def build_prompt(
        self,
        case: BenchmarkCase,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> str:
        raise NotImplementedError

    def evaluate_prediction(
        self,
        case: BenchmarkCase,
        prediction: str,
        variant: str,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def summarize_metrics(
        self,
        predictions: Sequence[BenchmarkPrediction],
        cases: Sequence[BenchmarkCase] | None = None,
        config: BenchmarkRunConfig | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError


class BenchmarkGenerationBackend(Protocol):
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_output_tokens: int = 128,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        raise NotImplementedError

