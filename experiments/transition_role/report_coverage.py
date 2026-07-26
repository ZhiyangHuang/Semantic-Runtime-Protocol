from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .validate_matrix import load_transition_role_matrix, validate_transition_role_matrix
from .validate_registry import load_transition_role_registry, validate_transition_role_registry


@dataclass(slots=True)
class CoverageWorkload:
    source: str
    status: str
    artifact_hint: str = ""
    artifact_exists: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CoverageItem:
    transition_role: str
    purpose: str
    diagnostics: list[str]
    coverage_status: str
    completed_workloads: int
    planned_workloads: int
    workloads: list[CoverageWorkload] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "transition_role": self.transition_role,
            "purpose": self.purpose,
            "diagnostics": list(self.diagnostics),
            "coverage_status": self.coverage_status,
            "completed_workloads": self.completed_workloads,
            "planned_workloads": self.planned_workloads,
            "workloads": [workload.to_dict() for workload in self.workloads],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class CoverageReport:
    schema_version: int
    report_version: str
    protocol_boundary: str
    items: list[CoverageItem]
    summary: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_version": self.report_version,
            "protocol_boundary": self.protocol_boundary,
            "items": [item.to_dict() for item in self.items],
            "summary": dict(self.summary),
        }


def _default_paths() -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parents[2]
    return (
        root / "experiments" / "transition_role" / "registry.yaml",
        root / "experiments" / "transition_role" / "validation_matrix.json",
        root / "experiments" / "results" / "transition_role",
    )


def _artifact_hint(root: Path, role_id: str, source: str) -> Path:
    if source == "locomo":
        return root / role_id / source / "run_latest" / "report.md"
    if source == "longmemeval":
        return root.parent / "external_validation_longmemeval_reality_check_smoke_v2" / "longmemeval_reality_check_report.md"
    return root / role_id / source / "run_latest" / "report.md"


def _build_item(role: dict[str, Any], matrix_rows: list[dict[str, Any]], results_root: Path) -> CoverageItem:
    role_id = str(role.get("id", ""))
    row = next((item for item in matrix_rows if item.get("transition_role") == role_id), None)
    workload_entries = list(row.get("workloaos", [])) if isinstance(row, dict) else []
    completed = sum(1 for entry in workload_entries if str(entry.get("status")) == "complete")
    planned = sum(1 for entry in workload_entries if str(entry.get("status")) != "complete")

    workloads: list[CoverageWorkload] = []
    for entry in workload_entries:
        source = str(entry.get("source", ""))
        status = str(entry.get("status", "planned"))
        hint = _artifact_hint(results_root, role_id, source)
        workloads.append(
            CoverageWorkload(
                source=source,
                status=status,
                artifact_hint=str(hint),
                artifact_exists=hint.exists(),
            )
        )

    if not workload_entries:
        coverage_status = "no_workloads"
    elif planned == 0 and completed > 0:
        coverage_status = "complete"
    elif completed > 0:
        coverage_status = "partial"
    else:
        coverage_status = "planned"

    notes: list[str] = []
    if role_id == "inference_proposal" and not workload_entries:
        notes.append("no compatible workload has been instantiated yet")
    if any(workload.status == "complete" and not workload.artifact_exists for workload in workloads):
        notes.append("a workload is marked complete but no latest artifact was found")

    return CoverageItem(
        transition_role=role_id,
        purpose=str(role.get("purpose", "")),
        diagnostics=list(role.get("diagnostics", [])),
        coverage_status=coverage_status,
        completed_workloads=completed,
        planned_workloads=planned,
        workloads=workloads,
        notes=notes,
    )


def _render_markdown(report: CoverageReport) -> str:
    lines = [
        "# SRP Transition Role Coverage Report",
        "",
        "This report summarizes transition role coverage across semantic workloads.",
        "It is a protocol coverage artifact, not a benchmark ranking.",
        "",
        "## Protocol Boundary",
        "",
        f"- schema_version: `{report.schema_version}`",
        f"- report_version: `{report.report_version}`",
        f"- protocol_boundary: `{report.protocol_boundary}`",
        "",
        "## Summary",
        "",
    ]
    for key, value in report.summary.items():
        lines.append(f"- {key}: `{value}`")
    lines.extend(["", "## Role Coverage", "", "| Role | Status | Completed | Planned | Diagnostics |", "| --- | --- | ---: | ---: | --- |"])
    for item in report.items:
        lines.append(
            f"| `{item.transition_role}` | `{item.coverage_status}` | `{item.completed_workloads}` | "
            f"`{item.planned_workloads}` | `{', '.join(item.diagnostics)}` |"
        )
        for workload in item.workloads:
            lines.append(
                f"  - `{workload.source}`: `{workload.status}` "
                f"(artifact: `{workload.artifact_hint}`, exists: `{workload.artifact_exists}`)"
            )
        for note in item.notes:
            lines.append(f"  - note: {note}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `evidence_update`, `temporal_state_evolution`, and `inference_proposal` currently have instantiated workload slices or bridge artifacts.",
            "- `action_proposal` remains the only planned coverage target.",
            "- The report tracks protocol coverage, not task superiority.",
            "",
        ]
    )
    return "\n".join(lines)


def build_role_coverage_report(
    roles_path: str | Path | None = None,
    matrix_path: str | Path | None = None,
    results_root: str | Path | None = None,
) -> CoverageReport:
    default_roles, default_matrix, default_results = _default_paths()
    roles_file = Path(roles_path) if roles_path is not None else default_roles
    matrix_file = Path(matrix_path) if matrix_path is not None else default_matrix
    results_dir = Path(results_root) if results_root is not None else default_results

    registry_data = load_transition_role_registry(roles_file)
    matrix_data = load_transition_role_matrix(matrix_file)
    validate_transition_role_registry(roles_file)
    validate_transition_role_matrix(matrix_file, roles_file, Path("data/external/registry.json"))

    rows = matrix_data.get("rows", []) if isinstance(matrix_data, dict) else []
    roles = registry_data.get("roles", []) if isinstance(registry_data, dict) else []
    items = [_build_item(role, rows, results_dir) for role in roles if isinstance(role, dict)]

    summary = {
        "role_count": len(items),
        "complete_roles": sum(1 for item in items if item.coverage_status == "complete"),
        "partial_roles": sum(1 for item in items if item.coverage_status == "partial"),
        "planned_roles": sum(1 for item in items if item.coverage_status == "planned"),
        "no_workload_roles": sum(1 for item in items if item.coverage_status == "no_workloads"),
        "completed_workloads": sum(item.completed_workloads for item in items),
        "planned_workloads": sum(item.planned_workloads for item in items),
    }
    return CoverageReport(
        schema_version=1,
        report_version="v1.2-alpha",
        protocol_boundary="transition_role_protocol",
        items=items,
        summary=summary,
    )


def write_role_coverage_report(
    output_dir: str | Path,
    roles_path: str | Path | None = None,
    matrix_path: str | Path | None = None,
    results_root: str | Path | None = None,
) -> dict[str, str]:
    report = build_role_coverage_report(roles_path=roles_path, matrix_path=matrix_path, results_root=results_root)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    json_path = output_path / "role_coverage_report.json"
    markdown_path = output_path / "role_coverage_report.md"
    json_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    markdown_path.write_text(_render_markdown(report), encoding="utf-8")

    return {
        "report_json": str(json_path),
        "report_markdown": str(markdown_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the SRP transition role coverage report.")
    parser.add_argument("--roles", type=Path, default=None, help="Path to experiments/transition_role/registry.yaml")
    parser.add_argument("--matrix", type=Path, default=None, help="Path to experiments/transition_role/validation_matrix.json")
    parser.add_argument("--results-root", type=Path, default=None, help="Path to experiments/results/transition_role")
    parser.add_argument("--output", type=Path, default=None, help="Output directory for the coverage report")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout instead of writing a file")
    args = parser.parse_args(argv)

    report = build_role_coverage_report(args.roles, args.matrix, args.results_root)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2, default=str))
        return 0

    output_dir = args.output or (Path(__file__).resolve().parents[2] / "experiments" / "results" / "transition_role" / "coverage")
    outputs = write_role_coverage_report(output_dir, args.roles, args.matrix, args.results_root)
    print(outputs["report_markdown"])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
