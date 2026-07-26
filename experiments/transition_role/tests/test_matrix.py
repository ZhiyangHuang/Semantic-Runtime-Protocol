from __future__ import annotations

import unittest
from pathlib import Path

from experiments.transition_role.validate_matrix import validate_transition_role_matrix


class TransitionRoleMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix_path = Path("experiments/transition_role/validation_matrix.json")
        self.roles_path = Path("experiments/transition_role/registry.yaml")
        self.external_path = Path("data/external/registry.json")

    def test_matrix_is_valid(self) -> None:
        report = validate_transition_role_matrix(self.matrix_path, self.roles_path, self.external_path)
        self.assertTrue(report.valid, msg=report.errors)
        self.assertEqual(report.details["row_count"], 4)


if __name__ == "__main__":
    unittest.main()
