from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LLMTransitionScenario:
    name: str
    description: str
    kind: str
    state_before: dict[str, Any]
    conversation: str
    expected_decision: bool
    reference_delta: dict[str, Any]
    reference_evidence: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "kind": self.kind,
            "state_before": dict(self.state_before),
            "conversation": self.conversation,
            "expected_decision": self.expected_decision,
            "reference_delta": dict(self.reference_delta),
            "reference_evidence": dict(self.reference_evidence),
            "metadata": dict(self.metadata),
        }


def _base_state(preference: str | None, authority_level: str = "user") -> dict[str, Any]:
    memory = ["User preferences are tracked as governed semantic state."]
    facts: dict[str, Any] = {}
    if preference is not None:
        memory.append(f"User prefers {preference}.")
        facts["user_prefers"] = preference
    return {
        "memory": memory,
        "facts": facts,
        "authority_level": authority_level,
        "state_version": 0,
    }


def build_llm_transition_scenarios() -> list[LLMTransitionScenario]:
    return [
        LLMTransitionScenario(
            name="valid_update",
            description="A supported preference update with enough evidence to admit the transition.",
            kind="valid",
            state_before=_base_state("tea"),
            conversation="I prefer tea over coffee.",
            expected_decision=True,
            reference_delta={
                "state_patch": {
                    "memory": [
                        "User preferences are tracked as governed semantic state.",
                        "User prefers tea.",
                        "Preference confirmed: tea over coffee.",
                    ],
                    "facts": {"user_prefers": "tea"},
                    "state_version": 1,
                },
                "confidence": 0.95,
            },
            reference_evidence={
                "verification_score": 0.95,
                "sources": [
                    {
                        "source": "conversation_turn_12",
                        "content": "I prefer tea over coffee.",
                    }
                ],
            },
            metadata={
                "scenario_group": "supported_preference_update",
            },
        ),
        LLMTransitionScenario(
            name="unsupported_update",
            description="The proposal overreaches beyond the evidence available in the conversation.",
            kind="unsupported",
            state_before=_base_state(None),
            conversation="I like coffee.",
            expected_decision=False,
            reference_delta={
                "state_patch": {
                    "memory": [
                        "User preferences are tracked as governed semantic state.",
                        "User likes espresso every morning.",
                    ],
                    "facts": {"user_prefers": "espresso"},
                    "state_version": 1,
                },
                "confidence": 0.2,
            },
            reference_evidence={
                "verification_score": 0.2,
                "sources": [
                    {
                        "source": "conversation_turn_4",
                        "content": "I like coffee.",
                    }
                ],
            },
            metadata={
                "scenario_group": "unsupported_inference",
            },
        ),
        LLMTransitionScenario(
            name="contradictory_update",
            description="The proposal conflicts with an already established preference and lacks enough evidence.",
            kind="contradictory",
            state_before=_base_state("tea"),
            conversation="Actually, I prefer coffee now.",
            expected_decision=False,
            reference_delta={
                "state_patch": {
                    "memory": [
                        "User preferences are tracked as governed semantic state.",
                        "User prefers tea.",
                        "User now prefers coffee.",
                    ],
                    "facts": {"user_prefers": "coffee"},
                    "state_version": 1,
                },
                "confidence": 0.3,
            },
            reference_evidence={
                "verification_score": 0.3,
                "sources": [
                    {
                        "source": "conversation_turn_18",
                        "content": "Actually, I prefer coffee now.",
                    }
                ],
            },
            metadata={
                "scenario_group": "contradictory_preference_update",
            },
        ),
    ]
