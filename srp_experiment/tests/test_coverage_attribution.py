import tempfile
import unittest
from pathlib import Path

from experiments.analysis.coverage_attribution import (
    load_coverage_attribution_records,
    summarize_coverage_attribution,
    write_coverage_attribution_outputs,
)
from experiments.analysis.semantic_snapshot import build_stage_snapshots


def _record() -> dict:
    return {
        "task_id": "coverage-task",
        "source_package": {
            "memory": "John bought milk. Only John can enter room A.",
            "semantic_object_inventory": {
                "objects": [
                    {"object_id": "entity:john", "type": "entity", "value": "John", "confidence": 0.9, "evidence_pointer": "memory:1"},
                    {"object_id": "fact:milk", "type": "fact", "value": "milk", "confidence": 0.8, "evidence_pointer": "memory:1"},
                ]
            },
            "semantic_dependencies": {
                "required_dependency_objects": [
                    {
                        "dependency_id": "d1",
                        "subject": {"canonical": "John", "type": "entity"},
                        "relation": {"canonical": "bought", "type": "relation"},
                        "object": {"canonical": "milk", "type": "entity"},
                    }
                ]
            },
            "constraints": ["Only John can enter room A."],
        },
        "semantic_runtime_graph": {
            "schema_version": "semantic_runtime_graph.v1.5",
            "nodes": [
                {"id": "entity:john", "type": "entity", "label": "John", "identity": {"canonical_name": "John", "aliases": [], "entity_key": "entity:john"}, "attributes": {"properties": {}, "state": {}}, "lifecycle": {"created": True, "modified": True, "compressed": True, "recovered": True, "verified": True, "retained": True}},
                {"id": "fact:milk", "type": "fact", "label": "milk", "identity": {"canonical_name": "milk", "aliases": [], "entity_key": "fact:milk"}, "attributes": {"properties": {}, "state": {}}, "lifecycle": {"created": True, "modified": True, "compressed": True, "recovered": True, "verified": True, "retained": True}},
            ],
            "edges": [
                {"source": "entity:john", "target": "fact:milk", "relation": "bought", "confidence": 0.9},
            ],
        },
        "compressed_package": {
            "memory": "John bought milk.",
            "semantic_object_inventory": {
                "objects": [
                    {"object_id": "entity:john", "type": "entity", "value": "John", "confidence": 0.9, "evidence_pointer": "memory:1"},
                ]
            },
            "semantic_dependencies": {
                "required_dependency_objects": []
            },
            "constraints": [],
        },
        "recovered_package": {
            "typed_representation": {
                "objects": [
                    {"object_id": "entity:john", "type": "entity", "value": "John", "confidence": 0.9, "evidence_pointer": "memory:1"},
                ]
            }
        },
        "validation": {
            "coverage_score": 0.5,
            "passed": False,
            "object_alignment": {
                "entity": {
                    "matches": [
                        {"source_object_id": "entity:john", "recovered_object_id": "entity:john", "similarity": 1.0, "object_type": "entity", "source_value": "John"},
                    ]
                }
            },
            "dependency_audit": {
                "matched_objects": ["entity:john"],
            },
        },
        "validation_coverage": 0.5,
        "graph_integrity_score": 0.6,
        "dependency_recall": 0.5,
    }


class TestCoverageAttribution(unittest.TestCase):
    def test_build_stage_snapshots_and_summary(self):
        record = _record()
        snapshots = build_stage_snapshots(record)
        self.assertIn("source", snapshots)
        self.assertIn("representation", snapshots)
        self.assertIn("compression", snapshots)
        self.assertIn("recovery", snapshots)
        self.assertIn("validation", snapshots)
        summary = summarize_coverage_attribution([record])
        self.assertEqual(summary["records"], 1)
        self.assertEqual(summary["records_with_snapshots"], 1)
        self.assertIn("stagewise_loss_matrix", summary)
        self.assertIn("root_cause", summary)
        markdown = __import__("experiments.analysis.coverage_attribution", fromlist=["render_coverage_attribution_markdown"]).render_coverage_attribution_markdown(summary)
        self.assertIn("# Coverage Attribution", markdown)
        self.assertIn("Stagewise Loss Matrix", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_coverage_attribution_outputs([record], Path(tmpdir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["markdown"].exists())
            self.assertTrue(outputs["matrix_csv"].exists())
            self.assertTrue(outputs["semantic_snapshot_trace"].exists())
            self.assertTrue(outputs["semantic_delta_trace"].exists())
            self.assertTrue(outputs["root_cause_markdown"].exists())

    def test_load_coverage_attribution_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "records.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            records = load_coverage_attribution_records(path)
            self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
