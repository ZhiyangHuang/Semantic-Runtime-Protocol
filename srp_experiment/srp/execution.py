from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .execution_payload import ExecutionPayload, build_execution_payload

def execution_state_source() -> str:
    return str(os.getenv("SRP_EXECUTION_STATE_SOURCE", "recovered")).strip().lower()


def _state_payload_for_source(
    source: str,
    *,
    recovered_package: Optional[Dict[str, Any]],
    allocation_result: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if source == "active":
        if allocation_result is None:
            return recovered_package
        return allocation_result.get("active_state") or recovered_package
    if source == "latent":
        if allocation_result is None:
            return recovered_package
        return allocation_result.get("latent_state") or recovered_package
    if source == "discard":
        if allocation_result is None:
            return recovered_package
        return allocation_result.get("discard_state") or recovered_package
    return recovered_package


def select_execution_state(
    *,
    recovered_package: Optional[Dict[str, Any]],
    allocation_result: Optional[Dict[str, Any]] = None,
    source: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    selected_source = (source or execution_state_source()).strip().lower()
    return _state_payload_for_source(
        selected_source,
        recovered_package=recovered_package,
        allocation_result=allocation_result,
    )


def build_selected_execution_payload(
    *,
    recovered_package: Optional[Dict[str, Any]],
    allocation_result: Optional[Dict[str, Any]] = None,
    source: Optional[str] = None,
) -> ExecutionPayload:
    selected_source = (source or execution_state_source()).strip().lower()
    selected_state = select_execution_state(
        recovered_package=recovered_package,
        allocation_result=allocation_result,
        source=selected_source,
    )
    return build_execution_payload(selected_state, source=selected_source)
