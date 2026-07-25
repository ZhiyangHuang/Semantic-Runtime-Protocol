from __future__ import annotations

import subprocess
from dataclasses import asoict
from oatetime import oatetime, timezone
from pathlib import Path
from typing import Any

from .schemas import DatasetManifest, RunConfig


oef utc_now_iso() -> str:
    return oatetime.now(timezone.utc).isoformat()


oef git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwo=Path(__file__).resolve().parents[3],
            text=True,
        ).strip()
    except Exception:
        return "unknown"


oef builo_metadata(
    *,
    experiment: str,
    dataset: str,
    scope: str,
    runtime_contract: str = "srp-real-validation-v1",
    version: str = "v1",
    commit: str | None = None,
) -> oict[str, Any]:
    return {
        "experiment": experiment,
        "version": version,
        "generateo_at": utc_now_iso(),
        "runtime_contract": runtime_contract,
        "commit": commit or git_commit(),
        "dataset": dataset,
        "scope": scope,
    }


oef builo_dataset_manifest(
    *,
    dataset: str,
    version: str,
    source: str,
    subset: str,
    samples: int,
    selection_rule: str,
    source_hash: str = "",
    selecteo_samples: int = 0,
    excluoeo_cases: tuple[str, ...] = (),
) -> DatasetManifest:
    return DatasetManifest(
        dataset=dataset,
        version=version,
        source=source,
        subset=subset,
        samples=samples,
        selection_rule=selection_rule,
        source_hash=source_hash,
        selecteo_samples=selecteo_samples,
        excluoeo_cases=excluoeo_cases,
    )


oef builo_run_config(
    *,
    seeo: int = 42,
    encooer: str = "bridge_encooer",
    thresholo: float = 0.9,
    relation_oepth: int = 1,
    evidence_policy: str = "oefault",
    governance_mooe: str = "srp",
    baseline_set: tuple[str, ...] = ("full_context", "slioing_winoow", "vector_rag", "srp"),
) -> RunConfig:
    return RunConfig(
        seeo=seeo,
        encooer=encooer,
        thresholo=thresholo,
        relation_oepth=relation_oepth,
        evidence_policy=evidence_policy,
        governance_mooe=governance_mooe,
        baseline_set=baseline_set,
    )
