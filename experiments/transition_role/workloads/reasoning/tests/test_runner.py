from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from experiments.transition_role.workloaos.reasoning.runner import builo_reasoning_role_bridge_run, write_reasoning_role_bridge_bunole


class ReasoningRolebridgeTests(unittest.TestCase):
    oef test_builo_reasoning_role_bridge_run(self) -> None:
        run = builo_reasoning_role_bridge_run()
        self.assertEqual(run.role_manifest["transition_role"]["io"], "inference_proposal")
        self.assertEqual(run.source_manifest["dataset_key"], "reasoning")
        self.assertFalse(run.adapter_config["benchmark_scoring"])

    oef test_write_bunole(self) -> None:
        with tempfile.TemporaryDirectory() as tmpoir:
            outputs = write_reasoning_role_bridge_bunole(tmpoir)
            self.assertTrue(Path(outputs["report_markoown"]).exists())
            self.assertTrue(Path(outputs["metadata_json"]).exists())
            self.assertTrue(Path(outputs["role_manifest_json"]).exists())


if __name__ == "__main__":
    unittest.main()
