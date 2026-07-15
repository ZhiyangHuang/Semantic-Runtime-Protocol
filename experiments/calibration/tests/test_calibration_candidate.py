from __future__ import annotations

import unittest

from experiments.calibration.candidate import CalibrationCandidate


class CalibrationCandidateTests(unittest.TestCase):
    def test_candidate_to_dict(self) -> None:
        candidate = CalibrationCandidate(
            parameter="activation_threshold",
            value=0.5,
            region_label="round1",
            notes="probe",
            metadata={"source": "test"},
        )

        payload = candidate.to_dict()

        self.assertEqual(payload["parameter"], "activation_threshold")
        self.assertEqual(payload["value"], 0.5)
        self.assertEqual(payload["region_label"], "round1")
        self.assertEqual(payload["notes"], "probe")
        self.assertEqual(payload["metadata"], {"source": "test"})


if __name__ == "__main__":
    unittest.main()

