from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "paper" / "main_evidence_manifest.json"
SUMMARY_MD_PATH = ROOT / "paper" / "SRP_MAIN_RESULTS_SUMMARY_V1.md"
SUMMARY_JSON_PATH = ROOT / "paper" / "SRP_MAIN_RESULTS_SUMMARY_V1.json"
METADATA_JSON_PATH = ROOT / "paper" / "SRP_MAIN_RESULTS_SUMMARY_V1.metadata.json"


def load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def build_summary(manifest: dict) -> dict:
    main_evidence = list(manifest.get("main_evidence", []))
    total_samples = sum(int(item.get("sample_count", 0)) for item in main_evidence)
    return {
        "schema_version": 1,
        "summary_version": "v1.0",
        "manifest_name": manifest.get("manifest_name", "srp_main_evidence_manifest"),
        "evidence_status_policy": list(manifest.get("evidence_status_policy", [])),
        "main_evidence": main_evidence,
        "supporting_evidence": list(manifest.get("supporting_evidence", [])),
        "release_notes": list(manifest.get("notes", [])),
        "summary": {
            "main_evidence_count": len(main_evidence),
            "main_evidence_sample_count": total_samples,
            "status_layers": ["Main", "Appendix", "Archive"],
        },
    }


def render_markdown(summary: dict) -> str:
    main_evidence = summary["main_evidence"]
    totals = summary["summary"]
    lines: list[str] = [
        "# SRP Main Results Summary V1",
        "",
        "This document is the paper-facing source of truth for benchmark positioning and sample counts.",
        "It is generated from `paper/main_evidence_manifest.json`.",
        "",
        "## Evidence Status Policy",
        "",
    ]
    for status in summary.get("evidence_status_policy", []):
        lines.append(f"- {status}")
    lines.extend(
        [
            "",
            "## Main Evidence",
            "",
            "| Benchmark | Status | Samples | Focus |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for item in main_evidence:
        lines.append(
            f"| {item.get('benchmark', '')} | {item.get('status', '')} | {item.get('sample_count', 0)} | {item.get('focus', '')} |"
        )
    lines.extend(
        [
            "",
            "## Totals",
            "",
            f"- main_evidence_count: `{totals.get('main_evidence_count', 0)}`",
            f"- main_evidence_sample_count: `{totals.get('main_evidence_sample_count', 0)}`",
            "",
            "## Supporting Evidence Layers",
            "",
        ]
    )
    for section in summary.get("supporting_evidence", []):
        lines.append(f"- {section.get('status', '')}: {', '.join(section.get('items', []))}")
    lines.extend(
        [
            "",
            "## Release Policy",
            "",
        ]
    )
    for note in summary.get("release_notes", []):
        lines.append(f"- {note}")
    lines.extend(
        [
            "",
            "## Usage Rule",
            "",
            "- Paper prose should cite this summary for benchmark counts and status tiers.",
            "- Detailed reports and metadata remain the lower-level artifacts.",
            "- The release-facing benchmark set is MMLU, LongMemEval, ARC, and HumanEval, with 100 samples each.",
            "- Benchmark payloads are obtained from original sources and are not redistributed in this repository.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    manifest = load_manifest()
    summary = build_summary(manifest)
    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/generate_main_results_summary.py",
        "manifest_path": str(MANIFEST_PATH.relative_to(ROOT)),
        "summary_path": str(SUMMARY_MD_PATH.relative_to(ROOT)),
        "summary_json_path": str(SUMMARY_JSON_PATH.relative_to(ROOT)),
        "metadata_json_path": str(METADATA_JSON_PATH.relative_to(ROOT)),
        "schema_version": summary["schema_version"],
        "summary_version": summary["summary_version"],
        "main_evidence_count": summary["summary"]["main_evidence_count"],
        "main_evidence_sample_count": summary["summary"]["main_evidence_sample_count"],
    }

    SUMMARY_MD_PATH.write_text(render_markdown(summary), encoding="utf-8")
    SUMMARY_JSON_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    METADATA_JSON_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
