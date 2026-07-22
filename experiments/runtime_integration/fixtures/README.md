# Runtime Integration Fixtures

This directory holds frozen replay fixtures for the SRP v1.1 runtime integration scaffold.

The primary fixture is:

- `semantic_transition_replay_v1.json`

Run it with:

```bash
python -m experiments.runtime_integration.runner --mode replay --fixture experiments/runtime_integration/fixtures/semantic_transition_replay_v1.json
```

Each replay run writes a `runtime_integration_manifest.json` alongside the report files. The manifest records the fixture hash, runtime contract, adapter name, and governance policy so the replay boundary stays auditable.
