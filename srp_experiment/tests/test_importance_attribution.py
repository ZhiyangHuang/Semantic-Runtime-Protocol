from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.analysis.importance_attribution import (
    summarize_importance_attribution,
    write_importance_attribution_outputs,
)


class ImportanceAttributionTest(unittest.TestCase):
    def _record(self) -> dict:
        return {
            "task_id": "synthetic-task",
            "cycle": 1,
            "compression_suite": "synthetic",
            "compression_scenario": "importance-test",
            "source_package": {
                "memory": "John must keep the key. Mary needs the door unlocked. User asked about the key.",
                "constraints": ["John must keep the key"],
                "semantic_dependencies": {
                    "required_dependency_objects": [
                        {
                            "subject": {"canonical": "John"},
                            "relation": {"canonical": "owns"},
                            "object": {"canonical": "key"},
                        }
                    ]
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
                            "object_id": "goal:001",
                            "type": "goal",
                            "value": "Keep the key",
                            "confidence": 0.95,
                            "evidence_pointer": "memory:1",
                        },
                        {
                            "object_id": "fact:001",
                            "type": "fact",
                            "value": "Mary bought milk yesterday",
                            "confidence": 0.55,
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
            "runtime_metadata_snapshot": {
                "constraint:001": {"importance": 0.92, "confidence": 0.98, "lifecycle_state": "active"},
                "goal:001": {"importance": 0.58, "confidence": 0.7, "lifecycle_state": "active"},
                "fact:001": {"importance": 0.12, "confidence": 0.45, "lifecycle_state": "decayed"},
            },
        }

    def test_summarize_importance_attribution(self) -> None:
        summary = summarize_importance_attribution([self._record()])
        self.assertEqual(summary["records"], 1)
        self.assertEqual(summary["records_with_traces"], 1)
        self.assertGreater(summary["mean_observed_importance"], 0.0)
        self.assertEqual(summary["root_cause"]["dominant_low_importance_reason"], "not_task_salient")
        self.assertIn("goal_relevance", summary["component_means"])

    def test_write_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            outputs = write_importance_attribution_outputs([self._record()], tmp)
            for key in ["json", "markdown", "trace", "root_cause_markdown"]:
                self.assertTrue(Path(outputs[key]).exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
