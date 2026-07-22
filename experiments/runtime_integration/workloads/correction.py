from __future__ import annotations

from .base import RuntimeIntegrationExample


def build_correction_workload() -> list[RuntimeIntegrationExample]:
    return [
        RuntimeIntegrationExample(
            example_id="correction_valid_move",
            family="correction",
            category="valid",
            description="Supported fact correction from Boston to New York.",
            conversation="I moved to New York.",
            state_before={
                "facts": {"location": "Boston"},
                "authority_level": "user",
            },
            candidate_payload={
                "transition_id": "correction_valid_move",
                "subject": "location",
                "operation": "UPDATE",
                "previous_value": {"facts": {"location": "Boston"}},
                "proposed_value": {"facts": {"location": "New York"}},
                "provenance": {"source": "conversation_turn_20"},
                "evidence": [{"source": "conversation_turn_20", "content": "I moved to New York."}],
                "confidence": 0.9,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kind": "valid",
                    "proposal_ms": 0.0,
                },
            },
            expected_decision=True,
        ),
        RuntimeIntegrationExample(
            example_id="correction_unsupported_la",
            family="correction",
            category="unsupported",
            description="Unsupported fact rewrite without enough evidence.",
            conversation="I may have moved recently.",
            state_before={
                "facts": {"location": "Boston"},
                "authority_level": "user",
            },
            candidate_payload={
                "transition_id": "correction_unsupported_la",
                "subject": "location",
                "operation": "UPDATE",
                "previous_value": {"facts": {"location": "Boston"}},
                "proposed_value": {"facts": {"location": "Los Angeles"}},
                "provenance": {"source": "conversation_turn_7"},
                "evidence": [{"source": "conversation_turn_7", "content": "I may have moved recently."}],
                "confidence": 0.35,
                "timestamp": "2026-07-22T00:00:00Z",
                "metadata": {
                    "transition_kind": "unsupported",
                    "proposal_ms": 0.0,
                },
            },
            expected_decision=False,
        ),
    ]
