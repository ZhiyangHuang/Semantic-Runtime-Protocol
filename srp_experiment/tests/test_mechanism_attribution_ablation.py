from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from srp_experiment.mechanism_ablation.ablation_metrics import summarize_mechanism_ablation_records
from srp_experiment.mechanism_ablation.ablation_runner import run_mechanism_attribution_ablation, write_mechanism_attribution_outputs
from srp_experiment.mechanism_ablation.variants.baseline import MechanismAblationBaselinePolicy
from srp_experiment.mechanism_ablation.variants.remove_importance_weighting import MechanismAblationNoImportancePolicy
from srp_experiment.mechanism_ablation.variants.remove_dependency_retention import MechanismAblationNoDependencyPolicy


class TestMechanismAttributionAblation(unittest.TestCase):
    def test_variant_policies_are_distinct(self) -> None:
        baseline = MechanismAblationBaselinePolicy()
        no_importance = MechanismAblationNoImportancePolicy()
        ablated = MechanismAblationNoDependencyPolicy()
        self.assertNotEqual(baseline.name, ablated.name)
        self.assertNotEqual(baseline.name, no_importance.name)
        self.assertTrue(baseline.include_dependency)
        self.assertTrue(baseline.include_importance)
        self.assertFalse(no_importance.include_importance)
        self.assertTrue(no_importance.include_dependency)
        self.assertFalse(ablated.include_dependency)

    def test_summarize_mechanism_ablation_records_detects_shift(self) -> None:
        records = []
        for variant, budget, dependency_coverage, dependency_f1, validation_score, active_retention in [
            ("baseline", 24, 0.9, 0.8, 0.92, 0.75),
            ("baseline", 16, 0.7, 0.6, 0.81, 0.5),
            ("remove_importance_weighting", 24, 0.88, 0.78, 0.9, 0.72),
            ("remove_importance_weighting", 16, 0.68, 0.58, 0.79, 0.48),
            ("remove_dependency_retention", 24, 0.8, 0.7, 0.88, 0.75),
            ("remove_dependency_retention", 16, 0.5, 0.4, 0.7, 0.5),
        ]:
            records.append(
                {
                    "mechanism_ablation_variant": variant,
                    "mechanism_ablation_suite": "memory_saturation",
                    "mechanism_ablation_budget": budget,
                    "mechanism_ablation": {
                        "semantic_unit_count": 48,
                        "semantic_pressure_index": 48 / budget,
                    },
                    "validation_coverage": validation_score - 0.05,
                    "dependency_coverage": dependency_coverage,
                    "dependency_precision": dependency_f1,
                    "dependency_f1": dependency_f1,
                    "validation_score": validation_score,
                    "graph_integrity_score": 0.9,
                    "object_retention": 0.85,
                    "weighted_object_retention": 0.8,
                    "state_allocation_result": {
                        "metrics": {
                            "active_object_count": int(budget / 2),
                            "active_state_efficiency": 1.0 / budget,
                            "active_retention_ratio": active_retention,
                            "latent_preservation": 0.5,
                            "hallucination_isolation": 0.75,
                        }
                    },
                }
            )
        summary = summarize_mechanism_ablation_records(records)
        self.assertEqual(summary["records"], 6)
        self.assertIn("baseline", summary["variants"])
        self.assertIn("remove_importance_weighting", summary["variants"])
        self.assertIn("remove_dependency_retention", summary["variants"])
        self.assertIn("comparisons", summary)
        self.assertIn("remove_importance_weighting", summary["comparisons"])
        self.assertIn("remove_dependency_retention", summary["comparisons"])
        comparison = summary["comparison"]["memory_saturation"]
        self.assertIn("allocation_boundary_shift", comparison)
        self.assertIn("budget_delta_table", comparison)
        self.assertIn("attribution_score", comparison)

    def test_run_and_write_outputs(self) -> None:
        records = run_mechanism_attribution_ablation(budgets=[8], seeds=[0], cycles=1)
        self.assertGreater(len(records), 0)
        self.assertIn("mechanism_ablation", records[0])
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_mechanism_attribution_outputs(records, Path(tmpdir))
            self.assertTrue(outputs["comparison_json"].exists())
            self.assertTrue(outputs["comparison_markdown"].exists())
            self.assertTrue(any(key.endswith("_jsonl") for key in outputs))
            self.assertTrue(any("remove_importance_weighting" in key for key in outputs))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
