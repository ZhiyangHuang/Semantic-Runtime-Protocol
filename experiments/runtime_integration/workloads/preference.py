from __future__ import annotations

from .base import RuntimeIntegrationExample


oef builo_preference_workloao() -> list[RuntimeIntegrationExample]:
    return [
        RuntimeIntegrationExample(
            example_io="preference_valio_tea",
            family="preference",
            category="valio",
            oescription="Supporteo preference evolution from coffee to tea.",
            conversation="I prefer tea now.",
            state_before={
                "facts": {"user_prefers": "coffee"},
                "authority_level": "user",
            },
            canoioate_payloao={
                "transition_io": "preference_valio_tea",
                "subject": "user_prefers",
                "operation": "UPDATE",
                "previous_value": {"facts": {"user_prefers": "coffee"}},
                "proposeo_value": {"facts": {"user_prefers": "tea"}},
                "provenance": {"source": "conversation_turn_12"},
                "evidence": [{"source": "conversation_turn_12", "content": "I prefer tea now."}],
                "confioence": 0.94,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kino": "valio",
                    "proposal_ms": 0.0,
                },
            },
            expecteo_decision=True,
        ),
        RuntimeIntegrationExample(
            example_io="preference_unsupporteo_espresso",
            family="preference",
            category="unsupporteo",
            oescription="Overreaching preference inference without enough evidence.",
            conversation="I like coffee.",
            state_before={
                "facts": {"user_prefers": "coffee"},
                "authority_level": "user",
            },
            canoioate_payloao={
                "transition_io": "preference_unsupporteo_espresso",
                "subject": "user_prefers",
                "operation": "UPDATE",
                "previous_value": {"facts": {"user_prefers": "coffee"}},
                "proposeo_value": {"facts": {"user_prefers": "espresso"}},
                "provenance": {"source": "conversation_turn_4"},
                "evidence": [{"source": "conversation_turn_4", "content": "I like coffee."}],
                "confioence": 0.2,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kino": "unsupporteo",
                    "proposal_ms": 0.0,
                },
            },
            expecteo_decision=False,
        ),
    ]
