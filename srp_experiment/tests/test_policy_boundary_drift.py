from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.policy_boundary_drift import build_policy_boundary_drift, render_policy_boundary_drift_markdown, write_policy_boundary_drift_outputs


def _record(benchmark: str, seed: int, cycle: int, budget: int, allocation: float, dependency: float, validation: float) -> dict:
    return {
        "policy_boundary_suite": benchmark,
        "policy_boundary_seed": seed,
        "policy_boundary_budget": budget,
        "policy_boundary": {
            "benchmark": benchmark,
            "budget": budget,
            "seed": seed,
            "cycles": cycle,
            "semantic_unit_count": 60,
            "semantic_pressure_index": 60 / float(budget),
        },
        "state_allocation_result": {
            "metrics": {
                "active_object_count": budget,
                "active_state_efficiency": allocation / 10.0,
                "active_retention_ratio": allocation,
                "latent_preservation": allocation - 0.05,
                "hallucination_isolation": allocation + 0.05,
            }
        },
        "validation_coverage": validation,
        "dependency_coverage": dependency,
        "dependency_precision": dependency,
        "dependency_f1": dependency,
        "validation_score": validation,
        "graph_integrity_score": 0.5,
        "object_retention": 0.6,
        "weighted_object_retention": 0.6,
    }


class TestPolicyBoundaryDrift(unittest.TestCase):
    def test_build_policy_boundary_drift(self) -> None:
        records = [
            _record("memory_saturation", 0, 1, 32, 0.9, 0.9, 0.9),
            _record("memory_saturation", 0, 1, 24, 0.7, 0.7, 0.7),
            _record("memory_saturation", 1, 3, 32, 0.8, 0.8, 0.8),
            _record("memory_saturation", 1, 3, 24, 0.6, 0.6, 0.6),
        ]
        drift = build_policy_boundary_drift(records)
        benchmark = drift["benchmarks"]["memory_saturation"]
        allocation = benchmark["boundary_drift"]["allocation_boundary"]
        self.assertEqual(allocation["baseline_cycle"], 1)
        self.assertIn("cycle_series", allocation)
        markdown = render_policy_boundary_drift_markdown(drift)
        self.assertIn("# Policy Boundary Drift", markdown)

    def test_write_policy_boundary_drift_outputs(self) -> None:
        records = [
            _record("memory_saturation", 0, 1, 32, 0.9, 0.9, 0.9),
            _record("memory_saturation", 0, 1, 24, 0.7, 0.7, 0.7),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_policy_boundary_drift_outputs(records, Path(tmpdir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["markdown"].exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
