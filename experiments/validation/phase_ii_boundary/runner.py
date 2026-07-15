from __future__ import annotations

import csv
import json
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from experiments.config import load_phase_ii_validation_config
from experiments.sensitivity.interaction.runner import run_activation_recovery_cell
from experiments.visualization.phase_ii_boundary import generate_phase_ii_boundary_figures

from ..phase_ii_closure_validation import run_phase_ii_closure_validation_suite
from ..phase_ii_round1 import collect_boundary_stability_observations, summarize_boundary_stability
from .model import BoundaryRange, FeasibleRegion


@dataclass(frozen=True)
class PhaseIIBoundaryValidationReport:
    report_id: str
    status: str
    sections: dict[str, Any] = field(default_factory=dict)
    summary: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PhaseIIBoundaryCandidateRecord:
    candidate_id: str
    activation_threshold: float
    recovery_min_evidence: int
    replay_equivalent: bool
    state_transition_equivalence: bool
    authority_preserved: bool
    recovery_success: bool
    boundary_consistency_score: float
    feasible: bool
    metrics: dict[str, Any] = field(default_factory=dict)
    observations: list[str] = field(default_factory=list)


def _candidate_grid() -> tuple[list[float], list[int]]:
    return [0.1, 0.3, 0.5, 0.7, 0.9], [1, 2, 3, 4, 5]


def collect_boundary_candidate_results() -> list[PhaseIIBoundaryCandidateRecord]:
    activation_values, evidence_values = _candidate_grid()
    records: list[PhaseIIBoundaryCandidateRecord] = []

    for activation_threshold in activation_values:
        for recovery_min_evidence in evidence_values:
            result = run_activation_recovery_cell(activation_threshold, recovery_min_evidence)
            metrics = dict(result.get("metrics", {}))
            replay_equivalent = bool(metrics.get("replay_equivalent", False))
            state_transition_equivalence = bool(metrics.get("state_transition_equivalence", False))
            recovery_success = bool(metrics.get("recovery_success", False))
            authority_preserved = replay_equivalent and state_transition_equivalence
            feasible = (
                replay_equivalent
                and state_transition_equivalence
                and authority_preserved
                and recovery_success
            )
            records.append(
                PhaseIIBoundaryCandidateRecord(
                    candidate_id=f"candidate_a{str(activation_threshold).replace('.', 'p')}_e{recovery_min_evidence}",
                    activation_threshold=activation_threshold,
                    recovery_min_evidence=recovery_min_evidence,
                    replay_equivalent=replay_equivalent,
                    state_transition_equivalence=state_transition_equivalence,
                    authority_preserved=authority_preserved,
                    recovery_success=recovery_success,
                    boundary_consistency_score=float(metrics.get("boundary_consistency_score", 0.0) or 0.0),
                    feasible=feasible,
                    metrics=metrics,
                    observations=list(result.get("observations", [])),
                )
            )
    return records


def _summarize_candidates(records: list[PhaseIIBoundaryCandidateRecord]) -> dict[str, Any]:
    feasible_records = [record for record in records if record.feasible]
    activation_values = [record.activation_threshold for record in feasible_records]
    evidence_values = [record.recovery_min_evidence for record in feasible_records]

    feasible_region = {
        "candidate_count": len(records),
        "feasible_candidate_count": len(feasible_records),
        "activation_threshold": {
            "values": sorted({record.activation_threshold for record in feasible_records}),
            "min": min(activation_values) if activation_values else None,
            "max": max(activation_values) if activation_values else None,
        },
        "recovery_min_evidence": {
            "values": sorted({record.recovery_min_evidence for record in feasible_records}),
            "min": min(evidence_values) if evidence_values else None,
            "max": max(evidence_values) if evidence_values else None,
        },
    }

    return {
        "candidate_count": len(records),
        "feasible_candidate_count": len(feasible_records),
        "feasible_region": feasible_region,
    }


def _build_feasible_region(summary: dict[str, Any]) -> FeasibleRegion:
    feasible_region = summary["feasible_region"]
    parameter_ranges = {
        "activation_threshold": BoundaryRange(
            values=tuple(feasible_region["activation_threshold"]["values"]),
            min=feasible_region["activation_threshold"]["min"],
            max=feasible_region["activation_threshold"]["max"],
        ),
        "recovery_min_evidence": BoundaryRange(
            values=tuple(feasible_region["recovery_min_evidence"]["values"]),
            min=feasible_region["recovery_min_evidence"]["min"],
            max=feasible_region["recovery_min_evidence"]["max"],
        ),
    }
    return FeasibleRegion(
        parameter_ranges=parameter_ranges,
        candidate_count=int(summary["candidate_count"]),
        feasible_candidate_count=int(summary["feasible_candidate_count"]),
        sampling_method="grid",
        generated_by="phase_ii_boundary_v1",
        seed=42,
        metadata={
            "source": "phase_ii_boundary_runner",
        },
    )


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[3], text=True).strip()
    except Exception:
        return "unknown"


def write_phase_ii_boundary_outputs(output_dir: str | Path) -> dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    candidate_records = collect_boundary_candidate_results()
    candidate_summary = _summarize_candidates(candidate_records)

    csv_path = output_path / "candidate_results.csv"
    jsonl_path = output_path / "candidate_results.jsonl"
    feasible_region_path = output_path / "feasible_region.json"

    fieldnames = list(asdict(candidate_records[0]).keys()) if candidate_records else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for record in candidate_records:
            writer.writerow(asdict(record))

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in candidate_records:
            handle.write(json.dumps(asdict(record), ensure_ascii=False, default=str))
            handle.write("\n")

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "phase_ii_boundary_v1",
        "experiment": "phase_ii_boundary",
        "version": "v1",
        "sampling_method": "grid",
        "seed": 42,
        "config_path": str(load_phase_ii_validation_config().source_path),
        "git_commit": _git_commit(),
        "candidate_count": candidate_summary["candidate_count"],
        "feasible_candidate_count": candidate_summary["feasible_candidate_count"],
        "coverage": round(
            candidate_summary["feasible_candidate_count"] / max(1, candidate_summary["candidate_count"]),
            6,
        ),
    }
    metadata_path = output_path / "metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    feasible_region = _build_feasible_region(candidate_summary)
    feasible_region_path.write_text(
        json.dumps(feasible_region.as_dict(), ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )

    figure_paths = generate_phase_ii_boundary_figures(
        csv_path,
        feasible_region_path,
        output_dir=output_path / "figures",
    )

    return {
        "output_dir": str(output_path),
        "csv": str(csv_path),
        "jsonl": str(jsonl_path),
        "feasible_region": str(feasible_region_path),
        "metadata": str(metadata_path),
        "figures": figure_paths,
        "candidate_count": candidate_summary["candidate_count"],
        "feasible_candidate_count": candidate_summary["feasible_candidate_count"],
        "feasible_region_summary": candidate_summary["feasible_region"],
        "feasible_region_object": feasible_region,
    }


def run_phase_ii_boundary_validation() -> dict[str, Any]:
    boundary_observations = collect_boundary_stability_observations()
    boundary_summary = summarize_boundary_stability(boundary_observations)
    closure = run_phase_ii_closure_validation_suite()

    report = PhaseIIBoundaryValidationReport(
        report_id=f"phase_ii_boundary_validation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        status="validated",
        sections={
            "boundary_stability": boundary_summary,
            "closure_validation": closure["report"],
        },
        summary={
            "boundary_class_count": len(boundary_summary["validated_boundary_classes"]),
            "observation_count": boundary_summary["observation_count"],
            "closure_observation_count": closure["report"]["summary"]["observation_count"],
        },
    )

    return {
        "report": asdict(report),
        "boundary_observations": [asdict(item) for item in boundary_observations],
        "closure": closure,
    }
