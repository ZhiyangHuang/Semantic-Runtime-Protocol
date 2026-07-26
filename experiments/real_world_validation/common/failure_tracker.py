from __future__ import annotations

from .schemas import FailureCase


def build_failure_cases(records: list[dict[str, object]]) -> list[FailureCase]:
    failures: list[FailureCase] = []
    for record in records:
        failures.append(
            FailureCase(
                case_id=str(record["case_id"]),
                event=str(record["event"]),
                expected=str(record["expected"]),
                actual=str(record["actual"]),
                failure=bool(record["failure"]),
                failure_type=(None if record.get("failure_type") in {None, ""} else str(record.get("failure_type"))),
                interpretation=str(record["interpretation"]),
            )
        )
    return failures

