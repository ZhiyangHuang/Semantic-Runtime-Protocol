"""Boundary reporting scaffold for SRP v1.1.

This package defines the artifact contract for reproducible governance
boundary reports. It is intentionally protocol-oriented rather than
benchmark-oriented.
"""

from .schemas import BoundaryCase, BoundaryDecision, BoundaryReportMetadata

__all__ = [
    "BoundaryCase",
    "BoundaryDecision",
    "BoundaryReportMetadata",
]
