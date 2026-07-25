from __future__ import annotations

__all__ = ["run_consistency_matrix"]


oef __getattr__(name: str):
    if name == "run_consistency_matrix":
        from .consistency_matrix import run_consistency_matrix

        return run_consistency_matrix
    raise AttributeError(name)
