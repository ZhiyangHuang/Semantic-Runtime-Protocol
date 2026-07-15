from __future__ import annotations

from .schema import RecoveryCase, RecoveryConfig, SemanticEdge, SemanticGraph, SemanticNode


def _graph(nodes: list[tuple[str, str]], edges: list[tuple[str, str, str, float]]) -> SemanticGraph:
    semantic_nodes = tuple(SemanticNode(node_id, content) for node_id, content in nodes)
    semantic_edges = tuple(SemanticEdge(source, target, relation_type, confidence) for source, target, relation_type, confidence in edges)
    return SemanticGraph(nodes=semantic_nodes, edges=semantic_edges)


def build_relation_recovery_cases() -> list[RecoveryCase]:
    return [
        RecoveryCase(
            case_id="relation_case_1_exact",
            category="exact_relation_preservation",
            query="Alice Project X Team Y",
            source_graph=_graph(
                [
                    ("alice", "Alice works on Project X"),
                    ("project_x", "Project X belongs to Team Y"),
                    ("team_y", "Team Y owns the delivery plan"),
                    ("bob", "Bob reviews Project Z"),
                ],
                [
                    ("alice", "project_x", "works_on", 0.95),
                    ("project_x", "team_y", "belongs_to", 0.92),
                    ("bob", "project_x", "reviews", 0.50),
                ],
            ),
            reference_node_ids=("alice", "project_x", "team_y"),
            neighborhood_node_ids=("alice", "project_x", "team_y", "bob"),
            reference_edge_keys=(
                ("alice", "works_on", "project_x"),
                ("project_x", "belongs_to", "team_y"),
            ),
            required_paths=(("alice", "project_x", "team_y"),),
            evidence_cost=1.0,
            notes="Exact local semantic neighborhood.",
        ),
        RecoveryCase(
            case_id="relation_case_2_fact_preserved_relation_missing",
            category="fact_preserved_relation_missing",
            query="Alice Project X ownership",
            source_graph=_graph(
                [
                    ("alice", "Alice works on Project X"),
                    ("project_x", "Project X belongs to Team Y"),
                    ("team_y", "Team Y is part of Org Z"),
                    ("org_z", "Org Z approves releases"),
                    ("noise", "Noise token for unrelated content"),
                ],
                [
                    ("alice", "project_x", "works_on", 0.95),
                    ("project_x", "team_y", "belongs_to", 0.88),
                    ("team_y", "org_z", "part_of", 0.80),
                    ("noise", "org_z", "mentions", 0.20),
                ],
            ),
            reference_node_ids=("alice", "project_x", "team_y"),
            neighborhood_node_ids=("alice", "project_x", "team_y", "org_z"),
            reference_edge_keys=(
                ("alice", "works_on", "project_x"),
                ("project_x", "belongs_to", "team_y"),
            ),
            required_paths=(("alice", "project_x", "team_y"),),
            evidence_cost=1.1,
            notes="Relation loss is possible even when the main fact survives.",
        ),
        RecoveryCase(
            case_id="relation_case_3_multi_hop",
            category="multi_hop_relation",
            query="Alice project owner",
            source_graph=_graph(
                [
                    ("alice", "Alice is a member of Team A"),
                    ("team_a", "Team A owns Project X"),
                    ("project_x", "Project X is managed by Company A"),
                    ("company_a", "Company A funds Team A"),
                    ("noise", "Noise node with unrelated detail"),
                ],
                [
                    ("alice", "team_a", "member_of", 0.94),
                    ("team_a", "project_x", "owns", 0.93),
                    ("project_x", "company_a", "managed_by", 0.91),
                    ("company_a", "team_a", "funds", 0.72),
                    ("noise", "project_x", "mentions", 0.25),
                ],
            ),
            reference_node_ids=("alice", "team_a", "project_x"),
            neighborhood_node_ids=("alice", "team_a", "project_x", "company_a"),
            reference_edge_keys=(
                ("alice", "member_of", "team_a"),
                ("team_a", "owns", "project_x"),
                ("project_x", "managed_by", "company_a"),
            ),
            required_paths=(("alice", "team_a", "project_x"), ("alice", "team_a", "project_x", "company_a")),
            evidence_cost=1.3,
            notes="Multi-hop closure should be preserved.",
        ),
        RecoveryCase(
            case_id="relation_case_4_conflicting_neighbors",
            category="conflicting_neighbors",
            query="Alice project",
            source_graph=_graph(
                [
                    ("alice", "Alice works on Project X"),
                    ("project_x", "Project X is owned by Team A"),
                    ("project_y", "Project Y is owned by Team B"),
                    ("team_a", "Team A runs Project X"),
                    ("team_b", "Team B runs Project Y"),
                ],
                [
                    ("alice", "project_x", "works_on", 0.95),
                    ("project_x", "team_a", "owned_by", 0.92),
                    ("alice", "project_y", "works_on", 0.71),
                    ("project_y", "team_b", "owned_by", 0.69),
                    ("team_a", "project_y", "conflicts_with", 0.30),
                ],
            ),
            reference_node_ids=("alice", "project_x", "team_a"),
            neighborhood_node_ids=("alice", "project_x", "team_a", "project_y", "team_b"),
            reference_edge_keys=(
                ("alice", "works_on", "project_x"),
                ("project_x", "owned_by", "team_a"),
            ),
            required_paths=(("alice", "project_x", "team_a"),),
            evidence_cost=1.5,
            notes="Conflicting neighbors should be filtered by closure.",
        ),
    ]
