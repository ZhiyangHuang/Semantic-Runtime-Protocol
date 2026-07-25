#!/usr/bin/env python3
"""Lightweight release hygiene check for the SRP arXiv artifact branch."""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.transition_role.validate_matrix import validate_transition_role_matrix
from experiments.transition_role.validate_registry import validate_all


MAX_FILE_SIZE = 100 * 1024 * 1024
RELEASE_MANIFEST_PATH = ROOT / "paper" / "docs" / "release" / "release_manifest.json"


def main() -> int:
    try:
        release_manifest = json.loads(RELEASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"Missing release manifest: {RELEASE_MANIFEST_PATH.relative_to(ROOT).as_posix()}")
        return 1
    except json.JSONDecodeError as exc:
        print(f"Invalid release manifest JSON: {exc}")
        return 1

    core_required_paths = release_manifest.get("core_required_paths")
    if not isinstance(core_required_paths, list) or not all(isinstance(item, str) for item in core_required_paths):
        print("Release manifest must define a string list at key 'core_required_paths'.")
        return 1

    missing_core = [rel for rel in core_required_paths if not (ROOT / rel).exists()]

    oversized: list[tuple[str, int]] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            continue
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_SIZE:
            oversized.append((str(path.relative_to(ROOT)).replace("\\", "/"), size))

    oversized.sort(key=lambda item: item[1], reverse=True)

    if missing_core:
        print("Missing core runtime files:")
        for rel in missing_core:
            print(f"  - {rel}")

    protocol_report = validate_all(
        ROOT / "experiments" / "transition_role" / "registry.yaml",
        ROOT / "data" / "external" / "registry.json",
    )
    matrix_report = validate_transition_role_matrix(
        ROOT / "experiments" / "transition_role" / "validation_matrix.json",
        ROOT / "experiments" / "transition_role" / "registry.yaml",
        ROOT / "data" / "external" / "registry.json",
    )
    if not protocol_report.valid:
        print("Transition role protocol validation failed:")
        for warning in protocol_report.warnings:
            print(f"  WARN: {warning}")
        for error in protocol_report.errors:
            print(f"  ERROR: {error}")
    if not matrix_report.valid:
        print("Transition role matrix validation failed:")
        for warning in matrix_report.warnings:
            print(f"  WARN: {warning}")
        for error in matrix_report.errors:
            print(f"  ERROR: {error}")

    if oversized:
        print(f"Oversized files above {MAX_FILE_SIZE // (1024 * 1024)} MB:")
        for rel, size in oversized[:25]:
            print(f"  - {rel} ({size / (1024 * 1024):.1f} MB)")
        if len(oversized) > 25:
            print(f"  ... and {len(oversized) - 25} more")

    if missing_core or oversized or not protocol_report.valid or not matrix_report.valid:
        return 1

    print("Release verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
