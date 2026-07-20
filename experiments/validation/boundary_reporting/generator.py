from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from .schemas import BoundaryCase


def load_cases_from_jsonl(path: str | Path) -> list[dict]:
    source_path = Path(path)
    cases: list[dict] = []
    with source_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
    return cases


def generate_cases(source_cases: Iterable[dict], runtime_contract: str) -> list[BoundaryCase]:
    """Convert protocol-neutral input cases into boundary-report cases."""

    del runtime_contract
    return [
        BoundaryCase(
            case_id=case["case_id"],
            semantic_state=dict(case["semantic_state"]),
            proposal=dict(case["proposal"]),
            evidence=dict(case["evidence"]),
            authority=dict(case["authority"]),
            expected=dict(case["expected"]),
        )
        for case in source_cases
    ]


def case_fingerprint(cases: Iterable[BoundaryCase]) -> str:
    import hashlib

    payload = json.dumps([asdict(case) for case in cases], sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
