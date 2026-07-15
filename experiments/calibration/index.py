from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List

from .result import CalibrationResult


@dataclass(frozen=True)
class CalibrationRecord:
    calibration_id: str
    parameter: str
    candidate_value: Any
    baseline_version: str
    created_at: str
    result_location: str
    status: str
    tested_region: list[Any] = field(default_factory=list)
    acceptable_region: list[Any] = field(default_factory=list)
    rejected_region: list[Any] = field(default_factory=list)
    accepted: bool = False


class CalibrationIndex:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def register(self, record: CalibrationRecord) -> None:
        records = self._read()
        records = [item for item in records if item.calibration_id != record.calibration_id]
        records.append(record)
        records.sort(key=lambda item: (item.parameter, item.calibration_id))
        self._write(records)

    def register_from_result(self, result: CalibrationResult, *, result_location: str) -> CalibrationRecord:
        record = CalibrationRecord(
            calibration_id=result.experiment_id,
            parameter=result.parameter,
            candidate_value=result.candidate_value,
            baseline_version=result.baseline_version,
            created_at=datetime.now(timezone.utc).isoformat(),
            result_location=result_location,
            status="accepted" if result.accepted else "rejected",
            tested_region=list(result.tested_region),
            acceptable_region=list(result.acceptable_region),
            rejected_region=list(result.rejected_region),
            accepted=result.accepted,
        )
        self.register(record)
        return record

    def load(self, calibration_id: str) -> CalibrationRecord:
        for record in self._read():
            if record.calibration_id == calibration_id:
                return record
        raise KeyError(calibration_id)

    def list_records(self, parameter: str | None = None, status: str | None = None) -> List[CalibrationRecord]:
        records = self._read()
        if parameter is not None:
            records = [record for record in records if record.parameter == parameter]
        if status is not None:
            records = [record for record in records if record.status == status]
        return records

    def list_parameters(self, status: str | None = None) -> List[str]:
        parameters: list[str] = []
        for record in self.list_records(status=status):
            if record.parameter not in parameters:
                parameters.append(record.parameter)
        return parameters

    def _read(self) -> List[CalibrationRecord]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [CalibrationRecord(**item) for item in payload]

    def _write(self, records: Iterable[CalibrationRecord]) -> None:
        payload = [asdict(record) for record in records]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

