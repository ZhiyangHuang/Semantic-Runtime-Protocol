from __future__ import annotations

import json
from typing import Dict, Iterable, List


def _list_block(values: Iterable[str]) -> str:
    items = [str(item).strip() for item in values if str(item).strip()]
    if not items:
        return "- none"
    return "\n".join(f"- {item}" for item in items)


def build_compression_prompt(
    memory: str,
    constraints: Iterable[str],
    global_vocabulary: Iterable[str],
    local_vocabulary: Iterable[str],
    term_map: Dict[str, str],
    loss_notes: Iterable[str],
    policy: Dict[str, str],
) -> str:
    schema = {
        "memory_summary": "compressed semantic memory",
        "constraints": ["preserved constraints"],
        "anchor_terms": ["stable terms"],
        "term_map": {"surface": "canonical"},
        "loss_risks": ["possible information loss"],
    }
    return "\n".join(
        [
            "Compress semantic state. Return only one compact JSON object, no markdown, no explanation.",
            "Schema:",
            json.dumps(schema, ensure_ascii=False),
            "",
            "Rules:",
            "- Start with { and end with }.",
            "- memory_summary: concrete facts from Memory, not task description.",
            "- constraints: preserve supplied constraints.",
            "- anchor_terms: names, dates, places, entities, option-critical terms.",
            "- loss_risks: possible lost facts.",
            "",
            "Policy:",
            json.dumps(policy, ensure_ascii=False),
            "",
            "Constraints:",
            _list_block(constraints),
            "",
            "Global vocabulary:",
            _list_block(global_vocabulary),
            "",
            "Local vocabulary:",
            _list_block(local_vocabulary),
            "",
            "Term map:",
            json.dumps(term_map, ensure_ascii=False),
            "",
            "Loss notes:",
            _list_block(loss_notes),
            "",
            "Memory:",
            memory,
        ]
    )


def build_recovery_prompt(
    memory: str,
    constraints: Iterable[str],
    global_vocabulary: Iterable[str],
    local_vocabulary: Iterable[str],
    term_map: Dict[str, str],
    loss_notes: Iterable[str],
    policy: Dict[str, str],
    semantic_object_inventory: Dict[str, object] | None = None,
    anchor_memory: str = "",
) -> str:
    vocabulary = list(dict.fromkeys([str(item).strip() for item in list(global_vocabulary) + list(local_vocabulary) if str(item).strip()]))[:8]
    compact_policy = {
        key: str(value).strip()
        for key, value in policy.items()
        if str(key).strip() and str(value).strip()
    }
    return "\n".join(
        [
            "Recover concise semantic state.",
            "Do not answer the benchmark question.",
            "Preserve typed objects, constraints, and evidence links when possible.",
            "Prefer a structured JSON state package if possible; otherwise return plain text facts only.",
            "",
            "Policy:",
            json.dumps(compact_policy, ensure_ascii=False),
            "",
            "Semantic object inventory:",
            json.dumps(semantic_object_inventory or {}, ensure_ascii=False),
            "",
            "Structured state package schema:",
            json.dumps(
                {
                    "schema_version": "structured_state_package.v1",
                    "fields": [
                        "memory",
                        "constraints",
                        "global_vocabulary",
                        "local_vocabulary",
                        "term_map",
                        "policy",
                        "semantic_object_inventory",
                        "typed_representation",
                    ],
                },
                ensure_ascii=False,
            ),
            "",
            "Constraints:",
            _list_block(constraints),
            "",
            "Vocabulary:",
            _list_block(vocabulary),
            "",
            "Term map:",
            json.dumps(term_map, ensure_ascii=False),
            "",
            "Known loss risks:",
            _list_block(loss_notes),
            "",
            "Anchor memory tail:",
            anchor_memory,
            "",
            "Compressed memory:",
            memory,
        ]
    )
