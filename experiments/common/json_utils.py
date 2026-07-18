from __future__ import annotations

import json
import re


def extract_json_object(raw_text: str):
    cleaned = str(raw_text).strip()
    if not cleaned:
        raise json.JSONDecodeError("empty response", cleaned, 0)

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start < 0:
        raise json.JSONDecodeError("no JSON object found", cleaned, 0)

    depth = 0
    in_string = False
    escape = False
    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(cleaned[start : index + 1])

    raise json.JSONDecodeError("unterminated JSON object", cleaned, start)

