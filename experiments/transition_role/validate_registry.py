from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback parser
    yaml = None

from experiments.validation.boundary_reporting.adapters import ADAPTER_CAPABILITIES, resolve_adapter


ROLE_REQUIRED_LIST_FIELDS = ("invariants", "diagnostics", "workload_requirements")
ROLE_OPTIONAL_LIST_FIELDS = ("compatible_workloads",)


@dataclass(slots=True)
class ValidationReport:
    name: str
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_transition_role_registry(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:  # pragma: no branch - preferred path
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise ValueError("transition role registry must be a mapping")
        return data
    return _parse_transition_role_registry_fallback(text)


def _parse_transition_role_registry_fallback(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lines = text.splitlines()

    def capture_top_level_value(prefix: str) -> str | None:
        for line in lines:
            if line.startswith(prefix):
                value = line.split(":", 1)[1].strip()
                return value if value != ">" else None
        return None

    data["schema_version"] = capture_top_level_value("schema_version:") or ""
    data["registry_version"] = capture_top_level_value("registry_version:") or ""

    purpose_start = None
    for index, line in enumerate(lines):
        if line.startswith("purpose:"):
            purpose_start = index
            break
    if purpose_start is not None:
        purpose_lines: list[str] = []
        for line in lines[purpose_start + 1 :]:
            if line.startswith("roles:"):
                break
            stripped = line.strip()
            if stripped:
                purpose_lines.append(stripped)
        data["purpose"] = " ".join(purpose_lines).strip()

    role_matches = list(re.finditer(r"(?m)^\s*-\s+id:\s*(\S+)\s*$", text))
    roles: list[dict[str, Any]] = []
    for index, match in enumerate(role_matches):
        start = match.start()
        end = role_matches[index + 1].start() if index + 1 < len(role_matches) else len(text)
        block = text[start:end]
        role: dict[str, Any] = {"id": match.group(1)}
        for field in ("purpose", *ROLE_REQUIRED_LIST_FIELDS, *ROLE_OPTIONAL_LIST_FIELDS):
            if field == "purpose":
                if re.search(rf"(?m)^\s+{re.escape(field)}:\s*", block):
                    role[field] = ""
                continue
            role[field] = _extract_yaml_list(block, field)
        roles.append(role)

    data["roles"] = roles
    return data


def _extract_yaml_list(block: str, field: str) -> list[str]:
    if re.search(rf"(?m)^\s{{4}}{re.escape(field)}:\s*\[\]\s*$", block):
        return []
    match = re.search(
        rf"(?ms)^\s{{4}}{re.escape(field)}:\s*$\n(?P<body>(?:^\s{{6}}-\s+.*$\n?)*)",
        block,
    )
    if not match:
        return []
    items: list[str] = []
    for line in match.group("body").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def validate_transition_role_registry(path: Path) -> ValidationReport:
    data = load_transition_role_registry(path)
    errors: list[str] = []
    warnings: list[str] = []

    roles = data.get("roles")
    if not isinstance(roles, list) or not roles:
        return ValidationReport(
            name="transition_role_registry",
            valid=False,
            errors=["roles must be a non-empty list"],
            details={"path": str(path)},
        )

    seen_ids: set[str] = set()
    role_ids: list[str] = []
    for role in roles:
        if not isinstance(role, dict):
            errors.append("each role entry must be a mapping")
            continue
        role_id = role.get("id")
        if not isinstance(role_id, str) or not role_id.strip():
            errors.append("each role must declare a non-empty id")
            continue
        if role_id in seen_ids:
            errors.append(f"duplicate role id: {role_id}")
        seen_ids.add(role_id)
        role_ids.append(role_id)

        purpose = role.get("purpose")
        if not isinstance(purpose, str) or not purpose.strip():
            errors.append(f"role {role_id} must declare a non-empty purpose")

        for field in ROLE_REQUIRED_LIST_FIELDS:
            values = role.get(field)
            if not isinstance(values, list) or not values:
                errors.append(f"role {role_id} must declare a non-empty {field} list")

        compatible_workloads = role.get("compatible_workloads")
        if not isinstance(compatible_workloads, list):
            errors.append(f"role {role_id} must declare compatible_workloads as a list")
        elif not compatible_workloads:
            warnings.append(f"role {role_id} has no compatible workloads yet")

    return ValidationReport(
        name="transition_role_registry",
        valid=not errors,
        errors=errors,
        warnings=warnings,
        details={"path": str(path), "role_ids": role_ids},
    )


def validate_external_registry_consistency(
    external_registry_path: Path,
    transition_role_registry_path: Path,
) -> ValidationReport:
    role_report = validate_transition_role_registry(transition_role_registry_path)
    errors = list(role_report.errors)
    warnings = list(role_report.warnings)

    if not role_report.valid:
        return ValidationReport(
            name="external_registry_consistency",
            valid=False,
            errors=errors,
            warnings=warnings,
            details={"path": str(external_registry_path), "role_registry_path": str(transition_role_registry_path)},
        )

    role_ids = set(role_report.details.get("role_ids", []))
    external_data = json.loads(external_registry_path.read_text(encoding="utf-8"))
    sources = external_data.get("sources", [])
    if not isinstance(sources, list) or not sources:
        errors.append("external registry must contain a non-empty sources list")
        return ValidationReport(
            name="external_registry_consistency",
            valid=False,
            errors=errors,
            warnings=warnings,
            details={"path": str(external_registry_path), "role_registry_path": str(transition_role_registry_path)},
        )

    source_names: list[str] = []
    transition_roles: list[str] = []
    unresolved_adapters: list[str] = []
    unknown_roles: list[str] = []
    for source in sources:
        if not isinstance(source, dict):
            errors.append("each external source entry must be a mapping")
            continue
        source_name = source.get("name")
        adapter_name = source.get("adapter")
        transition_role = source.get("transition_role")
        if isinstance(source_name, str):
            source_names.append(source_name)
        if isinstance(transition_role, str):
            transition_roles.append(transition_role)
            if transition_role not in role_ids:
                unknown_roles.append(transition_role)
        else:
            errors.append(f"source {source_name!r} must declare a transition_role")
        if isinstance(adapter_name, str):
            try:
                resolve_adapter(adapter_name)
            except ValueError:
                unresolved_adapters.append(adapter_name)
        else:
            errors.append(f"source {source_name!r} must declare an adapter")

    if unknown_roles:
        errors.append(f"unknown transition roles in external registry: {sorted(set(unknown_roles))}")
    if unresolved_adapters:
        errors.append(f"unknown adapters in external registry: {sorted(set(unresolved_adapters))}")

    return ValidationReport(
        name="external_registry_consistency",
        valid=not errors,
        errors=errors,
        warnings=warnings,
        details={
            "path": str(external_registry_path),
            "role_registry_path": str(transition_role_registry_path),
            "source_names": source_names,
            "transition_roles": transition_roles,
        },
    )


def validate_adapter_capabilities(
    external_registry_path: Path,
    transition_role_registry_path: Path,
) -> ValidationReport:
    role_report = validate_transition_role_registry(transition_role_registry_path)
    errors = list(role_report.errors)
    warnings = list(role_report.warnings)

    if not role_report.valid:
        return ValidationReport(
            name="adapter_capabilities",
            valid=False,
            errors=errors,
            warnings=warnings,
            details={"path": str(external_registry_path), "role_registry_path": str(transition_role_registry_path)},
        )

    role_data = load_transition_role_registry(transition_role_registry_path)
    roles_by_id = {role["id"]: role for role in role_data.get("roles", []) if isinstance(role, dict) and "id" in role}
    external_data = json.loads(external_registry_path.read_text(encoding="utf-8"))
    sources = external_data.get("sources", [])

    adapter_names: list[str] = []
    for source in sources:
        if not isinstance(source, dict):
            continue
        adapter_name = source.get("adapter")
        transition_role = source.get("transition_role")
        if not isinstance(adapter_name, str) or not isinstance(transition_role, str):
            continue

        adapter_caps = ADAPTER_CAPABILITIES.get(adapter_name)
        if adapter_caps is None:
            errors.append(f"adapter {adapter_name} is missing capability metadata")
            continue
        adapter_names.append(adapter_name)
        if not adapter_caps.get("official_scorer", False):
            errors.append(f"adapter {adapter_name} must declare official_scorer support")
        runtime_contracts = adapter_caps.get("runtime_contracts", [])
        if "frozen" not in runtime_contracts:
            errors.append(f"adapter {adapter_name} must support the frozen runtime contract")

        role = roles_by_id.get(transition_role)
        if role is None:
            errors.append(f"source {source.get('name')!r} references unknown transition role {transition_role}")
            continue
        required_diagnostics = set(role.get("diagnostics", []))
        supported_diagnostics = set(adapter_caps.get("diagnostics", []))
        missing = sorted(required_diagnostics - supported_diagnostics)
        if missing:
            errors.append(f"adapter {adapter_name} is missing diagnostics for role {transition_role}: {missing}")

    return ValidationReport(
        name="adapter_capabilities",
        valid=not errors,
        errors=errors,
        warnings=warnings,
        details={
            "path": str(external_registry_path),
            "role_registry_path": str(transition_role_registry_path),
            "adapter_names": adapter_names,
        },
    )


def validate_all(
    transition_role_registry_path: Path,
    external_registry_path: Path,
) -> ValidationReport:
    role_report = validate_transition_role_registry(transition_role_registry_path)
    external_report = validate_external_registry_consistency(external_registry_path, transition_role_registry_path)
    adapter_report = validate_adapter_capabilities(external_registry_path, transition_role_registry_path)

    errors = [*role_report.errors, *external_report.errors, *adapter_report.errors]
    warnings = sorted(set([*role_report.warnings, *external_report.warnings, *adapter_report.warnings]))
    details = {
        "transition_role_registry": role_report.details,
        "external_registry_consistency": external_report.details,
        "adapter_capabilities": adapter_report.details,
    }
    return ValidationReport(
        name="transition_role_validation",
        valid=not errors,
        errors=errors,
        warnings=warnings,
        details=details,
    )


def _default_paths() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[2]
    return root / "experiments" / "transition_role" / "registry.yaml", root / "data" / "external" / "registry.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the SRP transition role protocol and external registry.")
    parser.add_argument("--roles", type=Path, default=None, help="Path to experiments/transition_role/registry.yaml")
    parser.add_argument("--external", type=Path, default=None, help="Path to data/external/registry.json")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    args = parser.parse_args(argv)

    default_roles, default_external = _default_paths()
    roles_path = args.roles or default_roles
    external_path = args.external or default_external

    report = validate_all(roles_path, external_path)
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
