from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.policy_boundary_robustness import (
    build_policy_boundary_robustness,
    render_policy_boundary_robustness_markdown,
    write_policy_boundary_robustness_outputs,
)


def _record(benchmark: str, seed: int, budget: int, retention: float, validation: float, dependency: float, dependency_f1: float) -> dict:
    return {
        "policy_boundary_suite": benchmark,
        "policy_boundary_seed": seed,
        "policy_boundary_budget": budget,
        "policy_boundary": {
            "benchmark": benchmark,
            "budget": budget,
            "seed": seed,
            "semantic_unit_count": 60,
            "semantic_pressure_index": 60 / float(budget),
        },
        "state_allocation_result": {
            "metrics": {
                "active_object_count": budget,
                "active_state_efficiency": retention / 10.0,
                "active_retention_ratio": retention,
                "latent_preservation": retention - 0.05,
                "hallucination_isolation": retention + 0.05,
            }
        },
        "validation_coverage": validation,
        "dependency_coverage": dependency,
        "dependency_precision": dependency_f1,
        "dependency_f1": dependency_f1,
        "validation_score": validation,
        "graph_integrity_score": 0.5,
        "object_retention": 0.6,
        "weighted_object_retention": 0.6,
    }


class TestPolicyBoundaryRobustness(unittest.TestCase):
    def test_build_policy_boundary_robustness(self) -> None:
        records = [
            _record("memory_saturation", 0, 32, 0.8, 0.9, 0.9, 0.7),
            _record("memory_saturation", 0, 24, 0.6, 0.7, 0.7, 0.6),
            _record("memory_saturation", 1, 32, 0.82, 0.91, 0.91, 0.72),
            _record("memory_saturation", 1, 24, 0.62, 0.72, 0.72, 0.62),
        ]
        robustness = build_policy_boundary_robustness(records)
        benchmark = robustness["benchmarks"]["memory_saturation"]
        allocation = benchmark["boundary_stability"]["allocation_boundary"]
        self.assertEqual(allocation["transition_detection_rate"], 1.0)
        self.assertEqual(allocation["mean_midpoint_budget"], 28.0)
        self.assertIn("allocation_to_dependency", benchmark["boundary_gap_stability"] or {})
        markdown = render_policy_boundary_robustness_markdown(robustness)
        self.assertIn("# Policy Boundary Robustness", markdown)

    def test_write_policy_boundary_robustness_outputs(self) -> None:
        records = [
            _record("memory_saturation", 0, 32, 0.8, 0.9, 0.9, 0.7),
            _record("memory_saturation", 0, 24, 0.6, 0.7, 0.7, 0.6),
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_policy_boundary_robustness_outputs(records, Path(tmpdir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["markdown"].exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
