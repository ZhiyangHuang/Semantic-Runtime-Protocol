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
            "status_layers": ["Main", "Appendix", "Archive"],
        },
    }


def render_markdown(summary: dict) -> str:
    main_evidence = summary["main_evidence"]
    lines: list[str] = [
        "# SRP Main Results Summary V1",
        "",
        "Two-track guide for the current SRP release.",
        "",
        "## STFB Standard Track",
        "",
        "Use this track for the frozen benchmark contract and its core evidence.",
        "",
        "- `RQ1`: controlled semantic transition failures under the STFB contract",
        "- `RQ2`: external validation under the same frozen contract",
        "- Core sources: `STFB/README.md`, `paper/docs/plans/STFB_SPEC.md`, `paper/docs/plans/STFB_ROADMAP.md`",
        "",
        "## Supplementary Protocol Track",
        "",
        "Use this track for supporting governance and runtime evidence.",
        "",
        "- `RQ1b`: evidence-authority separation",
        "- `RQ3`: divergence behavior",
        "- `RQ4`: capability trade-offs and runtime integration",
        "- Core sources: `experiments/validation/evidence_authority_separation/README.md`, `paper/SRP_MANUSCRIPT_V1.md`, `paper/docs/release/EVIDENCE_SURFACE.md`",
        "",
        "## Quick Rule",
        "",
        "- If you want the benchmark standard, start with the STFB track.",
        "- If you want supporting evidence, use the supplementary protocol track.",
        "- Do not blend the two when citing results.",
        "",
        "## Main Evidence Snapshot",
        "",
        "| Benchmark | Status | Focus |",
        "| --- | --- | --- |",
    ]

    for item in main_evidence:
        lines.append(
            f"| {item.get('benchmark', '')} | {item.get('status', '')} | {item.get('focus', '')} |"
        )

    lines.extend(
        [
            "",
            f"- main evidence count: `{summary['summary'].get('main_evidence_count', 0)}`",
            "- release evidence remains benchmark-by-benchmark, not blended into one score",
            "",
            "## Where To Look",
            "",
            "- `paper/SRP_MANUSCRIPT_V1.md` for the manuscript",
            "- `paper/docs/release/EVIDENCE_SURFACE.md` for the consolidated evidence surface",
            "- `paper/docs/release/README.md` for the active release summary",
            "",
            "Use this page for a quick release scan; use the detailed reports for provenance.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    manifest = load_manifest()
    summary = build_summary(manifest)
    timestamp = datetime.now(timezone.utc).isoformat()
    metadata = {
        "generated_at": timestamp,
        "generator": "scripts/generate_main_results_summary.py",
        "manifest_path": str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/"),
        "summary_path": str(SUMMARY_MD_PATH.relative_to(ROOT)).replace("\\", "/"),
        "summary_json_path": str(SUMMARY_JSON_PATH.relative_to(ROOT)).replace("\\", "/"),
        "metadata_json_path": str(METADATA_JSON_PATH.relative_to(ROOT)).replace("\\", "/"),
        "schema_version": summary["schema_version"],
        "summary_version": summary["summary_version"],
        "main_evidence_count": summary["summary"]["main_evidence_count"],
    }

    SUMMARY_MD_PATH.write_text(render_markdown(summary), encoding="utf-8")
    SUMMARY_JSON_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    METADATA_JSON_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
