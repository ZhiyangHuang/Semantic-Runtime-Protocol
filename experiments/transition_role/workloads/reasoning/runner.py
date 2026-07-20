from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROLE_ID = "inference_proposal"
ROLE_PURPOSE = "govern semantic transitions generated from reasoning or inference traces before they become runtime state"
ROLE_DIAGNOSTICS = (
    "semantic_coverage",
    "semantic_drift",
    "transition_acceptance",
    "governance_consistency",
)


@dataclass(frozen=True)
class ReasoningRoleBridgeRun:
    metadata: dict[str, Any]
    source_manifest: dict[str, Any]
    adapter_config: dict[str, Any]
    provenance: str
    role_manifest: dict[str, Any]
    report_markdown: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected mapping at {path}")
    return data


def _render_report(run: ReasoningRoleBridgeRun) -> str:
    lines = [
        "# SRP Reasoning Role Bridge Report",
        "",
        "This report instantiates the `inference_proposal` transition role as a workload bridge.",
        "The external reasoning payload is not stored in the repository, so this artifact records protocol readiness rather than benchmark results.",
        "",
        "## 1. Frozen Contract",
        "",
        f"- Transition role: `{ROLE_ID}`",
        f"- Purpose: {ROLE_PURPOSE}",
        f"- Runtime contract: `{run.role_manifest['runtime_contract']}`",
        "",
        "## 2. External Source Registration",
        "",
        f"- Dataset: `{run.source_manifest.get('dataset', 'Reasoning Sources')}`",
        f"- Source family: `{run.source_manifest.get('source_family', 'reasoning')}`",
        f"- Adapter: `{run.source_manifest.get('adapter', 'reasoning_adapter')}`",
        f"- Payload: `{run.source_manifest.get('payload', 'not stored in repository')}`",
        "",
        "## 3. Adapter Contract",
        "",
        f"- Adapter transition role: `{run.adapter_config.get('transition_role', ROLE_ID)}`",
        f"- Adapter contract: `{run.adapter_config.get('adapter_contract', 'BoundaryCase')}`",
        f"- Benchmark scoring enabled: `{run.adapter_config.get('benchmark_scoring', False)}`",
        "",
        "## 4. Protocol Diagnostics",
        "",
    ]
    for diag in run.role_manifest["transition_role"]["diagnostics"]:
        lines.append(f"- diagnostic: `{diag}`")
    lines.extend(
        [
            "",
            "## 5. Interpretation",
            "",
            "- The reasoning source family is registered as an external input for `inference_proposal`.",
            "- No benchmark payload is stored locally, so the bridge cannot claim benchmark superiority.",
            "- The artifact is useful as a protocol readiness slice and a provenance anchor for later workload integration.",
            "",
        ]
    )
    return "\n".join(lines)


def build_reasoning_role_bridge_run() -> ReasoningRoleBridgeRun:
    repo_root = Path(__file__).resolve().parents[4]
    source_manifest_path = repo_root / "data" / "external" / "reasoning" / "manifest.json"
    adapter_config_path = repo_root / "data" / "external" / "reasoning" / "adapter_config.json"
    provenance_path = repo_root / "data" / "external" / "reasoning" / "provenance.md"

    source_manifest = _load_json(source_manifest_path)
    adapter_config = _load_json(adapter_config_path)
    provenance = provenance_path.read_text(encoding="utf-8")

    role_manifest = {
        "transition_role": {
            "id": ROLE_ID,
            "purpose": ROLE_PURPOSE,
            "diagnostics": list(ROLE_DIAGNOSTICS),
            "workload": "Reasoning Sources",
            "scope": "bridge readiness slice",
        },
        "runtime_contract": "srp-real-validation-v1",
    }
    metadata = {
        "experiment": "transition_role_role_bridge",
        "transition_role": ROLE_ID,
        "workload": "Reasoning Sources",
        "scope": "v1.2_role_bridge",
        "runtime_contract": "srp-real-validation-v1",
    }
    run = ReasoningRoleBridgeRun(
        metadata=metadata,
        source_manifest=source_manifest,
        adapter_config=adapter_config,
        provenance=provenance,
        role_manifest=role_manifest,
        report_markdown="",
    )
    object.__setattr__(run, "report_markdown", _render_report(run))
    return run


def write_reasoning_role_bridge_bundle(output_dir: str | Path) -> dict[str, str]:
    run = build_reasoning_role_bridge_run()
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata_path = output_path / "metadata.json"
    source_manifest_path = output_path / "source_manifest.json"
    adapter_config_path = output_path / "adapter_config.json"
    role_manifest_path = output_path / "role_manifest.json"
    provenance_path = output_path / "provenance.md"
    report_path = output_path / "report.md"

    metadata_path.write_text(json.dumps(run.metadata, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    source_manifest_path.write_text(json.dumps(run.source_manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    adapter_config_path.write_text(json.dumps(run.adapter_config, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    role_manifest_path.write_text(json.dumps(run.role_manifest, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    provenance_path.write_text(run.provenance, encoding="utf-8")
    report_path.write_text(run.report_markdown, encoding="utf-8")

    return {
        "metadata_json": str(metadata_path),
        "source_manifest_json": str(source_manifest_path),
        "adapter_config_json": str(adapter_config_path),
        "role_manifest_json": str(role_manifest_path),
        "provenance_md": str(provenance_path),
        "report_markdown": str(report_path),
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    output_root = repo_root / "experiments" / "results" / "transition_role" / ROLE_ID / "reasoning"
    output_dir = output_root / "run_latest"
    outputs = write_reasoning_role_bridge_bundle(output_dir)
    print(outputs["report_markdown"])


if __name__ == "__main__":  # pragma: no cover
    main()
