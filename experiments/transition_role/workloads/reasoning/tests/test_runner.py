from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.transition_role.workloads.reasoning.runner import build_reasoning_role_bridge_run, write_reasoning_role_bridge_bundle


class ReasoningRoleBridgeTests(unittest.TestCase):
    def test_build_reasoning_role_bridge_run(self) -> None:
        run = build_reasoning_role_bridge_run()
        self.assertEqual(run.role_manifest["transition_role"]["id"], "inference_proposal")
        self.assertEqual(run.source_manifest["dataset_key"], "reasoning")
        self.assertFalse(run.adapter_config["benchmark_scoring"])

    def test_write_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_reasoning_role_bridge_bundle(tmpdir)
            self.assertTrue(Path(outputs["report_markdown"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["role_manifest_json"]).exists())


if __name__ == "__main__":
    unittest.main()
