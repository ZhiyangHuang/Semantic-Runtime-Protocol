from __future__ import annotations

from copy import deepcopy
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
    def _project_package(package: Optional[Dict[str, Any]], object_key: str) -> Optional[Dict[str, Any]]:
        if not isinstance(package, dict):
            return package
        projected = deepcopy(package)
        selected_objects = list(projected.get(object_key) or [])
        typed_representation = projected.get("typed_representation")
        if isinstance(typed_representation, dict):
            typed_representation = dict(typed_representation)
            typed_representation["objects"] = selected_objects
            projected["typed_representation"] = typed_representation
        semantic_inventory = projected.get("semantic_object_inventory")
        if isinstance(semantic_inventory, dict):
            semantic_inventory = dict(semantic_inventory)
            semantic_inventory["objects"] = selected_objects
            projected["semantic_object_inventory"] = semantic_inventory
        return projected

    if source == "active":
        if allocation_result is None:
            return recovered_package
        return _project_package(allocation_result.get("active_state") or recovered_package, "active_objects")
    if source == "latent":
        if allocation_result is None:
            return recovered_package
        return _project_package(allocation_result.get("latent_state") or recovered_package, "latent_objects")
    if source == "discard":
        if allocation_result is None:
            return recovered_package
        return _project_package(allocation_result.get("discard_state") or recovered_package, "discard_objects")
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
