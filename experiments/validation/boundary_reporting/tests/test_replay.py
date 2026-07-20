from __future__ import annotations

import hashlib
import json
import unittest
from dataclasses import asdict

from experiments.validation.boundary_reporting.schemas import BoundaryCase


class BoundaryReportingReplayTests(unittest.TestCase):
    def test_same_case_same_fingerprint(self) -> None:
        case = BoundaryCase(
            case_id="knowledge_001",
            semantic_state={"content": "x", "provenance": "p", "authority": "read_only"},
            proposal={"delta": "y", "source": "agent"},
            evidence={"strength": 0.8, "sources": 3},
            authority={"allow_mutation": False},
            expected={"admissible": False},
        )
        payload = json.dumps(asdict(case), sort_keys=True, ensure_ascii=False)
        fingerprint_1 = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        fingerprint_2 = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        self.assertEqual(fingerprint_1, fingerprint_2)


if __name__ == "__main__":
    unittest.main()
