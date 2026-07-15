from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Iterable, List

from .results import SensitivityResult


class SensitivityResultStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, result: SensitivityResult) -> Path:
        payload = self._serialize(result)
        path = self.root / f"{result.experiment_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        return path

    def load(self, experiment_id: str) -> SensitivityResult:
        path = self.root / f"{experiment_id}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        return self._deserialize(payload)

    def list_results(self, parameter: str) -> List[SensitivityResult]:
        results: List[SensitivityResult] = []
        for path in sorted(self.root.glob("*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            if str(payload.get("parameter")) != str(parameter):
                continue
            results.append(self._deserialize(payload))
        return results

    def _serialize(self, result: SensitivityResult) -> dict[str, object]:
        payload = asdict(result) if is_dataclass(result) else dict(result)
        payload["configuration"] = {
            "parameter": result.parameter,
            "value": result.value,
        }
        return payload

    def _deserialize(self, payload: dict[str, object]) -> SensitivityResult:
        return SensitivityResult(
            experiment_id=str(payload["experiment_id"]),
            parameter=str(payload["parameter"]),
            value=payload["value"],
            baseline_version=str(payload["baseline_version"]),
            timestamp=str(payload["timestamp"]),
            metrics=dict(payload.get("metrics", {})),
            observations=list(payload.get("observations", [])),
        )

