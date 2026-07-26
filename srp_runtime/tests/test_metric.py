import unittest

from srp_runtime.metric.semantic_metric import SemanticMetric
from srp_runtime.semantic.graph import SemanticGraph
from srp_runtime.semantic.unit import SemanticUnit


class TestMetric(unittest.TestCase):
    def test_identity_metric_same_unit(self):
        unit = SemanticUnit(
            unit_id="u1",
            canonical_name="car",
            aliases=["auto"],
            lineage=["v1"],
            provenance=["source:1"],
        )
        result = SemanticMetric().distance(unit, unit)
        self.assertEqual(result.total_distance, 0.0)

    def test_alias_similarity_is_lower_than_unrelated(self):
        left = SemanticUnit(
            unit_id="u1",
            canonical_name="car",
            aliases=["auto"],
            semantic_payload={"type": "vehicle"},
        )
        right = SemanticUnit(
            unit_id="u2",
            canonical_name="automobile",
            aliases=["car"],
            semantic_payload={"type": "vehicle"},
        )
        unrelated = SemanticUnit(
            unit_id="u3",
            canonical_name="table",
            semantic_payload={"type": "furniture"},
        )

        metric = SemanticMetric()
        close_distance = metric.distance(left, right).total_distance
        far_distance = metric.distance(left, unrelated).total_distance

        self.assertLess(close_distance, far_distance)

    def test_structural_similarity_uses_graph_context(self):
        graph = SemanticGraph()
        a = SemanticUnit(unit_id="a", canonical_name="A")
        b = SemanticUnit(unit_id="b", canonical_name="B")
        c = SemanticUnit(unit_id="c", canonical_name="C")
        d = SemanticUnit(unit_id="d", canonical_name="D")
        e = SemanticUnit(unit_id="e", canonical_name="E")
        for unit in [a, b, c, d, e]:
            graph.add_unit(unit)
        graph.relation_index["a"] = ["b", "c"]
        graph.relation_index["d"] = ["b", "c"]
        graph.relation_index["e"] = ["c"]

        metric = SemanticMetric()
        similar = metric.distance(a, d, graph=graph).total_distance
        different = metric.distance(a, e, graph=graph).total_distance

        self.assertLess(similar, different)

    def test_metric_deterministic(self):
        left = SemanticUnit(unit_id="u1", canonical_name="car")
        right = SemanticUnit(unit_id="u2", canonical_name="automobile")
        metric = SemanticMetric()

        first = metric.distance(left, right).total_distance
        second = metric.distance(left, right).total_distance

        self.assertEqual(first, second)

