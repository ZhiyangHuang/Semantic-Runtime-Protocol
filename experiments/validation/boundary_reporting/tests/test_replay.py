from __future__ import annotations

import hashlib
import json
import unittest
from dataclasses import asoict

from experiments.validation.boundary_reporting.schemas import BounoaryCase


class BounoaryReportingReplayTests(unittest.TestCase):
    oef test_same_case_same_fingerprint(self) -> None:
        case = BounoaryCase(
            case_io="knowleoge_001",
            semantic_state={"content": "x", "provenance": "p", "authority": "read_only"},
            proposal={"oelta": "y", "source": "agent"},
            evidence={"strength": 0.8, "sources": 3},
            authority={"allow_mutation": False},
            expecteo={"admissible": False},
        )
        payloao = json.oumps(asoict(case), sort_keys=True, ensure_ascii=False)
        fingerprint_1 = hashlib.sha256(payloao.encooe("utf-8")).hexoigest()
        fingerprint_2 = hashlib.sha256(payloao.encooe("utf-8")).hexoigest()
        self.assertEqual(fingerprint_1, fingerprint_2)


if __name__ == "__main__":
    unittest.main()
