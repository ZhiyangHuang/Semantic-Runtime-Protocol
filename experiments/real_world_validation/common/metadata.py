from __future__ import annotations

import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schemas import DatasetManifest, RunConfig


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def build_metadata(
    *,
    experiment: str,
    dataset: str,
    scope: str,
    runtime_contract: str = "srp-real-validation-v1",
    version: str = "v1",
    commit: str | None = None,
) -> dict[str, Any]:
    return {
        "experiment": experiment,
        "version": version,
        "generated_at": utc_now_iso(),
        "runtime_contract": runtime_contract,
        "commit": commit or git_commit(),
        "dataset": dataset,
        "scope": scope,
    }


def build_dataset_manifest(
    *,
    dataset: str,
    version: str,
    source: str,
    subset: str,
    samples: int,
    selection_rule: str,
    source_hash: str = "",
    selected_samples: int = 0,
    excluded_cases: tuple[str, ...] = (),
) -> DatasetManifest:
    return DatasetManifest(
        dataset=dataset,
        version=version,
        source=source,
        subset=subset,
        samples=samples,
        selection_rule=selection_rule,
        source_hash=source_hash,
        selected_samples=selected_samples,
        excluded_cases=excluded_cases,
    )


def build_run_config(
    *,
    seed: int = 42,
    encoder: str = "bridge_encoder",
    threshold: float = 0.9,
    relation_depth: int = 1,
    evidence_policy: str = "default",
    governance_mode: str = "srp",
    baseline_set: tuple[str, ...] = ("full_context", "sliding_window", "vector_rag", "srp"),
) -> RunConfig:
    return RunConfig(
        seed=seed,
        encoder=encoder,
        threshold=threshold,
        relation_depth=relation_depth,
        evidence_policy=evidence_policy,
        governance_mode=governance_mode,
        baseline_set=baseline_set,
    )
