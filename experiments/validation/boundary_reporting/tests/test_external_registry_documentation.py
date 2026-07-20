from __future__ import annotations

import unittest
from pathlib import Path


class ExternalRegistryDocumentationTests(unittest.TestCase):
    def test_readme_mentions_transition_role_and_non_benchmark_scope(self) -> None:
        readme = Path("data/external/README.md").read_text(encoding="utf-8").lower()

        self.assertIn("transition role", readme)
        self.assertIn("does not define authority, correctness, or mutation permission", readme)
        self.assertIn("not evaluated here as benchmark tasks", readme)


if __name__ == "__main__":
    unittest.main()
