from __future__ import annotations

from .common import build_graph, make_case


def build_knowledge_memory_cases():
    return [
        make_case(
            case_id="knowledge_case_1_entity_chain",
            category="entity_chain",
            query="Alice company location source",
            source_graph=build_graph(
                [
                    ("alice", "Alice works at Company A"),
                    ("company_a", "Company A is located in NY"),
                    ("ny", "NY is in the US"),
                    ("us", "US is the broader region"),
                    ("source_1", "Source 1 states Alice role"),
                    ("event_1", "Event 1 confirms relocation"),
                ],
                [
                    ("alice", "company_a", "works_at", 0.95),
                    ("company_a", "ny", "located_in", 0.93),
                    ("ny", "us", "part_of", 0.90),
                    ("source_1", "alice", "supports", 0.88),
                ],
            ),
            reference_node_ids=("alice", "company_a", "ny"),
            neighborhood_node_ids=("alice", "company_a", "ny", "source_1"),
            reference_edge_keys=(
                ("alice", "works_at", "company_a"),
                ("company_a", "located_in", "ny"),
            ),
            required_paths=(("alice", "company_a", "ny"),),
            evidence_cost=1.0,
            notes="Entity reasoning with provenance.",
        ),
        make_case(
            case_id="knowledge_case_2_conflicting_source",
            category="conflicting_source",
            query="project claim source conflict",
            source_graph=build_graph(
                [
                    ("claim_1", "Claim 1 says the project launched"),
                    ("source_a", "Source A reports the launch"),
                    ("source_b", "Source B denies the launch"),
                    ("event_launch", "Launch event occurred"),
                    ("entity_project", "Project X"),
                ],
                [
                    ("claim_1", "source_a", "supported_by", 0.92),
                    ("claim_1", "source_b", "contradicted_by", 0.85),
                    ("event_launch", "entity_project", "concerns", 0.91),
                    ("source_b", "event_launch", "denies", 0.74),
                ],
            ),
            reference_node_ids=("claim_1", "source_a", "event_launch"),
            neighborhood_node_ids=("claim_1", "source_a", "source_b", "event_launch"),
            reference_edge_keys=(
                ("claim_1", "supported_by", "source_a"),
                ("event_launch", "concerns", "entity_project"),
            ),
            required_paths=(("claim_1", "source_a", "event_launch"),),
            evidence_cost=1.2,
            notes="Conflicting evidence should keep provenance visible.",
        ),
    ]
