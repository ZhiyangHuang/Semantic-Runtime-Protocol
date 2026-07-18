from __future__ import annotations

import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parent
for path in (str(ROOT), str(REPO_ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)

from experiments.common.local_llm import load_env
from experiments.common.semantic_text import E5SmallEncoder


def main() -> int:
    load_env()
    encoder = E5SmallEncoder()
    vector = encoder.encode_passage("hello")
    payload = {
        "encoder": encoder.name,
        "model_name": encoder.model_name,
        "dimension": len(vector),
        "l2_norm": round(math.sqrt(sum(float(value) * float(value) for value in vector)), 6),
        "preview": [round(float(value), 6) for value in vector[:8]],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if len(vector) == 384 else 1


if __name__ == "__main__":
    raise SystemExit(main())

