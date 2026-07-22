from __future__ import annotations

from .base import RuntimeIntegrationExample


def build_preference_workload() -> list[RuntimeIntegrationExample]:
    return [
        RuntimeIntegrationExample(
            example_id="preference_valid_tea",
            family="preference",
            category="valid",
            description="Supported preference evolution from coffee to tea.",
            conversation="I prefer tea now.",
            state_before={
                "facts": {"user_prefers": "coffee"},
                "authority_level": "user",
            },
            candidate_payload={
                "transition_id": "preference_valid_tea",
                "subject": "user_prefers",
                "operation": "UPDATE",
                "previous_value": {"facts": {"user_prefers": "coffee"}},
                "proposed_value": {"facts": {"user_prefers": "tea"}},
                "provenance": {"source": "conversation_turn_12"},
                "evidence": [{"source": "conversation_turn_12", "content": "I prefer tea now."}],
                "confidence": 0.94,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kind": "valid",
                    "proposal_ms": 0.0,
                },
            },
            expected_decision=True,
        ),
        RuntimeIntegrationExample(
            example_id="preference_unsupported_espresso",
            family="preference",
            category="unsupported",
            description="Overreaching preference inference without enough evidence.",
            conversation="I like coffee.",
            state_before={
                "facts": {"user_prefers": "coffee"},
                "authority_level": "user",
            },
            candidate_payload={
                "transition_id": "preference_unsupported_espresso",
                "subject": "user_prefers",
                "operation": "UPDATE",
                "previous_value": {"facts": {"user_prefers": "coffee"}},
                "proposed_value": {"facts": {"user_prefers": "espresso"}},
                "provenance": {"source": "conversation_turn_4"},
                "evidence": [{"source": "conversation_turn_4", "content": "I like coffee."}],
                "confidence": 0.2,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kind": "unsupported",
                    "proposal_ms": 0.0,
                },
            },
            expected_decision=False,
        ),
    ]
