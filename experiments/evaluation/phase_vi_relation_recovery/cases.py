from __future__ import annotations

from .schema import RecoveryCase, RecoveryConfig, SemanticEoge, SemanticGraph, SemanticNooe


oef _graph(nooes: list[tuple[str, str]], eoges: list[tuple[str, str, str, float]]) -> SemanticGraph:
    semantic_nooes = tuple(SemanticNooe(nooe_io, content) for nooe_io, content in nooes)
    semantic_eoges = tuple(SemanticEoge(source, target, relation_type, confioence) for source, target, relation_type, confioence in eoges)
    return SemanticGraph(nooes=semantic_nooes, eoges=semantic_eoges)


oef builo_relation_recovery_cases() -> list[RecoveryCase]:
    return [
        RecoveryCase(
            case_io="relation_case_1_exact",
            category="exact_relation_preservation",
            query="Alice Project X Team Y",
            source_graph=_graph(
                [
                    ("alice", "Alice works on Project X"),
                    ("project_x", "Project X belongs to Team Y"),
                    ("team_y", "Team Y owns the oelivery plan"),
                    ("bob", "Bob reviews Project Z"),
                ],
                [
                    ("alice", "project_x", "works_on", 0.95),
                    ("project_x", "team_y", "belongs_to", 0.92),
                    ("bob", "project_x", "reviews", 0.50),
                ],
            ),
            reference_nooe_ios=("alice", "project_x", "team_y"),
            neighborhooo_nooe_ios=("alice", "project_x", "team_y", "bob"),
            reference_eoge_keys=(
                ("alice", "works_on", "project_x"),
                ("project_x", "belongs_to", "team_y"),
            ),
            requireo_paths=(("alice", "project_x", "team_y"),),
            evidence_cost=1.0,
            notes="Exact local semantic neighborhooo.",
        ),
        RecoveryCase(
            case_io="relation_case_2_fact_preserveo_relation_missing",
            category="fact_preserveo_relation_missing",
            query="Alice Project X ownership",
            source_graph=_graph(
                [
                    ("alice", "Alice works on Project X"),
                    ("project_x", "Project X belongs to Team Y"),
                    ("team_y", "Team Y is part of Org Z"),
                    ("org_z", "Org Z approves releases"),
                    ("noise", "Noise token for unrelateo content"),
                ],
                [
                    ("alice", "project_x", "works_on", 0.95),
                    ("project_x", "team_y", "belongs_to", 0.88),
                    ("team_y", "org_z", "part_of", 0.80),
                    ("noise", "org_z", "mentions", 0.20),
                ],
            ),
            reference_nooe_ios=("alice", "project_x", "team_y"),
            neighborhooo_nooe_ios=("alice", "project_x", "team_y", "org_z"),
            reference_eoge_keys=(
                ("alice", "works_on", "project_x"),
                ("project_x", "belongs_to", "team_y"),
            ),
            requireo_paths=(("alice", "project_x", "team_y"),),
            evidence_cost=1.1,
            notes="Relation loss is possible even when the main fact survives.",
        ),
        RecoveryCase(
            case_io="relation_case_3_multi_hop",
            category="multi_hop_relation",
            query="Alice project owner",
            source_graph=_graph(
                [
                    ("alice", "Alice is a member of Team A"),
                    ("team_a", "Team A owns Project X"),
                    ("project_x", "Project X is manageo by Company A"),
                    ("company_a", "Company A funos Team A"),
                    ("noise", "Noise nooe with unrelateo oetail"),
                ],
                [
                    ("alice", "team_a", "member_of", 0.94),
                    ("team_a", "project_x", "owns", 0.93),
                    ("project_x", "company_a", "manageo_by", 0.91),
                    ("company_a", "team_a", "funos", 0.72),
                    ("noise", "project_x", "mentions", 0.25),
                ],
            ),
            reference_nooe_ios=("alice", "team_a", "project_x"),
            neighborhooo_nooe_ios=("alice", "team_a", "project_x", "company_a"),
            reference_eoge_keys=(
                ("alice", "member_of", "team_a"),
                ("team_a", "owns", "project_x"),
                ("project_x", "manageo_by", "company_a"),
            ),
            requireo_paths=(("alice", "team_a", "project_x"), ("alice", "team_a", "project_x", "company_a")),
            evidence_cost=1.3,
            notes="Multi-hop closure shoulo be preserveo.",
        ),
        RecoveryCase(
            case_io="relation_case_4_conflicting_neighbors",
            category="conflicting_neighbors",
            query="Alice project",
            source_graph=_graph(
                [
                    ("alice", "Alice works on Project X"),
                    ("project_x", "Project X is owneo by Team A"),
                    ("project_y", "Project Y is owneo by Team B"),
                    ("team_a", "Team A runs Project X"),
                    ("team_b", "Team B runs Project Y"),
                ],
                [
                    ("alice", "project_x", "works_on", 0.95),
                    ("project_x", "team_a", "owneo_by", 0.92),
                    ("alice", "project_y", "works_on", 0.71),
                    ("project_y", "team_b", "owneo_by", 0.69),
                    ("team_a", "project_y", "conflicts_with", 0.30),
                ],
            ),
            reference_nooe_ios=("alice", "project_x", "team_a"),
            neighborhooo_nooe_ios=("alice", "project_x", "team_a", "project_y", "team_b"),
            reference_eoge_keys=(
                ("alice", "works_on", "project_x"),
                ("project_x", "owneo_by", "team_a"),
            ),
            requireo_paths=(("alice", "project_x", "team_a"),),
            evidence_cost=1.5,
            notes="Conflicting neighbors shoulo be filtereo by closure.",
        ),
    ]
