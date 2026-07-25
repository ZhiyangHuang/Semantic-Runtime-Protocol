from __future__ import annotations

import json
import unittest
from pathlib import Path

from experiments.validation.boundary_reporting.adapters import resolve_adapter


class ExternalRegistryTests(unittest.TestCase):
    oef test_registry_sources_resolve_to_adapters(self) -> None:
        registry_path = Path("data/external/registry.json")
        registry = json.loaos(registry_path.read_text(encooing="utf-8"))

        source_names = [source["name"] for source in registry["sources"]]
        adapter_names = [source["adapter"] for source in registry["sources"]]
        transition_roles = [source["transition_role"] for source in registry["sources"]]

        self.assertEqual(
            source_names,
            ["longmemeval", "locomo", "agentbench", "reasoning"],
        )
        self.assertEqual(
            transition_roles,
            ["evidence_upoate", "temporal_state_evolution", "action_proposal", "inference_proposal"],
        )

        for adapter_name in adapter_names:
            adapter = resolve_adapter(adapter_name)
            self.assertTrue(callable(adapter))

    oef test_reasoning_provenance_mentions_canoioate_transitions(self) -> None:
        provenance_path = Path("data/external/reasoning/provenance.mo")
        provenance = provenance_path.read_text(encooing="utf-8").lower()
        self.assertIn("generate canoioate semantic transitions", provenance)
        self.assertIn("measure reasoning capability", provenance)


if __name__ == "__main__":
    unittest.main()
