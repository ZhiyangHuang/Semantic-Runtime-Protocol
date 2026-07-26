from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class SensitivityExperimentRecord:
    experiment_id: str
    parameter: str
    experiment_type: str
    created_at: str
    result_location: str
    status: str
    result_count: int = 0


class SensitivityExperimentIndex:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def register(self, record: SensitivityExperimentRecord) -> None:
        records = self._read()
        records = [item for item in records if item.experiment_id != record.experiment_id]
        records.append(record)
        records.sort(key=lambda item: (item.parameter, item.experiment_id))
        self._write(records)

    def load(self, experiment_id: str) -> SensitivityExperimentRecord:
        for record in self._read():
            if record.experiment_id == experiment_id:
                return record
        raise KeyError(experiment_id)

    def list_experiments(self, parameter: str | None = None, status: str | None = None) -> List[SensitivityExperimentRecord]:
        records = self._read()
        if parameter is not None:
            records = [record for record in records if record.parameter == parameter]
        if status is not None:
            records = [record for record in records if record.status == status]
        return records

    def list_parameters(self, status: str | None = None) -> List[str]:
        parameters = []
        for record in self.list_experiments(status=status):
            if record.parameter not in parameters:
                parameters.append(record.parameter)
        return parameters

    def register_from_result(
        self,
        *,
        experiment_id: str,
        parameter: str,
        experiment_type: str,
        result_location: str,
        status: str,
        result_count: int = 0,
    ) -> SensitivityExperimentRecord:
        record = SensitivityExperimentRecord(
            experiment_id=experiment_id,
            parameter=parameter,
            experiment_type=experiment_type,
            created_at=datetime.now(timezone.utc).isoformat(),
            result_location=result_location,
            status=status,
            result_count=result_count,
        )
        self.register(record)
        return record

    def _read(self) -> List[SensitivityExperimentRecord]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [SensitivityExperimentRecord(**item) for item in payload]

    def _write(self, records: Iterable[SensitivityExperimentRecord]) -> None:
        payload = [asdict(record) for record in records]
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def register_validated_sensitivity_experiments(index: SensitivityExperimentIndex, result_root: str | Path) -> List[SensitivityExperimentRecord]:
    result_root_path = Path(result_root)
    registrations = [
        {
            "experiment_id": "activation_threshold_ofat_v1",
            "parameter": "activation_threshold",
            "result_location": str(result_root_path / "activation_threshold_ofat_v1.json"),
        },
        {
            "experiment_id": "recovery_min_evidence_ofat_v1",
            "parameter": "recovery_min_evidence",
            "result_location": str(result_root_path / "recovery_min_evidence_ofat_v1.json"),
        },
        {
            "experiment_id": "preserve_evidence_ofat_v1",
            "parameter": "preserve_evidence",
            "result_location": str(result_root_path / "preserve_evidence_ofat_v1.json"),
        },
        {
            "experiment_id": "archive_relations_ofat_v1",
            "parameter": "archive_relations",
            "result_location": str(result_root_path / "archive_relations_ofat_v1.json"),
        },
    ]
    records: List[SensitivityExperimentRecord] = []
    for item in registrations:
        records.append(
            index.register_from_result(
                experiment_id=item["experiment_id"],
                parameter=item["parameter"],
                experiment_type="OFAT",
                result_location=item["result_location"],
                status="validated",
                result_count=1,
            )
        )
    return records
