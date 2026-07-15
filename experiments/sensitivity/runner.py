from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Callable, Iterable

from srp_runtime.config import RuntimeConfig, load_default_profile
from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel import RuntimeKernel
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit

from .config import SensitivityExperimentConfig
from .metrics import SensitivityMetrics, metrics_to_dict
from .results import SensitivityResult
from .storage import SensitivityResultStore


def build_baseline_state() -> SemanticState:
    state = SemanticState(state_id="sensitivity:activation", version_id="v0", timestamp_round=1)
    state.units["u1"] = SemanticUnit(
        unit_id="u1",
        canonical_name="alpha",
        semantic_payload={"entity_type": "concept"},
        activation=0.4,
        confidence=0.5,
        version_id="v0",
    )
    return state


def build_activation_event() -> RuntimeEvent:
    return RuntimeEvent(
        event_id="event:sensitivity:activation:1",
        event_type="ActivationUpdate",
        schema_version="1",
        causal_parent=None,
        actor="tester",
        targets=["u1"],
        payload={},
        mutation_mode="update",
        operator_name="ActivationUpdate",
    )


def run_single_activation_threshold_case(value: float, *, baseline: RuntimeConfig | None = None) -> SensitivityResult:
    runtime_config = baseline or load_default_profile()
    runtime_config = RuntimeConfig(**{**asdict(runtime_config), "activation_threshold": value})
    kernel = RuntimeKernel(state=build_baseline_state(), config=None)
    kernel._config.runtime_config = runtime_config
    kernel._activation_operator.runtime_config = runtime_config
    transition = kernel.apply_event(build_activation_event())
    metrics = SensitivityMetrics(
        successful_transitions=1 if transition.success else 0,
        replay_equivalent=True,
        runtime_event_count=len(kernel.event_stream),
        final_activation=kernel._state.units["u1"].activation if "u1" in kernel._state.units else None,
    )
    observations = [
        f"activation_threshold={value}",
        f"transition_success={transition.success}",
        f"final_activation={metrics.final_activation}",
    ]
    return SensitivityResult(
        experiment_id=f"activation_threshold_{str(value).replace('.', 'p')}",
        baseline_version="default",
        timestamp=datetime.now(timezone.utc).isoformat(),
        parameter="activation_threshold",
        value=value,
        metrics=metrics_to_dict(metrics),
        observations=observations,
    )


def run_activation_threshold_sensitivity(
    values: Iterable[float] | None = None,
    *,
    store: SensitivityResultStore | None = None,
) -> dict[str, Any]:
    candidate_values = list(values) if values is not None else [0.1, 0.2, 0.3, 0.4, 0.5]
    config = SensitivityExperimentConfig(
        parameter="activation_threshold",
        values=candidate_values,
        baseline="default",
        scenario="activation_update",
        dataset="fixed_kernel_state",
    )
    results = [run_single_activation_threshold_case(value) for value in candidate_values]
    stored_paths = []
    if store is not None:
        stored_paths = [str(store.save(result)) for result in results]
    return {
        "experiment": {
            "parameter": config.parameter,
            "values": list(config.values),
            "baseline": config.baseline,
            "scenario": config.scenario,
            "dataset": config.dataset,
        },
        "results": [asdict(result) for result in results],
        "stored_paths": stored_paths,
    }
