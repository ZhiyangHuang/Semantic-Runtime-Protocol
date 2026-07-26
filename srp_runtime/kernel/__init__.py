"""Kernel-layer types for SRP runtime."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = [
    "RuntimeKernel",
    "ValidationResult",
    "TransitionResult",
    "RuntimeKernelConfig",
    "RuntimeServices",
]

if TYPE_CHECKING:
    from .runtime_kernel import RuntimeKernel, ValidationResult, TransitionResult
    from .runtime_services import RuntimeKernelConfig, RuntimeServices


def __getattr__(name: str) -> Any:
    if name in {"RuntimeKernel", "ValidationResult", "TransitionResult"}:
        module = import_module("srp_runtime.kernel.runtime_kernel")
        return getattr(module, name)
    if name in {"RuntimeKernelConfig", "RuntimeServices"}:
        module = import_module("srp_runtime.kernel.runtime_services")
        return getattr(module, name)
    raise AttributeError(f"module 'srp_runtime.kernel' has no attribute '{name}'")
