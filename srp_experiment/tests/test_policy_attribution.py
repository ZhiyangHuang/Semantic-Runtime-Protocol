from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.analysis.policy_attribution import (
    summarize_policy_attribution,
    write_policy_attribution_outputs,
)


class PolicyAttributionTest(unittest.TestCase):
    def _record(self) -> dict:
        return {
            "task_id": "policy-task",
            "cycle": 1,
            "compression_suite": "policy-suite",
            "compression_scenario": "policy-test",
            "source_size": 100,
            "compressed_size": 40,
            "compression_ratio": 0.4,
            "policy_flat": {
                "schema_version": "policy_spec_flat.v1",
                "lifecycle_retained_importance": 0.35,
                "lifecycle_retained_passes": 2,
                "lifecycle_archived_importance": 0.3,
                "lifecycle_archived_drift_count": 2,
                "lifecycle_archived_failure_count": 2,
                "lifecycle_decayed_floor": 0.05,
                "lifecycle_decayed_multiplier": 0.92,
            },
            "source_package": {
                "policy_flat": {
                    "schema_version": "policy_spec_flat.v1",
                    "lifecycle_retained_importance": 0.35,
                    "lifecycle_retained_passes": 2,
                    "lifecycle_archived_importance": 0.3,
                    "lifecycle_archived_drift_count": 2,
                    "lifecycle_archived_failure_count": 2,
                    "lifecycle_decayed_floor": 0.05,
                    "lifecycle_decayed_multiplier": 0.92,
                },
                "semantic_object_inventory": {
                    "objects": [
                        {
                            "object_id": "constraint:001",
                            "type": "constraint",
                            "value": "John must keep the key",
                            "confidence": 1.0,
                            "evidence_pointer": "constraint:1",
                        },
                        {
                            "object_id": "fact:001",
                            "type": "fact",
                            "value": "Mary bought milk yesterday",
                            "confidence": 0.55,
                            "evidence_pointer": "memory:2",
                        },
                        {
                            "object_id": "goal:001",
                            "type": "goal",
                            "value": "Keep the key",
                            "confidence": 0.95,
                            "evidence_pointer": "memory:1",
                        },
                    ],
                    "important_objects": [
                        {
                            "object_id": "constraint:001",
                            "type": "constraint",
                            "value": "John must keep the key",
                            "confidence": 1.0,
                            "evidence_pointer": "constraint:1",
                        }
                    ],
                },
                "runtime_metadata": {
                    "constraint:001": {"importance": 0.92, "confidence": 0.98, "verification_passes": 3, "verification_failures": 0, "drift_count": 0, "lifecycle_state": "active"},
                    "fact:001": {"importance": 0.12, "confidence": 0.45, "verification_passes": 0, "verification_failures": 1, "drift_count": 1, "lifecycle_state": "decayed"},
                    "goal:001": {"importance": 0.58, "confidence": 0.7, "verification_passes": 1, "verification_failures": 0, "drift_count": 0, "lifecycle_state": "active"},
                },
            },
            "compressed_package": {
                "semantic_object_inventory": {
                    "objects": [
                        {
                            "object_id": "constraint:001",
                            "type": "constraint",
                            "value": "John must keep the key",
                        }
                    ]
                }
            },
        }

    def test_summarize_policy_attribution(self) -> None:
        summary = summarize_policy_attribution([self._record()])
        self.assertEqual(summary["records"], 1)
        self.assertEqual(summary["records_with_traces"], 1)
        self.assertGreater(summary["root_cause"]["budget_pressure"], 0.0)
        self.assertIn("chunk_budget_pressure", summary["reason_counts"])

    def test_write_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outputs = write_policy_attribution_outputs([self._record()], tmp)
            for key in ["json", "markdown", "trace", "root_cause_markdown"]:
                self.assertTrue(Path(outputs[key]).exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
