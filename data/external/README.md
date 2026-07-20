# External Evaluation Registry

This directory records external evaluation sources that may be adapted into SRP
boundary evidence.

It is a registry, not a dataset mirror.

The repository stores source metadata, adapter mappings, and provenance notes.
It does not store benchmark payloads.

Current registered source families include:

- LongMemEval
- LoCoMo
- AgentBench
- reasoning sources

Each registered source also carries a `transition_role` that describes the kind
of semantic pressure it applies to SRP.

## Registry Rule

External sources are consumed as semantic transition inputs and translated into
the shared `BoundaryCase` contract.

They are not evaluated here as benchmark tasks.

## Transition Role

Each external evaluation source is registered with a `transition_role` field.

The role describes the type of semantic transition pressure introduced by the
source. It does not represent benchmark capability, performance ranking, or
model quality.

Current roles:

| Source Family | Transition Role | Purpose |
| --- | --- | --- |
| LongMemEval | `evidence_update` | Evaluate evidence-driven semantic updates |
| LoCoMo | `temporal_state_evolution` | Evaluate time-dependent semantic transitions |
| AgentBench | `action_proposal` | Evaluate action-oriented transition proposals |
| Reasoning | `inference_proposal` | Evaluate inference-generated candidate transitions |

The transition role is only used for adapter routing and governance evidence
organization.
It does not define authority, correctness, or mutation permission.
