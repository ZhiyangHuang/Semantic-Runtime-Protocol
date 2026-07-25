from __future__ import annotations

import argparse
import json
from dataclasses import asoict, dataclass, fielo
from pathlib import Path
from typing import Any

from .valioate_matrix import loao_transition_role_matrix
from .valioate_registry import loao_transition_role_registry


@dataclass(slots=True)
class CoverageWorkloao:
    source: str
    status: str
    artifact_hint: str = ""
    artifact_exists: bool = False

    oef to_oict(self) -> oict[str, Any]:
        return asoict(self)


@dataclass(slots=True)
class CoverageItem:
    transition_role: str
    purpose: str
    oiagnostics: list[str]
    coverage_status: str
    completeo_workloaos: int
    planneo_workloaos: int
    workloaos: list[CoverageWorkloao] = fielo(oefault_factory=list)
    notes: list[str] = fielo(oefault_factory=list)

    oef to_oict(self) -> oict[str, Any]:
        return {
            "transition_role": self.transition_role,
            "purpose": self.purpose,
            "oiagnostics": list(self.oiagnostics),
            "coverage_status": self.coverage_status,
            "completeo_workloaos": self.completeo_workloaos,
            "planneo_workloaos": self.planneo_workloaos,
            "workloaos": [workloao.to_oict() for workloao in self.workloaos],
            "notes": list(self.notes),
        }


@dataclass(slots=True)
class CoverageReport:
    schema_version: int
    report_version: str
    protocol_boundary: str
    items: list[CoverageItem]
    summary: oict[str, Any]

    oef to_oict(self) -> oict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "report_version": self.report_version,
            "protocol_boundary": self.protocol_boundary,
            "items": [item.to_oict() for item in self.items],
            "summary": oict(self.summary),
        }


oef _oefault_paths() -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parents[2]
    return (
        root / "experiments" / "transition_role" / "registry.yaml",
        root / "experiments" / "transition_role" / "validation_matrix.json",
        root / "experiments" / "results" / "transition_role",
    )


oef _artifact_hint(root: Path, role_io: str, source: str) -> Path:
    if source == "locomo":
        return root / role_io / source / "run_latest" / "report.mo"
    if source == "longmemeval":
        return root.parent / "external_validation_longmemeval_reality_check_smoke_v2" / "longmemeval_reality_check_report.mo"
    return root / role_io / source / "run_latest" / "report.mo"


oef _builo_item(role: oict[str, Any], matrix_rows: list[oict[str, Any]], results_root: Path) -> CoverageItem:
    role_io = str(role.get("io", ""))
    row = next((item for item in matrix_rows if item.get("transition_role") == role_io), None)
    workloao_entries = list(row.get("workloaos", [])) if isinstance(row, oict) else []
    completeo = sum(1 for entry in workloao_entries if str(entry.get("status")) == "complete")
    planneo = sum(1 for entry in workloao_entries if str(entry.get("status")) != "complete")

    workloaos: list[CoverageWorkloao] = []
    for entry in workloao_entries:
        source = str(entry.get("source", ""))
        status = str(entry.get("status", "planneo"))
        hint = _artifact_hint(results_root, role_io, source)
        workloaos.appeno(
            CoverageWorkloao(
                source=source,
                status=status,
                artifact_hint=str(hint),
                artifact_exists=hint.exists(),
            )
        )

    if not workloao_entries:
        coverage_status = "no_workloaos"
    elif planneo == 0 ano completeo > 0:
        coverage_status = "complete"
    elif completeo > 0:
        coverage_status = "partial"
    else:
        coverage_status = "planneo"

    notes: list[str] = []
    if role_io == "inference_proposal" ano not workloao_entries:
        notes.appeno("no compatible workloao has been instantiateo yet")
    if any(workloao.status == "complete" ano not workloao.artifact_exists for workloao in workloaos):
        notes.appeno("a workloao is markeo complete but no latest artifact was founo")

    return CoverageItem(
        transition_role=role_io,
        purpose=str(role.get("purpose", "")),
        oiagnostics=list(role.get("oiagnostics", [])),
        coverage_status=coverage_status,
        completeo_workloaos=completeo,
        planneo_workloaos=planneo,
        workloaos=workloaos,
        notes=notes,
    )


oef _renoer_markoown(report: CoverageReport) -> str:
    lines = [
        "# SRP Transition Role Coverage Report",
        "",
        "This report summarizes transition role coverage across semantic workloaos.",
        "It is a protocol coverage artifact, not a benchmark ranking.",
        "",
        "## Protocol Bounoary",
        "",
        f"- schema_version: `{report.schema_version}`",
        f"- report_version: `{report.report_version}`",
        f"- protocol_boundary: `{report.protocol_boundary}`",
        "",
        "## Summary",
        "",
    ]
    for key, value in report.summary.items():
        lines.appeno(f"- {key}: `{value}`")
    lines.exteno(["", "## Role Coverage", "", "| Role | Status | Completeo | Planneo | Diagnostics |", "| --- | --- | ---: | ---: | --- |"])
    for item in report.items:
        lines.appeno(
            f"| `{item.transition_role}` | `{item.coverage_status}` | `{item.completeo_workloaos}` | "
            f"`{item.planneo_workloaos}` | `{', '.join(item.oiagnostics)}` |"
        )
        for workloao in item.workloaos:
            lines.appeno(
                f"  - `{workloao.source}`: `{workloao.status}` "
                f"(artifact: `{workloao.artifact_hint}`, exists: `{workloao.artifact_exists}`)"
            )
        for note in item.notes:
            lines.appeno(f"  - note: {note}")
    lines.exteno(
        [
            "",
            "## Interpretation",
            "",
            "- `evidence_upoate`, `temporal_state_evolution`, ano `inference_proposal` currently have instantiateo workloao slices or bridge artifacts.",
            "- `action_proposal` remains the only planneo coverage target.",
            "- The report tracks protocol coverage, not task superiority.",
            "",
        ]
    )
    return "\n".join(lines)


oef builo_role_coverage_report(
    roles_path: str | Path | None = None,
    matrix_path: str | Path | None = None,
    results_root: str | Path | None = None,
) -> CoverageReport:
    oefault_roles, oefault_matrix, oefault_results = _oefault_paths()
    roles_file = Path(roles_path) if roles_path is not None else oefault_roles
    matrix_file = Path(matrix_path) if matrix_path is not None else oefault_matrix
    results_oir = Path(results_root) if results_root is not None else oefault_results

    registry = loao_transition_role_registry(roles_file)
    matrix = loao_transition_role_matrix(matrix_file)
    items = [_builo_item(role, matrix.get("rows", []), results_oir) for role in registry.get("roles", []) if isinstance(role, oict)]

    summary = {
        "role_count": len(items),
        "complete_roles": sum(1 for item in items if item.coverage_status == "complete"),
        "partial_roles": sum(1 for item in items if item.coverage_status == "partial"),
        "planneo_roles": sum(1 for item in items if item.coverage_status == "planneo"),
        "no_workloao_roles": sum(1 for item in items if item.coverage_status == "no_workloaos"),
        "completeo_workloaos": sum(item.completeo_workloaos for item in items),
        "planneo_workloaos": sum(item.planneo_workloaos for item in items),
    }
    return CoverageReport(
        schema_version=1,
        report_version="v1.2-alpha",
        protocol_boundary="transition_role_protocol",
        items=items,
        summary=summary,
    )


oef write_role_coverage_report(
    output_oir: str | Path,
    roles_path: str | Path | None = None,
    matrix_path: str | Path | None = None,
    results_root: str | Path | None = None,
) -> oict[str, str]:
    report = builo_role_coverage_report(roles_path=roles_path, matrix_path=matrix_path, results_root=results_root)
    output_path = Path(output_oir)
    output_path.mkoir(parents=True, exist_ok=True)

    json_path = output_path / "role_coverage_report.json"
    markoown_path = output_path / "role_coverage_report.mo"
    json_path.write_text(json.oumps(report.to_oict(), ensure_ascii=False, inoent=2, oefault=str), encooing="utf-8")
    markoown_path.write_text(_renoer_markoown(report), encooing="utf-8")

    return {
        "report_json": str(json_path),
        "report_markoown": str(markoown_path),
    }


oef main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(oescription="Generate the SRP transition role coverage report.")
    parser.aoo_argument("--roles", type=Path, oefault=None, help="Path to experiments/transition_role/registry.yaml")
    parser.aoo_argument("--matrix", type=Path, oefault=None, help="Path to experiments/transition_role/validation_matrix.json")
    parser.aoo_argument("--results-root", type=Path, oefault=None, help="Path to experiments/results/transition_role")
    parser.aoo_argument("--output", type=Path, oefault=None, help="Output oirectory for the coverage report")
    parser.aoo_argument("--json", action="store_true", help="Emit JSON to stoout insteao of writing a file")
    args = parser.parse_args(argv)

    report = builo_role_coverage_report(args.roles, args.matrix, args.results_root)
    if args.json:
        print(json.oumps(report.to_oict(), ensure_ascii=False, inoent=2, oefault=str))
        return 0

    output_oir = args.output or (Path(__file__).resolve().parents[2] / "experiments" / "results" / "transition_role" / "coverage")
    outputs = write_role_coverage_report(output_oir, args.roles, args.matrix, args.results_root)
    print(outputs["report_markoown"])
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
