import tempfile
import unittest
from pathlib import Path

from experiments.srp_runtime_legacy.run_fixed_harnesses import run_fixed_harness_bundle, write_fixed_harness_bundle_outputs


class TestFixedHarnessBundle(unittest.TestCase):
    def test_fixed_harness_bundle_runs_all_harnesses(self):
        bundle = run_fixed_harness_bundle(["controlled", "recovery", "reconstruction", "object_aware_compression"], cycles=1)
        self.assertIn("controlled", bundle["harnesses"])
        self.assertIn("recovery", bundle["harnesses"])
        self.assertIn("reconstruction", bundle["harnesses"])
        self.assertIn("object_aware_compression", bundle["harnesses"])
        self.assertGreaterEqual(bundle["harnesses"]["controlled"]["summary"]["records"], 1)
        self.assertGreaterEqual(bundle["harnesses"]["object_aware_compression"]["summary"]["records"], 1)

    def test_fixed_harness_bundle_writes_manifest_and_subdirs(self):
        bundle = run_fixed_harness_bundle(["controlled", "object_aware_compression"], cycles=1)
        with tempfile.TemporaryDirectory() as tmpdir:
            outputs = write_fixed_harness_bundle_outputs(bundle, Path(tmpdir))
            self.assertTrue(outputs["manifest"].exists())
            self.assertTrue((Path(tmpdir) / "controlled" / "controlled_harness_summary.md").exists())
            self.assertTrue((Path(tmpdir) / "object_aware_compression" / "object_aware_compression_summary.md").exists())


if __name__ == "__main__":
    unittest.main()
