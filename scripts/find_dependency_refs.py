#!/usr/bin/env python3
"""Generate a dependency audit report for legacy references and import cleanup."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "artifacts" / "dependency_audit"
REPORT_JSON = REPORT_DIR / "import_dependency_report.json"
REPORT_MD = REPORT_DIR / "import_dependency_report.md"

SCAN_EXTENSIONS = {".py", ".md", ".json", ".toml", ".yml", ".yaml", ".txt"}

# Keep the scan focused on the legacy package that is being retired.
LEGACY_PACKAGE_NAMES = ("srp_experiment",)


def _package_import_patterns(package_names: Iterable[str]) -> list[re.Pattern[str]]:
    patterns: list[re.Pattern[str]] = []
    for package_name in package_names:
        escaped = re.escape(package_name)
        patterns.append(re.compile(rf"^\s*from\s+{escaped}(?:\.[A-Za-z0-9_]+)*\s+import\b"))
        patterns.append(re.compile(rf"^\s*import\s+{escaped}(?:\b|\.)"))
    return patterns


IMPORT_PATTERNS = _package_import_patterns(LEGACY_PACKAGE_NAMES)
TEXT_PATTERNS = {
    "legacy_package": re.compile(r"\bsrp_experiment\b"),
}

BLOCKING_CATEGORIES = {"runtime_imports", "test_imports", "tooling_imports"}
CATEGORY_BASELINES = {
    "runtime_imports": 20,
    "tooling_imports": 28,
    "test_imports": 87,
}
CATEGORY_PRIORITY = {
    "runtime_imports": "P0",
    "tooling_imports": "P1",
    "test_imports": "P2",
    "markdown_references": "P3",
    "audit_references": "P3",
    "historical_mentions": "P3",
}
PRIORITY_ORDER = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}


@dataclass(frozen=True)
class ReferenceHit:
    file: str
    line: int
    kind: str
    category: str
    blocks_deletion: bool
    text: str


def iter_scan_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        if "artifacts" in path.parts and "dependency_audit" in path.parts:
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        yield path


def collect_hits() -> list[ReferenceHit]:
    hits: list[ReferenceHit] = []
    for path in iter_scan_files():
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue

        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for line_number, line in enumerate(lines, start=1):
            for pattern in IMPORT_PATTERNS:
                if pattern.search(line):
                    if "/tests/" in rel or rel.startswith("tests/"):
                        category = "test_imports"
                    elif rel.startswith("scripts/") or "/run_" in rel or rel.startswith("experiments/compatibility/"):
                        category = "tooling_imports"
                    else:
                        category = "runtime_imports"
                    hits.append(
                        ReferenceHit(
                            file=rel,
                            line=line_number,
                            kind="import",
                            category=category,
                            blocks_deletion=True,
                            text=line.strip(),
                        )
                    )
                    break

            for kind, pattern in TEXT_PATTERNS.items():
                if not pattern.search(line):
                    continue
                if rel.startswith("docs/"):
                    category = "historical_mentions"
                elif rel.startswith("artifacts/"):
                    category = "audit_references"
                elif rel.endswith(".md"):
                    category = "markdown_references"
                else:
                    category = "historical_mentions"
                hits.append(
                    ReferenceHit(
                        file=rel,
                        line=line_number,
                        kind=kind,
                        category=category,
                        blocks_deletion=False,
                        text=line.strip(),
                    )
                )
    return hits


def build_summary(hits: list[ReferenceHit]) -> dict[str, object]:
    by_kind: dict[str, int] = {}
    by_category: dict[str, int] = {}
    blocking_by_category: dict[str, int] = {}
    by_file: dict[str, int] = {}
    migration_velocity: list[dict[str, object]] = []

    for hit in hits:
        by_kind[hit.kind] = by_kind.get(hit.kind, 0) + 1
        by_category[hit.category] = by_category.get(hit.category, 0) + 1
        if hit.blocks_deletion:
            blocking_by_category[hit.category] = blocking_by_category.get(hit.category, 0) + 1
        by_file[hit.file] = by_file.get(hit.file, 0) + 1

    deletion_readiness: list[dict[str, object]] = []
    all_categories = sorted(
        set(by_category) | set(CATEGORY_BASELINES),
        key=lambda category: (PRIORITY_ORDER.get(CATEGORY_PRIORITY.get(category, "P3"), 3), category),
    )
    for category in all_categories:
        blocks = category in BLOCKING_CATEGORIES
        baseline = CATEGORY_BASELINES.get(category)
        remaining = by_category.get(category, 0)
        completed = None if baseline is None else max(0, baseline - remaining)
        deletion_readiness.append(
            {
                "category": category,
                "priority": CATEGORY_PRIORITY.get(category, "P3"),
                "count": remaining,
                "blocks_deletion": blocks,
                "ready_for_deletion": not blocks,
            }
        )
        if baseline is not None:
            migration_velocity.append(
                {
                    "category": category,
                    "priority": CATEGORY_PRIORITY.get(category, "P3"),
                    "baseline": baseline,
                    "remaining": remaining,
                    "completed": completed,
                    "completion_ratio": round(completed / baseline, 6) if baseline else None,
                }
            )

    return {
        "total_hits": len(hits),
        "blocking_hits": sum(1 for hit in hits if hit.blocks_deletion),
        "by_kind": dict(sorted(by_kind.items())),
        "by_category": {category: by_category.get(category, 0) for category in all_categories},
        "blocking_by_category": dict(sorted(blocking_by_category.items())),
        "deletion_readiness": deletion_readiness,
        "migration_velocity": migration_velocity,
        "by_file": dict(sorted(by_file.items(), key=lambda item: (-item[1], item[0]))),
    }


def render_markdown(summary: dict[str, object], hits: list[ReferenceHit]) -> str:
    lines = [
        "# Legacy Dependency Report",
        "",
        "This report enumerates legacy references that matter for repository deletion planning.",
        "",
        "## Summary",
        "",
        f"- total hits: `{summary['total_hits']}`",
        f"- blocking hits: `{summary['blocking_hits']}`",
        "",
        "### Priority Ladder",
        "",
        "| Priority | Category | Meaning |",
        "| --- | --- | --- |",
        "| `P0` | `runtime_imports` | Live code still depends on a legacy package at runtime. |",
        "| `P1` | `tooling_imports` | Scripts, generators, and maintenance tools still depend on a legacy package. |",
        "| `P2` | `test_imports` | Tests still depend on a legacy package; important, but usually lower risk than live code. |",
        "| `P3` | `markdown_references` / `audit_references` / `historical_mentions` | Informative references that do not by themselves block deletion. |",
        "",
        "### Deletion readiness",
        "",
        "| Category | Priority | Count | Blocks deletion? | ready for deletion? |",
        "| --- | --- | ---: | :---: | :---: |",
    ]

    for row in summary["deletion_readiness"]:
        blocks = "yes" if row["blocks_deletion"] else "no"
        ready = "yes" if row["ready_for_deletion"] else "no"
        lines.append(f"| `{row['category']}` | `{row['priority']}` | `{row['count']}` | `{blocks}` | `{ready}` |")

    lines.extend(
        [
            "",
            "### Blocking Counts",
            "",
            "| Category | Blocking Count |",
            "| --- | ---: |",
        ]
    )
    for category, count in summary["blocking_by_category"].items():
        lines.append(f"| `{category}` | `{count}` |")

    if summary["migration_velocity"]:
        lines.extend(
            [
                "",
                "### Migration Velocity",
                "",
                "| Category | Baseline | Remaining | Completed | Completion |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in summary["migration_velocity"]:
            completion = f"{row['completion_ratio']:.6f}".rstrip("0").rstrip(".")
            lines.append(
                f"| `{row['category']}` | `{row['baseline']}` | `{row['remaining']}` | `{row['completed']}` | `{completion}` |"
            )

    lines.extend(
        [
            "",
            "### By Kind",
            "",
            "| Kind | Count |",
            "| --- | ---: |",
        ]
    )
    for kind, count in summary["by_kind"].items():
        lines.append(f"| `{kind}` | `{count}` |")

    lines.extend(
        [
            "",
            "### By Category",
            "",
            "| Category | Count | Blocks deletion? |",
            "| --- | ---: | :---: |",
        ]
    )
    for category, count in summary["by_category"].items():
        blocks = "yes" if category in BLOCKING_CATEGORIES else "no"
        lines.append(f"| `{category}` | `{count}` | `{blocks}` |")

    lines.extend(
        [
            "",
            "### By File",
            "",
            "| File | Count |",
            "| --- | ---: |",
        ]
    )
    for file_path, count in summary["by_file"].items():
        lines.append(f"| `{file_path}` | `{count}` |")

    lines.extend(
        [
            "",
            "## Hits",
            "",
            "| File | Line | Kind | Category | Text |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for hit in hits:
        safe_text = hit.text.replace("|", "\\|")
        lines.append(f"| `{hit.file}` | `{hit.line}` | `{hit.kind}` | `{hit.category}` | `{safe_text}` |")

    lines.extend(
        [
            "",
            "## Reading Guide",
            "",
            "- `runtime_imports` (`P0`), `tooling_imports` (`P1`), and `test_imports` (`P2`) are blocking categories and must reach zero before legacy directories can be deleted.",
            "- `markdown_references`, `audit_references`, and `historical_mentions` are non-blocking categories; they can remain after live dependency cleanup.",
            "- `scripts/verify_release.py` must stop depending on historical traceability assets before they can be removed.",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    hits = collect_hits()
    summary = build_summary(hits)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "summary": summary,
        "hits": [asdict(hit) for hit in hits],
    }
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_markdown(summary, hits), encoding="utf-8")
    print(str(REPORT_JSON))
    print(str(REPORT_MD))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
