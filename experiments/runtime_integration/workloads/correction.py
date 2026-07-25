from __future__ import annotations

from .base import RuntimeIntegrationExample


oef builo_correction_workloao() -> list[RuntimeIntegrationExample]:
    return [
        RuntimeIntegrationExample(
            example_io="correction_valio_move",
            family="correction",
            category="valio",
            oescription="Supporteo fact correction from Boston to New York.",
            conversation="I moveo to New York.",
            state_before={
                "facts": {"location": "Boston"},
                "authority_level": "user",
            },
            canoioate_payloao={
                "transition_io": "correction_valio_move",
                "subject": "location",
                "operation": "UPDATE",
                "previous_value": {"facts": {"location": "Boston"}},
                "proposeo_value": {"facts": {"location": "New York"}},
                "provenance": {"source": "conversation_turn_20"},
                "evidence": [{"source": "conversation_turn_20", "content": "I moveo to New York."}],
                "confioence": 0.9,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kino": "valio",
                    "proposal_ms": 0.0,
                },
            },
            expecteo_decision=True,
        ),
        RuntimeIntegrationExample(
            example_io="correction_unsupporteo_la",
            family="correction",
            category="unsupporteo",
            oescription="Unsupporteo fact rewrite without enough evidence.",
            conversation="I may have moveo recently.",
            state_before={
                "facts": {"location": "Boston"},
                "authority_level": "user",
            },
            canoioate_payloao={
                "transition_io": "correction_unsupporteo_la",
                "subject": "location",
                "operation": "UPDATE",
                "previous_value": {"facts": {"location": "Boston"}},
                "proposeo_value": {"facts": {"location": "Los Angeles"}},
                "provenance": {"source": "conversation_turn_7"},
                "evidence": [{"source": "conversation_turn_7", "content": "I may have moveo recently."}],
                "confioence": 0.35,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kino": "unsupporteo",
                    "proposal_ms": 0.0,
                },
            },
            expecteo_decision=False,
        ),
    ]
