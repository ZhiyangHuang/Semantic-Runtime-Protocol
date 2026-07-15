from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from experiments.config import (
    PhaseIIIAOptimizationConfig,
    SemanticBackendComparisonConfig,
    load_experiment_config,
    load_phase_iii_a_config,
    load_semantic_backend_comparison_config,
)
from experiments.optimization.phase_iii_a_round1.runner import run_phase_iii_a_round1_optimization


class ConfigLoaderTest(unittest.TestCase):
    def test_load_phase_iii_a_config(self) -> None:
        config = load_phase_iii_a_config()

        self.assertIsInstance(config, PhaseIIIAOptimizationConfig)
        self.assertEqual(config.phase, "phase_iii_a")
        self.assertEqual(config.parameter_axes, ("activation_threshold", "recovery_min_evidence"))
        self.assertEqual(config.activation_threshold_values, (0.3, 0.4, 0.5, 0.6, 0.7, 0.8))
        self.assertEqual(config.recovery_min_evidence_values, (1, 2, 3))
        self.assertFalse(config.runtime_mutation_allowed)
        self.assertTrue(config.governance_approval_required)

    def test_load_semantic_backend_comparison_config(self) -> None:
        config = load_semantic_backend_comparison_config()

        self.assertIsInstance(config, SemanticBackendComparisonConfig)
        self.assertEqual(config.phase, "evaluation_study")
        self.assertEqual(config.experiment_name, "semantic_backend_comparison")
        self.assertEqual(config.baseline_backend, "vector")
        self.assertEqual(config.variant_backend, "vector_local_model")
        self.assertEqual(config.verification_backend, "vector_local_model")
        self.assertTrue(config.local_model_enabled)
        self.assertTrue(config.fallback_to_heuristic)
        self.assertEqual(config.local_model_name, "Qwen/Qwen3-4B-AWQ")

    def test_load_experiment_config_dispatch(self) -> None:
        config = load_experiment_config("phase_iii_a")
        self.assertIsInstance(config, PhaseIIIAOptimizationConfig)

    def test_round1_optimization_accepts_config(self) -> None:
        config = load_phase_iii_a_config()
        result = run_phase_iii_a_round1_optimization(config=config)

        self.assertEqual(len(result["candidates"]), 18)
        self.assertEqual(result["report"]["recommended_configuration"]["activation_threshold"], 0.8)
        self.assertEqual(result["report"]["recommended_configuration"]["recovery_min_evidence"], 1)


if __name__ == "__main__":
    unittest.main()
