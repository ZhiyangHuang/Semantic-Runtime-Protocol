# Semester Experiment Plan

## Goal

Finish one semester with a publishable short paper by proving only the smallest set of questions needed for SRP.

## What The Experiment Must Prove

1. SRP reduces finite-horizon semantic drift.
2. The structured semantic state matters.
3. Validation and recovery each contribute to stability.
4. Semantic drift is a better core metric than token count alone.
5. SRP has a visible failure boundary.

## What To Freeze Early

- one main model
- three cycle settings only: `3`, `5`, `7`
- raw prompt, summarization, retrieval, and SRP as the main comparison set
- `C_t`, `(C_t, V_t)`, `(C_t, M_t)`, `(C_t, V_t, M_t)` for the structure ablation
- recovery ablation
- validation ablation
- one failure block

## Minimal Experimental Stack

### Main Tasks

- multi-turn instruction consistency
- iterative compression-recovery cycles
- optional long-context summarization and regeneration only if time remains

### Main Metrics

- semantic drift
- task success
- token cost

### Failure Cases

- vocabulary corruption
- validator failure
- recovery collapse
- concept explosion

## Weekly Checklist

### Week 1

- freeze the question list
- freeze the baselines
- freeze the metrics
- freeze the cycle settings

### Week 2

- make the pipeline run end to end
- verify one baseline run
- verify one SRP run
- generate the first drift plot

### Week 3

- run the main comparison
- log all configs
- stabilize the main table

### Week 4

- run the structure ablation
- run the validation ablation
- run the recovery ablation

### Week 5

- run the failure block
- collect the clearest failure cases
- decide which failures belong in the paper

### Week 6

- write the draft around the actual results
- cut any claim not supported by evidence
- keep the story finite-horizon only

## Proof Map

| Question | Evidence |
| --- | --- |
| Does SRP reduce drift? | Drift-over-iterations comparison |
| Does structure matter? | State-tuple ablations |
| Does validation matter? | Validation ablation |
| Does recovery matter? | Recovery ablation |
| Is drift the right metric? | Drift, task success, and token cost together |
| Where does SRP fail? | Failure block |

## Publication Rule

Do not expand to extra models, extra datasets, or extra task families unless the main comparison is already stable.

## End State

If this plan is followed, the semester should end with:

- one credible short paper draft
- one clean experiment repo
- one drift figure
- one token-efficiency table
- one faculty-reviewable research package

