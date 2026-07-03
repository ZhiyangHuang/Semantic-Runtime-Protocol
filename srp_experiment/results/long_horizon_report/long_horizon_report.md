# Long Horizon SRP Report

- Status: `READY_TO_ANALYZE`
- Input files: `1`
- Total trace rows: `28`
- Methods: `rag, raw_prompt, srp, summarization`
- Task filter: `iterative_cycles`

## Interpretation

SRP is evaluated as a state-transition validity space: models act as executors of the constraint system, not as evaluators or reasoners over it.
The long-horizon curves are used to inspect whether repeated compression and recovery preserve validity under extended scheduling.

## Stage Offsets

- rag @ 1-10: drift=0.1504 offset=0.1147 contract=None commit=None
- raw_prompt @ 1-10: drift=0.0911 offset=0.0221 contract=None commit=None
- srp @ 1-10: drift=0.037 offset=0.0 contract=0.81 commit=1.0
- summarization @ 1-10: drift=0.5588 offset=0.147 contract=None commit=None

## Consistency Snapshot
- rag c1: drift_mean=0.0357 drift_std=0.0 contract_mean=None contract_std=None
- rag c2: drift_mean=0.0357 drift_std=0.0 contract_mean=None contract_std=None
- rag c3: drift_mean=0.0357 drift_std=0.0 contract_mean=None contract_std=None
- rag c4: drift_mean=0.0357 drift_std=0.0 contract_mean=None contract_std=None
- rag c5: drift_mean=0.0357 drift_std=0.0 contract_mean=None contract_std=None
- rag c6: drift_mean=0.5714 drift_std=0.0 contract_mean=None contract_std=None
- rag c7: drift_mean=0.303 drift_std=0.0 contract_mean=None contract_std=None
- raw_prompt c1: drift_mean=0.069 drift_std=0.0 contract_mean=None contract_std=None
- raw_prompt c2: drift_mean=0.069 drift_std=0.0 contract_mean=None contract_std=None
- raw_prompt c3: drift_mean=0.1 drift_std=0.0 contract_mean=None contract_std=None
- raw_prompt c4: drift_mean=0.1 drift_std=0.0 contract_mean=None contract_std=None
- raw_prompt c5: drift_mean=0.1 drift_std=0.0 contract_mean=None contract_std=None
- raw_prompt c6: drift_mean=0.1 drift_std=0.0 contract_mean=None contract_std=None
- raw_prompt c7: drift_mean=0.1 drift_std=0.0 contract_mean=None contract_std=None
- srp c1: drift_mean=0.037 drift_std=0.0 contract_mean=0.81 contract_std=0.0
- srp c2: drift_mean=0.037 drift_std=0.0 contract_mean=0.81 contract_std=0.0
- srp c3: drift_mean=0.037 drift_std=0.0 contract_mean=0.81 contract_std=0.0
- srp c4: drift_mean=0.037 drift_std=0.0 contract_mean=0.81 contract_std=0.0
- srp c5: drift_mean=0.037 drift_std=0.0 contract_mean=0.81 contract_std=0.0
- srp c6: drift_mean=0.037 drift_std=0.0 contract_mean=0.81 contract_std=0.0
- srp c7: drift_mean=0.037 drift_std=0.0 contract_mean=0.81 contract_std=0.0
- summarization c1: drift_mean=0.4118 drift_std=0.0 contract_mean=None contract_std=None
- summarization c2: drift_mean=0.4333 drift_std=0.0 contract_mean=None contract_std=None
- summarization c3: drift_mean=0.6061 drift_std=0.0 contract_mean=None contract_std=None
- summarization c4: drift_mean=0.5938 drift_std=0.0 contract_mean=None contract_std=None
- summarization c5: drift_mean=0.6364 drift_std=0.0 contract_mean=None contract_std=None
- summarization c6: drift_mean=0.5938 drift_std=0.0 contract_mean=None contract_std=None
- summarization c7: drift_mean=0.6364 drift_std=0.0 contract_mean=None contract_std=None
