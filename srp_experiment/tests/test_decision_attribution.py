import tempfile
import unittest
from pathlib import Path

from srp_experiment.analysis.decision_attribution import (
    load_decision_attribution_records,
    summarize_decision_attribution,
    write_decision_attribution_outputs,
)
from srp_experiment.analysis.decision_trace import build_compression_decision_trace


def _record() -> dict:
    return {
        "task_id": "decision-task",
        "compression_suite": "branching_dependency_chunk_score_plus_object_support",
        "compression_scenario": "branching_dependency",
        "object_support_enabled": True,
        "source_package": {
            "memory": "Alpha keeps the key. Beta keeps the red key. The room is quiet.",
            "constraints": ["Alpha keeps the key."],
            "semantic_object_inventory": {
                "objects": [
                    {"object_id": "entity:alpha", "type": "entity", "value": "Alpha", "confidence": 0.95, "evidence_pointer": "memory:1"},
                    {"object_id": "fact:key", "type": "fact", "value": "the key", "confidence": 0.92, "evidence_pointer": "memory:1"},
                    {"object_id": "fact:quiet", "type": "fact", "value": "The room is quiet", "confidence": 0.2, "evidence_pointer": "memory:3"},
                ]
            },
        },
        "compressed_package": {
            "memory": "Alpha keeps the key.",
            "constraints": ["Alpha keeps the key."],
            "semantic_object_inventory": {
                "objects": [
                    {"object_id": "entity:alpha", "type": "entity", "value": "Alpha", "confidence": 0.95, "evidence_pointer": "memory:1"},
                ]
            },
        },
        "selected_chunk_ids": [1],
        "chunk_selection": [
            {"chunk_id": 1, "text": "Alpha keeps the key.", "score": 0.91, "rule_score": 0.91, "embedding_score": None, "reason": "rule=0.910; high_saliency"},
        ],
        "chunk_selection_scores": [0.91],
        "chunk_selection_reasons": ["rule=0.910; high_saliency"],
        "chunk_selection_factors": [
            {
                "schema_version": "saliency_factors.v1",
                "scores": {
                    "constraint_overlap": 1.0,
                    "expected_keyword_overlap": 0.0,
                    "rule_boost": 0.2,
                    "object_support_score": 0.1,
                    "object_support_count": 1,
                    "embedding_score": None,
                    "rule_score": 0.91,
                },
                "signals": {"constraint_count": 1, "expected_keyword_count": 0},
                "flags": {
                    "has_date_or_month": False,
                    "has_acronym": False,
                    "has_digit": False,
                    "has_constraint_language": True,
                    "capitalized_start": True,
                },
            }
        ],
        "runtime_metadata_snapshot": {
            "entity:alpha": {"importance": 0.95, "confidence": 0.95, "lifecycle_state": "active"},
            "fact:key": {"importance": 0.88, "confidence": 0.92, "lifecycle_state": "active"},
            "fact:quiet": {"importance": 0.15, "confidence": 0.2, "lifecycle_state": "active"},
        },
        "validation_coverage": 0.4,
        "weighted_object_retention": 0.7,
        "graph_integrity_score": 0.5,
    }


class TestDecisionAttribution(unittest.TestCase):
    def test_build_compression_decision_trace(self):
        trace = build_compression_decision_trace(_record())
        self.assertEqual(trace["schema_version"], "compression_decision_trace.v1")
        self.assertIn("chunk_trace", trace)
        self.assertIn("object_trace", trace)
        self.assertIn("summary", trace)
        self.assertIn("root_cause", trace)
        self.assertGreaterEqual(trace["summary"]["source_object_count"], 1)
        self.assertGreaterEqual(trace["summary"]["dropped_object_count"], 1)
        self.assertIn("dropped_low_importance", trace["summary"]["object_reason_counts"])
        self.assertIn("keep", {item["decision"] for item in trace["chunk_trace"]})

    def test_summary_and_outputs(self):
        record = _record()
        summary = summarize_decision_attribution([record])
        self.assertEqual(summary["records"], 1)
        self.assertIn("branching_dependency", summary["scenarios"])
        markdown = __import__("srp_experiment.analysis.decision_attribution", fromlist=["render_decision_attribution_markdown"]).render_decision_attribution_markdown(summary)
        self.assertIn("# Decision Attribution", markdown)
        self.assertIn("Scenario Summary", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_decision_attribution_outputs([record], Path(tmpdir))
            self.assertTrue(outputs["json"].exists())
            self.assertTrue(outputs["markdown"].exists())
            self.assertTrue(outputs["trace"].exists())
            self.assertTrue(outputs["root_cause_markdown"].exists())

    def test_load_decision_attribution_records(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "records.jsonl"
            path.write_text("{}\n", encoding="utf-8")
            records = load_decision_attribution_records(path)
            self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
