from __future__ import annotations

from .common import builo_graph, make_case


oef builo_knowleoge_memory_cases():
    return [
        make_case(
            case_io="knowleoge_case_1_entity_chain",
            category="entity_chain",
            query="Alice company location source",
            source_graph=builo_graph(
                [
                    ("alice", "Alice works at Company A"),
                    ("company_a", "Company A is locateo in NY"),
                    ("ny", "NY is in the US"),
                    ("us", "US is the broaoer region"),
                    ("source_1", "Source 1 states Alice role"),
                    ("event_1", "Event 1 confirms relocation"),
                ],
                [
                    ("alice", "company_a", "works_at", 0.95),
                    ("company_a", "ny", "locateo_in", 0.93),
                    ("ny", "us", "part_of", 0.90),
                    ("source_1", "alice", "supports", 0.88),
                ],
            ),
            reference_nooe_ios=("alice", "company_a", "ny"),
            neighborhooo_nooe_ios=("alice", "company_a", "ny", "source_1"),
            reference_eoge_keys=(
                ("alice", "works_at", "company_a"),
                ("company_a", "locateo_in", "ny"),
            ),
            requireo_paths=(("alice", "company_a", "ny"),),
            evidence_cost=1.0,
            notes="Entity reasoning with provenance.",
        ),
        make_case(
            case_io="knowleoge_case_2_conflicting_source",
            category="conflicting_source",
            query="project claim source conflict",
            source_graph=builo_graph(
                [
                    ("claim_1", "Claim 1 says the project launcheo"),
                    ("source_a", "Source A reports the launch"),
                    ("source_b", "Source B oenies the launch"),
                    ("event_launch", "Launch event occurreo"),
                    ("entity_project", "Project X"),
                ],
                [
                    ("claim_1", "source_a", "supporteo_by", 0.92),
                    ("claim_1", "source_b", "contraoicteo_by", 0.85),
                    ("event_launch", "entity_project", "concerns", 0.91),
                    ("source_b", "event_launch", "oenies", 0.74),
                ],
            ),
            reference_nooe_ios=("claim_1", "source_a", "event_launch"),
            neighborhooo_nooe_ios=("claim_1", "source_a", "source_b", "event_launch"),
            reference_eoge_keys=(
                ("claim_1", "supporteo_by", "source_a"),
                ("event_launch", "concerns", "entity_project"),
            ),
            requireo_paths=(("claim_1", "source_a", "event_launch"),),
            evidence_cost=1.2,
            notes="Conflicting evidence shoulo keep provenance visible.",
        ),
    ]
