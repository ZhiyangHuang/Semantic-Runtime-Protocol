from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import List

from .result import CalibrationResult


class CalibrationResultStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, result: CalibrationResult) -> Path:
        path = self.root / f"{result.experiment_id}.json"
        payload = asdict(result) if is_dataclass(result) else dict(result)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return path

    def load(self, experiment_id: str) -> CalibrationResult:
        path = self.root / f"{experiment_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        return CalibrationResult(
            experiment_id=str(payload["experiment_id"]),
            parameter=str(payload["parameter"]),
            candidate_value=payload["candidate_value"],
            baseline_version=str(payload["baseline_version"]),
            timestamp=str(payload["timestamp"]),
            runtime_version=str(payload.get("runtime_version", payload.get("baseline_version", "default"))),
            accepted=bool(payload["accepted"]),
            constraints_passed=bool(payload["constraints_passed"]),
            tested_region=list(payload.get("tested_region", [])),
            acceptable_region=list(payload.get("acceptable_region", [])),
            rejected_region=list(payload.get("rejected_region", [])),
            metrics=dict(payload.get("metrics", {})),
            constraint_summary=dict(payload.get("constraint_summary", {})),
            invariant_status=dict(payload.get("invariant_status", {})),
            constraint_violations=list(payload.get("constraint_violations", [])),
            notes=list(payload.get("notes", [])),
        )

    def list_results(self, parameter: str) -> List[CalibrationResult]:
        results: List[CalibrationResult] = []
        for path in sorted(self.root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                continue
            if str(payload.get("parameter")) != str(parameter):
                continue
            results.append(self.load(str(payload["experiment_id"])))
        return results
