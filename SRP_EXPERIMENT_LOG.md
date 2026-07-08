# SRP Experiment Log

This document records active and recent experiments in a running-log format.

It is separate from `SRP_EXPERIMENT_INDEX.md`, which is the directory, and `SRP_EXPERIMENT_CHECKLIST.md`, which is the execution plan.

---

## Active Research Phase

Current focus:

```text
Recovery Policy Evaluation
```

Primary question:

```text
How should structured semantic state be reconstructed into a compact executable state?
```

Current hypothesis:

- structured semantic state contains sufficient recovery signal
- reconstruction policy controls the tradeoff between fidelity and inflation
- recovery should optimize minimal sufficient state, not maximum expansion

---

## Experiment Family Map

```text
Measurement Infrastructure
 ├── schema freeze
 └── lifecycle

Recovery Source Analysis
 └── text vs structured recovery

Recovery Policy Evaluation
 ├── unrestricted reconstruction
 ├── constrained reconstruction
 └── minimal sufficient reconstruction

Repair Diagnostics
 ├── repair constraint
 ├── repair objective
 └── filter interaction
```

---

## Experiment Records

### Template

```markdown
## <experiment_id>

### Identity

- experiment_id:
- parent_experiment_id:
- research_area:
- status:
- date:

### Research Question

Question:

Hypothesis:

### Configuration

Model:

Task:

Context budget:

Recovery source:

Recovery policy:

Repair:

Filter:

Encoder:

### Metrics

#### Fidelity

- validation_coverage:
- validation_alignment:

#### Object Recovery

- recovered_object_count:
- hallucinated_count:
- object_inflation_ratio:

#### Reconstruction

- reconstruction_precision:
- reconstruction_selectivity:
- minimality_score:
- reconstruction_efficiency:

#### Lifecycle

- source_object_count:
- compressed_object_count:
- recovered_object_count:
- repaired_object_count:

### Interpretation

component tested:

metric changed:

direction:

failure mode:

conclusion:

next action:
```

---

## Active / Recent Entries

### `srp_meas_longbench_state_allocation_policy_r01`

#### Identity

- experiment_id: `srp_meas_longbench_state_allocation_policy_r01`
- parent_experiment_id: `srp_meas_longbench_state_allocation_minimal_r01`
- research_area: `Recovery Policy Evaluation`
- status: `completed`
- date: `2026-07-08`

#### Research Question

Question:

How do unrestricted, constrained, and minimal allocation policies differ when operating on the same recovered state?

Hypothesis:

The three policies should differ primarily in runtime partitioning behavior, while validation coverage remains fixed because allocation is post-reconstruction.

#### Configuration

- Model: `Qwen/Qwen3-4B-AWQ`
- Task: `longbench_v2::66fcffd9bb02136c067c94c5`
- Context budget: `8192`
- Recovery source: `reconstructed_state_package`
- Recovery policy: `unrestricted / constrained / minimal`
- Repair: `disabled`
- Filter: `off`
- Encoder: `current baseline`

#### Metrics

##### Fidelity

- validation_coverage: `0.0021441567858629`
- validation_alignment: `0.0021441567858629`

##### Object Recovery

- recovered_object_count: `7770`
- hallucinated_count: `17` for constrained and minimal; `0` for unrestricted
- object_inflation_ratio: `0.5011933174224343`

##### Allocation

- unrestricted active_object_count: `7770`
- unrestricted latent_object_count: `0`
- unrestricted discard_object_count: `0`
- constrained active_object_count: `2754`
- constrained latent_object_count: `4999`
- constrained discard_object_count: `17`
- minimal active_object_count: `12`
- minimal latent_object_count: `7741`
- minimal discard_object_count: `17`
- active_state_efficiency: `2.759532542938095e-07` / `7.785609244237109e-07` / `0.00017867973215524165`
- latent_preservation: `0.0` / `249.95` / `387.05`
- hallucination_isolation: `1.0` / `0.9979428848015489` / `0.9979428848015489`
- active_retention_ratio: `0.9402226524685382` / `0.33325266214908034` / `0.001452081316553727`

#### Interpretation

- component tested: allocation strategy on a fixed recovered state
- metric changed: active/latent/discard partitioning changed substantially across policies
- direction: unrestricted maximized active retention, constrained introduced a mid-tier split, and minimal compressed active state most aggressively
- failure mode: validation coverage did not move because allocation does not alter reconstructed fidelity
- conclusion: the allocation layer behaves as a runtime partitioning policy, not a fidelity-improvement mechanism
- next action: use allocation metrics to compare runtime compactness and latent retention, not recovery coverage

### `srp_meas_longbench_state_allocation_minimal_r01`

#### Identity

- experiment_id: `srp_meas_longbench_state_allocation_minimal_r01`
- parent_experiment_id: `srp_meas_longbench_recovery_reconstruction_r01`
- research_area: `Recovery Policy Evaluation`
- status: `completed`
- date: `2026-07-08`

#### Research Question

Question:

How should reconstructed semantic state be partitioned into active, latent, and discard runtime memory?

Hypothesis:

A rule-based allocation policy can keep the active runtime state compact while preserving valid latent memory and isolating discardable noise.

#### Configuration

- Model: `Qwen/Qwen3-4B-AWQ`
- Task: `longbench_v2::66fcffd9bb02136c067c94c5`
- Context budget: `8192`
- Recovery source: `reconstructed_state_package`
- Recovery policy: `minimal allocation`
- Repair: `disabled`
- Filter: `off`
- Encoder: `current baseline`

#### Metrics

##### Fidelity

- validation_coverage: `0.0021441567858629`
- validation_alignment: `0.0021441567858629`

##### Object Recovery

- recovered_object_count: `7770`
- hallucinated_count: `17`
- object_inflation_ratio: `0.5011933174224343`

##### Reconstruction

- reconstruction_precision: `n/a`
- reconstruction_selectivity: `n/a`
- minimality_score: `n/a`
- reconstruction_efficiency: `n/a`

##### Lifecycle

- source_object_count: `16491`
- compressed_object_count: `16491`
- recovered_object_count: `7770`
- repaired_object_count: `7770`

#### Interpretation

- component tested: first rule-based semantic runtime allocation
- metric changed: the active runtime state was reduced to 12 objects while latent memory absorbed most valid recovered objects
- direction: active-state compactness increased sharply
- failure mode: validation coverage remained extremely low, so the allocation layer did not improve task fidelity by itself
- conclusion: the initial allocation policy is useful as a partitioning diagnostic, but it is not yet a fidelity-improving policy
- next action: compare unrestricted, constrained, and minimal allocation once the policy family is fully wired into the experimental matrix

### `srp_meas_longbench_recovery_reconstruction_r01`

#### Identity

- experiment_id: `srp_meas_longbench_recovery_reconstruction_r01`
- parent_experiment_id: `srp_meas_longbench_object_lifecycle_r01`
- research_area: `Recovery Source Analysis`
- status: `completed`
- date: `2026-07-07`

#### Research Question

Question:

How much does text grounding versus structured grounding help recovery?

Hypothesis:

Structured grounding should improve validation coverage, but may also increase object expansion unless reconstruction is constrained.

#### Configuration

- Model: `Qwen/Qwen3-4B-AWQ`
- Task: `longbench_v2::671b1335bb02136c067d4e88`
- Context budget: `8192`
- Recovery source: `chunks`, `structured_state_package`, `chunks+structured_state_package`
- Recovery policy: `unrestricted reconstruction`
- Repair: `disabled`
- Filter: `off`
- Encoder: `current baseline`

#### Metrics

##### Fidelity

- validation_coverage: `0.8316345270890685` for `structured_only`; `0.013486829332283604` for `text_only` and `text_plus_structured`
- validation_alignment: `n/a`

##### Object Recovery

- recovered_object_count: `132` for `text_only` and `text_plus_structured`; `1795` for `structured_only`
- hallucinated_count: `132` for `text_only`; `1674` for `structured_only`; `4` for `text_plus_structured`
- object_inflation_ratio: `7.510460251046025` for `structured_only`; `0.5523012552301255` for `text_plus_structured`

##### Reconstruction

- reconstruction_precision: `n/a`
- reconstruction_selectivity: `n/a`
- minimality_score: `n/a`
- reconstruction_efficiency: `0.000102172949486997` for `text_only` and `text_plus_structured`; `0.0004633061432251078` for `structured_only`

##### Lifecycle

- source_object_count: `239`
- compressed_object_count: `239`
- recovered_object_count: `138`
- repaired_object_count: `239`

#### Interpretation

- component tested: recovery source selection
- metric changed: validation coverage and object expansion diverged by reconstruction mode
- direction: structured grounding increased coverage but also expanded the recovered state substantially
- failure mode: hybrid reconstruction did not improve coverage over text-only recovery
- conclusion: structured representation is informative, but recovery policy is still the main control surface
- next action: evaluate reconstruction policy, not additional representation capability

---

### `srp_meas_longbench_object_lifecycle_r01`

#### Identity

- experiment_id: `srp_meas_longbench_object_lifecycle_r01`
- parent_experiment_id: `srp_meas_longbench_structrec_r01`
- research_area: `Measurement Infrastructure`
- status: `completed`
- date: `2026-07-07`

#### Research Question

Question:

Where does semantic degradation occur across the SRP lifecycle?

Hypothesis:

Compression should preserve objects, while reconstruction and repair may introduce inflation or drift.

#### Configuration

- Model: `Qwen/Qwen3-4B-AWQ`
- Task: `longbench_v2::671b1335bb02136c067d4e88`
- Context budget: `8192`
- Recovery objective: `generation`
- Recovery constraint: `unrestricted`
- Filter: `off`
- Encoder: `current baseline`

#### Metrics

##### Fidelity

- validation_coverage: `0.021066050111504232`
- validation_alignment: `0.021066050111504232`

##### Object Recovery

- recovered_object_count: `138`
- hallucinated_count: `17`
- object_inflation_ratio: `0.5774058577405857`

##### Reconstruction

- reconstruction_precision: `n/a`
- reconstruction_selectivity: `n/a`
- minimality_score: `n/a`
- reconstruction_efficiency: `n/a`

##### Lifecycle

- source_object_count: `239`
- compressed_object_count: `239`
- recovered_object_count: `138`
- repaired_object_count: `239`

#### Interpretation

- component tested: lifecycle attribution
- metric changed: source/compressed preserved objects, while recovery introduced the main degradation
- direction: compression recall saturated at 1.0, recovery reduced object count and introduced drift
- failure mode: repair expanded state back to 239 objects without improving task-critical recall
- conclusion: compression is not the bottleneck; reconstruction policy is the bottleneck
- next action: evaluate reconstruction policy

---

## Notes

- Keep this file as a running log, not a directory.
- Use `SRP_EXPERIMENT_INDEX.md` for the authoritative experiment list.
- Use `SRP_EXPERIMENT_LOG_TEMPLATE.md` to draft new records.
- Prefer one experiment record section per committed experiment.
