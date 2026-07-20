from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .validate_registry import (
    load_transition_role_registry,
    validate_external_registry_consistency,
    validate_transition_role_registry,
)


ALLOWED_STATUSES = {"planned", "complete", "pending"}


@dataclass(slots=True)
class MatrixValidationReport:
    name: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_transition_role_matrix(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("transition role matrix must be a mapping")
    return data


def validate_transition_role_matrix(
    matrix_path: Path,
    transition_role_registry_path: Path,
    external_registry_path: Path,
) -> MatrixValidationReport:
    role_report = validate_transition_role_registry(transition_role_registry_path)
    external_report = validate_external_registry_consistency(external_registry_path, transition_role_registry_path)
    errors = [*role_report.errors, *external_report.errors]
    warnings = [*role_report.warnings, *external_report.warnings]

    if not role_report.valid or not external_report.valid:
        return MatrixValidationReport(
            name="transition_role_matrix",
            valid=False,
            errors=errors,
            warnings=warnings,
            details={
                "matrix_path": str(matrix_path),
                "role_registry_path": str(transition_role_registry_path),
                "external_registry_path": str(external_registry_path),
            },
        )

    role_data = load_transition_role_registry(transition_role_registry_path)
    role_ids = {role["id"] for role in role_data.get("roles", []) if isinstance(role, dict) and "id" in role}
    external_data = json.loads(external_registry_path.read_text(encoding="utf-8"))
    external_sources = {
        source["name"]: source
        for source in external_data.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("name"), str)
    }
    matrix = load_transition_role_matrix(matrix_path)

    rows = matrix.get("rows", [])
    if not isinstance(rows, list) or not rows:
        return MatrixValidationReport(
            name="transition_role_matrix",
            valid=False,
            errors=["matrix rows must be a non-empty list"],
            warnings=warnings,
            details={"matrix_path": str(matrix_path)},
        )

    seen_roles: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("each matrix row must be a mapping")
            continue
        role = row.get("transition_role")
        workloads = row.get("workloads")
        if not isinstance(role, str) or not role.strip():
            errors.append("each matrix row must declare a non-empty transition_role")
            continue
        if role not in role_ids:
            errors.append(f"unknown transition_role in matrix: {role}")
        if role in seen_roles:
            errors.append(f"duplicate transition_role in matrix: {role}")
        seen_roles.add(role)
        if not isinstance(workloads, list) or not workloads:
            errors.append(f"matrix row {role} must declare a non-empty workloads list")
            continue

        for workload in workloads:
            if not isinstance(workload, dict):
                errors.append(f"matrix row {role} contains a non-mapping workload entry")
                continue
            source_name = workload.get("source")
            status = workload.get("status")
            if not isinstance(source_name, str) or not source_name.strip():
                errors.append(f"matrix row {role} contains a workload without a source name")
                continue
            if status not in ALLOWED_STATUSES:
                errors.append(f"matrix row {role} workload {source_name} has invalid status: {status!r}")

            source = external_sources.get(source_name)
            if source is None:
                errors.append(f"matrix workload {source_name} is missing from external registry")
                continue
            if source.get("transition_role") != role:
                errors.append(
                    f"matrix workload {source_name} maps to {source.get('transition_role')} in external registry, expected {role}"
                )

    return MatrixValidationReport(
        name="transition_role_matrix",
        valid=not errors,
        errors=errors,
        warnings=sorted(set(warnings)),
        details={
            "matrix_path": str(matrix_path),
            "role_registry_path": str(transition_role_registry_path),
            "external_registry_path": str(external_registry_path),
            "row_count": len(rows) if isinstance(rows, list) else 0,
        },
    )


def _default_paths() -> tuple[Path, Path, Path]:
    root = Path(__file__).resolve().parents[2]
    return (
        root / "experiments" / "transition_role" / "validation_matrix.json",
        root / "experiments" / "transition_role" / "registry.yaml",
        root / "data" / "external" / "registry.json",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the SRP transition role validation matrix.")
    parser.add_argument("--matrix", type=Path, default=None, help="Path to experiments/transition_role/validation_matrix.json")
    parser.add_argument("--roles", type=Path, default=None, help="Path to experiments/transition_role/registry.yaml")
    parser.add_argument("--external", type=Path, default=None, help="Path to data/external/registry.json")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    default_matrix, default_roles, default_external = _default_paths()
    matrix_path = args.matrix or default_matrix
    roles_path = args.roles or default_roles
    external_path = args.external or default_external

    report = validate_transition_role_matrix(matrix_path, roles_path, external_path)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        print(f"{report.name}: {'PASS' if report.valid else 'FAIL'}")
        for warning in report.warnings:
            print(f"WARN: {warning}")
        for error in report.errors:
            print(f"ERROR: {error}")
    return 0 if report.valid else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
