from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Iterable

from srp_runtime.config import load_default_profile

from experiments.visualization.phase_i_observability import generate_phase_i_observability_figures

from .archive_relations_experiment import run_archive_relations_sensitivity
from .preserve_evidence_experiment import run_preserve_evidence_sensitivity
from .recovery_min_evidence_experiment import run_recovery_min_evidence_sensitivity
from .runner import run_activation_threshold_sensitivity


@dataclass(frozen=True)
class PhaseIObservabilityRecord:
    observability_id: str
    parameter: str
    value: Any
    baseline_value: Any
    repeat_index: int
    scenario_label: str
    parameter_drift: float
    successful_transitions: int
    replay_equivalent: bool
    runtime_event_count: int
    final_activation: float | None
    state_consistency: float
    timestamp: str
    observations: list[str]


def _default_profile_values() -> dict[str, Any]:
    return asdict(load_default_profile())


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2], text=True).strip()
    except Exception:
        return "unknown"


def _parameter_drift(parameter: str, value: Any, defaults: dict[str, Any]) -> float:
    baseline_value = defaults.get(parameter)
    if isinstance(value, bool):
        return 0.0 if bool(value) == bool(baseline_value) else 1.0
    if isinstance(value, (int, float)) and isinstance(baseline_value, (int, float)):
        try:
            if parameter == "recovery_min_evidence":
                return float(abs(int(value) - int(baseline_value)))
            return float(abs(float(value) - float(baseline_value)))
        except (TypeError, ValueError):
            return 0.0
    return 0.0


def _state_consistency(replay_equivalent: bool, successful_transitions: int, runtime_event_count: int) -> float:
    if runtime_event_count <= 0:
        return 0.0
    return 1.0 if replay_equivalent and successful_transitions > 0 else 0.0


def _dense_activation_values() -> list[float]:
    return [
        0.10,
        0.15,
        0.20,
        0.25,
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
        0.75,
        0.80,
        0.85,
        0.90,
    ]


def _collect_records(repeat_count: int = 5) -> list[PhaseIObservabilityRecord]:
    defaults = _default_profile_values()
    records: list[PhaseIObservabilityRecord] = []

    for repeat_index in range(1, repeat_count + 1):
        experiment_outputs = [
            ("activation_threshold", f"repeat_{repeat_index}", run_activation_threshold_sensitivity(_dense_activation_values())),
            ("recovery_min_evidence", f"repeat_{repeat_index}", run_recovery_min_evidence_sensitivity([1, 2, 3, 4, 5])),
            ("preserve_evidence", f"repeat_{repeat_index}", run_preserve_evidence_sensitivity([True, False])),
            ("archive_relations", f"repeat_{repeat_index}", run_archive_relations_sensitivity([False, True])),
        ]

        for _, scenario_label, output in experiment_outputs:
            for result in output["results"]:
                parameter = str(result["parameter"])
                value = result["value"]
                metrics = dict(result.get("metrics", {}))
                successful_transitions = int(metrics.get("successful_transitions", 0) or 0)
                replay_equivalent = bool(metrics.get("replay_equivalent", False))
                runtime_event_count = int(metrics.get("runtime_event_count", 0) or 0)
                drift = _parameter_drift(parameter, value, defaults)
                records.append(
                    PhaseIObservabilityRecord(
                        observability_id=f"phase_i:{repeat_index}:{parameter}:{str(value).lower()}",
                        parameter=parameter,
                        value=value,
                        baseline_value=defaults.get(parameter),
                        repeat_index=repeat_index,
                        scenario_label=scenario_label,
                        parameter_drift=drift,
                        successful_transitions=successful_transitions,
                        replay_equivalent=replay_equivalent,
                        runtime_event_count=runtime_event_count,
                        final_activation=metrics.get("final_activation"),
                        state_consistency=_state_consistency(replay_equivalent, successful_transitions, runtime_event_count),
                        timestamp=str(result.get("timestamp", datetime.now(timezone.utc).isoformat())),
                        observations=list(result.get("observations", [])),
                    )
                )

    return records


def _summarize(records: list[PhaseIObservabilityRecord]) -> dict[str, Any]:
    grouped: dict[str, list[PhaseIObservabilityRecord]] = {}
    for record in records:
        grouped.setdefault(record.parameter, []).append(record)

    axes: dict[str, Any] = {}
    for parameter, items in grouped.items():
        drift_values = [item.parameter_drift for item in items]
        axes[parameter] = {
            "observation_count": len(items),
            "replay_success_rate": mean([1.0 if item.replay_equivalent else 0.0 for item in items]),
            "state_consistency_rate": mean([item.state_consistency for item in items]),
            "mean_parameter_drift": mean(drift_values),
            "median_parameter_drift": median(drift_values),
            "std_parameter_drift": pstdev(drift_values) if len(drift_values) > 1 else 0.0,
            "p25_parameter_drift": sorted(drift_values)[max(0, int(len(drift_values) * 0.25) - 1)] if drift_values else 0.0,
            "p75_parameter_drift": sorted(drift_values)[max(0, int(len(drift_values) * 0.75) - 1)] if drift_values else 0.0,
            "max_parameter_drift": max(drift_values),
            "mean_runtime_event_count": mean([float(item.runtime_event_count) for item in items]),
        }

    total_observations = len(records)
    replay_success_rate = mean([1.0 if item.replay_equivalent else 0.0 for item in records]) if records else 0.0
    state_consistency_rate = mean([item.state_consistency for item in records]) if records else 0.0
    drift_values = [item.parameter_drift for item in records]
    mean_parameter_drift = mean(drift_values) if drift_values else 0.0
    median_parameter_drift = median(drift_values) if drift_values else 0.0
    std_parameter_drift = pstdev(drift_values) if len(drift_values) > 1 else 0.0
    p25_parameter_drift = sorted(drift_values)[max(0, int(len(drift_values) * 0.25) - 1)] if drift_values else 0.0
    p75_parameter_drift = sorted(drift_values)[max(0, int(len(drift_values) * 0.75) - 1)] if drift_values else 0.0
    max_parameter_drift = max(drift_values, default=0.0)

    return {
        "status": "observed",
        "observed_parameter_count": len(grouped),
        "repeat_count": len({record.repeat_index for record in records}),
        "transition_count": total_observations,
        "replay_success_rate": replay_success_rate,
        "state_consistency_rate": state_consistency_rate,
        "mean_parameter_drift": mean_parameter_drift,
        "median_parameter_drift": median_parameter_drift,
        "std_parameter_drift": std_parameter_drift,
        "p25_parameter_drift": p25_parameter_drift,
        "p75_parameter_drift": p75_parameter_drift,
        "max_parameter_drift": max_parameter_drift,
        "axes": axes,
    }


def _render_markdown(
    summary: dict[str, Any],
    records: list[PhaseIObservabilityRecord],
    figure_paths: dict[str, Any] | None = None,
) -> str:
    lines = [
        "# SRP Phase I Observability Report",
        "",
        "This report freezes the Phase I parameter observability evidence package for SRP.",
        "It is a data report, not a calibration artifact and not an optimization artifact.",
        "",
        "## Summary",
        "",
        f"- observed parameter count: `{summary['observed_parameter_count']}`",
        f"- repeat count: `{summary['repeat_count']}`",
        f"- transition count: `{summary['transition_count']}`",
        f"- replay success rate: `{summary['replay_success_rate']:.4f}`",
        f"- state consistency rate: `{summary['state_consistency_rate']:.4f}`",
        f"- mean parameter drift: `{summary['mean_parameter_drift']:.4f}`",
        f"- median parameter drift: `{summary['median_parameter_drift']:.4f}`",
        f"- parameter drift std: `{summary['std_parameter_drift']:.4f}`",
        f"- parameter drift p25: `{summary['p25_parameter_drift']:.4f}`",
        f"- parameter drift p75: `{summary['p75_parameter_drift']:.4f}`",
        f"- max parameter drift: `{summary['max_parameter_drift']:.4f}`",
        "",
        "## Metric Definitions",
        "",
        "- `parameter drift` is the absolute difference from the frozen default profile; boolean values use `0/1` encoding.",
        "- `replay success` is reported when the direct and replayed transition paths produce the same state signature.",
        "",
        "## Observed Axes",
        "",
    ]

    for parameter, axis_summary in summary["axes"].items():
        lines.extend(
            [
                f"### {parameter}",
                "",
                f"- observation count: `{axis_summary['observation_count']}`",
                f"- replay success rate: `{axis_summary['replay_success_rate']:.4f}`",
                f"- state consistency rate: `{axis_summary['state_consistency_rate']:.4f}`",
                f"- mean parameter drift: `{axis_summary['mean_parameter_drift']:.4f}`",
                f"- median parameter drift: `{axis_summary['median_parameter_drift']:.4f}`",
                f"- parameter drift std: `{axis_summary['std_parameter_drift']:.4f}`",
                f"- max parameter drift: `{axis_summary['max_parameter_drift']:.4f}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Result Interpretation",
            "",
            "SRP establishes an observable parameter space that can be measured before validation or optimization.",
            "The export uses repeated observations over a dense parameter grid so the observability layer is machine-readable rather than a smoke test.",
            "",
        ]
    )

    if figure_paths is not None:
        lines.extend(
            [
                "## Figures",
                "",
                f"- observation frequency: `{figure_paths['observation_frequency_png']}`",
                f"- drift histogram: `{figure_paths['drift_histogram_png']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Record Count",
            "",
            f"- records exported: `{len(records)}`",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_phase_i_observability_outputs(output_dir: str | Path, *, repeat_count: int = 5) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    records = _collect_records(repeat_count=repeat_count)
    summary = _summarize(records)

    jsonl_path = output_path / "transition_log.jsonl"
    csv_path = output_path / "observability_metrics.csv"
    stats_path = output_path / "parameter_statistics.json"
    metadata_path = output_path / "metadata.json"
    report_path = output_path / "observability_report.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False, default=str))
            handle.write("\n")

    fieldnames = list(asdict(records[0]).keys()) if records else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))

    stats_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "phase_i_observability_v1",
        "experiment": "phase_i_observability",
        "version": "v1",
        "repeat_count": repeat_count,
        "dense_activation_grid_size": 17,
        "git_commit": _git_commit(),
        "runtime_profile": "default_profile",
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    figure_paths = generate_phase_i_observability_figures(csv_path, output_dir=output_path / "figures")
    report_path.write_text(_render_markdown(summary, records, figure_paths), encoding="utf-8")

    return {
        "output_dir": str(output_path),
        "jsonl": str(jsonl_path),
        "csv": str(csv_path),
        "stats": str(stats_path),
        "metadata": str(metadata_path),
        "report": str(report_path),
        "figures": figure_paths,
        "record_count": len(records),
        "summary": summary,
    }
