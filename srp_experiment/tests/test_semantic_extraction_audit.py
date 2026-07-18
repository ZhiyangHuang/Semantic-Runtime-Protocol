import tempfile
import unittest
from pathlib import Path

from experiments.analysis.semantic_extraction_audit import (
    render_semantic_extraction_audit_markdown,
    summarize_semantic_extraction_audit,
    write_semantic_extraction_audit_outputs,
)


def _graph_node(node_id: str, *, v1_5: bool) -> dict:
    node = {
        "id": node_id,
        "type": "fact",
        "label": node_id,
        "confidence": 0.9,
        "lifecycle": {
            "created": True,
            "modified": bool(v1_5),
            "compressed": True,
            "recovered": True,
            "verified": True,
            "retained": True,
            "source_present": True,
            "recovered_present": True,
        },
        "attributes": {
            "evidence_pointer": "memory:1",
            "source_present": True,
            "recovered_present": True,
            "object_origin": "source",
            "metadata": {},
        },
    }
    if v1_5:
        node["identity"] = {
            "canonical_name": node_id,
            "aliases": [node_id],
            "entity_key": node_id,
        }
        node["attributes"]["properties"] = {"origin": "source"}
        node["attributes"]["state"] = {"retained": True}
    return node


def _record(group: str, *, v1_5: bool) -> dict:
    source_package = {
        "semantic_object_inventory": {
            "objects": [
                {"object_id": "fact:1", "type": "fact", "value": "A", "confidence": 0.9, "evidence_pointer": "m:1"},
                {"object_id": "fact:2", "type": "fact", "value": "B", "confidence": 0.9, "evidence_pointer": "m:2"},
            ]
        },
        "semantic_dependencies": {
            "required_dependency_objects": [
                {"dependency_id": "d1", "subject": {"canonical": "A", "type": "entity"}, "relation": {"canonical": "rel", "type": "relation"}, "object": {"canonical": "B", "type": "entity"}},
                {"dependency_id": "d2", "subject": {"canonical": "B", "type": "entity"}, "relation": {"canonical": "rel", "type": "relation"}, "object": {"canonical": "A", "type": "entity"}},
            ]
        },
        "constraints": ["Only A matters."],
    }
    graph = {
        "schema_version": "semantic_runtime_graph.v1.5" if v1_5 else "semantic_runtime_graph.v1",
        "root_id": "semantic_runtime_graph::root",
        "nodes": [
            {"id": "semantic_runtime_graph::root", "type": "graph_root", "label": "semantic_runtime_graph", "lifecycle": {"created": True, "modified": False, "compressed": True, "recovered": True, "verified": True, "retained": True}, "attributes": {"properties": {}, "state": {}}},
            _graph_node("fact:1", v1_5=v1_5),
            _graph_node("fact:2", v1_5=v1_5),
            {"id": "contract::1", "type": "contract_constraint", "label": "Only A matters.", "lifecycle": {"created": True, "modified": False, "compressed": True, "recovered": False, "verified": False, "retained": False}, "attributes": {"properties": {}, "state": {}}},
            {"id": "contract::2", "type": "contract_semantic_dependency_tuple", "label": "A rel B", "lifecycle": {"created": True, "modified": False, "compressed": True, "recovered": False, "verified": False, "retained": False}, "attributes": {"properties": {}, "state": {}}},
            {"id": "contract::3", "type": "contract_semantic_dependency_tuple", "label": "B rel A", "lifecycle": {"created": True, "modified": False, "compressed": True, "recovered": False, "verified": False, "retained": False}, "attributes": {"properties": {}, "state": {}}},
        ],
        "edges": [
            {"edge_id": "e1", "source": "semantic_runtime_graph::root", "target": "fact:1", "relation": "contains", "lifecycle": {}},
            {"edge_id": "e2", "source": "semantic_runtime_graph::root", "target": "fact:2", "relation": "contains", "lifecycle": {}},
        ],
        "lifecycle": {},
        "summary": {},
    }
    return {
        "graph_representation_group": group,
        "graph_representation_version": "v1.5" if v1_5 else "v1",
        "graph_schema_version": "semantic_runtime_graph.v1.5" if v1_5 else "semantic_runtime_graph.v1",
        "graph_recovery_scenario": "dependency_chain",
        "source_package": source_package,
        "semantic_runtime_graph": graph,
        "recovered_state_package": {
            "typed_representation": {
                "objects": [
                    {"object_id": "fact:1", "type": "fact", "value": "A", "confidence": 0.9, "evidence_pointer": "m:1"},
                ]
            }
        },
        "semantic_graph_validation": {
            "dependency_recall": 0.5,
            "graph_integrity_score": 0.5 if not v1_5 else 0.8,
        },
        "validation_coverage": 0.4,
    }


class TestSemanticExtractionAudit(unittest.TestCase):
    def test_semantic_extraction_audit_detects_v1_5_gain(self):
        records = [_record("C", v1_5=False), _record("D", v1_5=True)]
        summary = summarize_semantic_extraction_audit(records)
        self.assertIn("graph_v1_5_minus_graph_v1", summary["comparison"])
        delta = summary["comparison"]["graph_v1_5_minus_graph_v1"]
        self.assertEqual(delta["node_capture_rate"], 0.0)
        self.assertEqual(delta["relation_capture_rate"], 0.0)
        self.assertEqual(delta["constraint_capture_rate"], 0.0)
        self.assertEqual(delta["attribute_completeness"], 1.0)
        self.assertEqual(delta["provenance_completeness"], 0.0)
        markdown = render_semantic_extraction_audit_markdown(summary)
        self.assertIn("# Semantic Extraction Audit", markdown)
        self.assertIn("Representation Delta", markdown)
        with tempfile.TemporaryDirectory() as tmpdir:
            output_paths = write_semantic_extraction_audit_outputs(records, Path(tmpdir))
            self.assertTrue(output_paths["jsonl"].exists())
            self.assertTrue(output_paths["csv"].exists())
            self.assertTrue(output_paths["markdown"].exists())
            self.assertTrue(output_paths["summary"].exists())
            self.assertTrue(output_paths["json"].exists())


if __name__ == "__main__":
    unittest.main()
