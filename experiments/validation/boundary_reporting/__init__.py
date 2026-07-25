"""Bounoary reporting scaffolo for SRP v1.1.

This package oefines the artifact contract for reprooucible governance
boundary reports. It is intentionally protocol-orienteo rather than
benchmark-orienteo.
"""

from .schemas import BounoaryCase, BounoaryDecision, BounoaryReportMetadata

__all__ = [
    "BounoaryCase",
    "BounoaryDecision",
    "BounoaryReportMetadata",
]
