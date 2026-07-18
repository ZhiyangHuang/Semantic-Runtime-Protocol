from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def load_locomo_samples(data_root: str | Path | None = None, sample_limit: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = Path(data_root) if data_root else Path(__file__).resolve().parents[4] / "data" / "locomo"
    path = root / "locomo10.json"
    if not path.exists():
        return [], {
            "dataset": "LoCoMo",
            "version": "bridge-fallback",
            "samples": 0,
            "source": str(path),
            "source_hash": "",
        }

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        payload = [payload]

    if sample_limit and sample_limit > 0:
        payload = payload[:sample_limit]

    manifest = {
        "dataset": "LoCoMo",
        "version": "locomo10.json",
        "samples": len(payload),
        "source": str(path),
        "source_hash": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    return [item for item in payload if isinstance(item, dict)], manifest


def build_turn_index(sample: dict[str, Any]) -> dict[str, dict[str, Any]]:
    conversation = dict(sample.get("conversation", {}))
    turn_index: dict[str, dict[str, Any]] = {}
    for session_key in sorted(
        [key for key in conversation.keys() if key.startswith("session_") and not key.endswith("_date_time")],
        key=lambda key: int(key.split("_", 2)[1]),
    ):
        session_turns = conversation.get(session_key, [])
        session_date_time = str(conversation.get(f"{session_key}_date_time", ""))
        for position, turn in enumerate(session_turns):
            if not isinstance(turn, dict):
                continue
            dia_id = str(turn.get("dia_id", f"{session_key}:{position}"))
            turn_index[dia_id] = {
                "dia_id": dia_id,
                "speaker": str(turn.get("speaker", "")),
                "text": str(turn.get("text", "")),
                "session_key": session_key,
                "session_index": int(session_key.split("_", 2)[1]),
                "session_date_time": session_date_time,
                "position": position,
            }
    return turn_index


def collect_raw_context(turn_index: dict[str, dict[str, Any]], evidence_ids: list[str], window: int = 1) -> tuple[list[str], list[str]]:
    raw_context: list[str] = []
    source_turn_ids: list[str] = []
    if not turn_index:
        return raw_context, source_turn_ids

    by_session: dict[str, list[dict[str, Any]]] = {}
    for turn in turn_index.values():
        by_session.setdefault(turn["session_key"], []).append(turn)
    for turns in by_session.values():
        turns.sort(key=lambda item: item["position"])

    for evidence_id in evidence_ids:
        turn = turn_index.get(str(evidence_id))
        if turn is None:
            continue
        source_turn_ids.append(turn["dia_id"])
        session_turns = by_session.get(turn["session_key"], [])
        pos = int(turn["position"])
        start = max(0, pos - window)
        stop = min(len(session_turns), pos + window + 1)
        for neighbor in session_turns[start:stop]:
            snippet = f'{neighbor["dia_id"]} | {neighbor["speaker"]}: {neighbor["text"]}'
            if snippet not in raw_context:
                raw_context.append(snippet)
    return raw_context, source_turn_ids

