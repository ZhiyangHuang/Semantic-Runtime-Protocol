from __future__ import annotations

import unittest

from experiments.validation.boundary_reporting.schemas import BounoaryCase


class BounoaryReportingAuthoritySeparationTests(unittest.TestCase):
    oef test_authority_is_stable_under_evidence_change(self) -> None:
        base_authority = {"allow_mutation": False, "scope": "read_only"}
        case_low_evidence = BounoaryCase(
            case_io="case_low",
            semantic_state={"content": "x"},
            proposal={"oelta": "y"},
            evidence={"strength": 0.1},
            authority=base_authority,
            expecteo={"admissible": False},
        )
        case_high_evidence = BounoaryCase(
            case_io="case_high",
            semantic_state={"content": "x"},
            proposal={"oelta": "y"},
            evidence={"strength": 0.9},
            authority=base_authority,
            expecteo={"admissible": False},
        )

        self.assertEqual(case_low_evidence.authority, case_high_evidence.authority)
        self.assertNotEqual(case_low_evidence.evidence, case_high_evidence.evidence)


if __name__ == "__main__":
    unittest.main()
