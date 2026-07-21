from __future__ import annotations

import unittest

from experiments.benchmarks.common import BenchmarkRunConfig
from experiments.benchmarks.longmemeval.adapter import LongMemEvalBridgeAdapter
from experiments.external_validation.benchmarks import LongMemEvalAdapter as ExternalLongMemEvalAdapter


class LongMemEvalBridgeAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = LongMemEvalBridgeAdapter()
        self.external_adapter = ExternalLongMemEvalAdapter()

    def test_case_normalization(self) -> None:
        external_cases = self.external_adapter.load_cases(sample_limit=1)
        self.assertTrue(external_cases)
        bridge_case = self.adapter.normalize_case(external_cases[0], BenchmarkRunConfig(benchmark_name="longmemeval", dataset_version="2025", model="m", prompt_format="p"))

        self.assertEqual(bridge_case.benchmark_name, "longmemeval")
        self.assertEqual(bridge_case.case_id, external_cases[0].case_id)
        self.assertEqual(bridge_case.prompt, external_cases[0].query)
        self.assertEqual(bridge_case.expected_answer, external_cases[0].expected_answer)
        self.assertEqual(bridge_case.reference_answer, external_cases[0].expected_answer)
        self.assertEqual(bridge_case.choices, ())

    def test_metadata_preservation(self) -> None:
        external_case = self.external_adapter.load_cases(sample_limit=1)[0]
        metadata = self.adapter.build_metadata(external_case)

        self.assertEqual(metadata["bridge"]["official_scorer"], "external_validation")
        self.assertEqual(metadata["bridge"]["runtime_contract"], "external_validation_runtime_contract_v1")
        self.assertEqual(metadata["bridge"]["payload_policy"], "not_stored_in_repository")
        self.assertEqual(metadata["release_source"]["dataset_key"], "longmemeval")
        self.assertIn("adapter_registration", metadata)
        self.assertNotIn("expected_answer", metadata)
        self.assertNotIn("reference_answer", metadata)

    def test_scorer_ownership_preservation(self) -> None:
        external_case = self.external_adapter.load_cases(sample_limit=1)[0]
        bridge_case = self.adapter.normalize_case(external_case)
        prompt = self.adapter.build_prompt(bridge_case, "srp")

        self.assertIn("official_scorer: external_validation", prompt)
        self.assertNotIn(external_case.expected_answer, prompt)
        self.adapter.validate_prompt_leakage(bridge_case, "srp", prompt)

    def test_no_payload_assumptions(self) -> None:
        external_case = self.external_adapter.load_cases(sample_limit=1)[0]
        bridge_case = self.adapter.normalize_case(external_case)

        self.assertEqual(bridge_case.metadata["bridge"]["payload_policy"], "not_stored_in_repository")
        self.assertEqual(bridge_case.metadata["bridge"]["source"], "experiments.external_validation")
        self.assertEqual(bridge_case.metadata["bridge"]["official_scorer"], "external_validation")


if __name__ == "__main__":
    unittest.main()

