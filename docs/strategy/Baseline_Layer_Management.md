# Baseline Layer Management

This note freezes the baseline-layer structure for the current semester experiment system.

## Goal

The repository should clearly separate:

- main paper comparison methods
- controlled baseline families
- SRP-native methods
- exploratory hybrid diagnostics

without repeatedly renegotiating which methods count as the core experiment.

## Main Paper Comparison Set

The canonical main comparison for the current paper is:

1. `raw_prompt`
2. `summarization`
3. `rag`
4. `srp`
5. `rag_srp_v2`

These are the only methods that should define the main quantitative comparison for the current semester paper unless the paper is deliberately rebaselined.

## Method Roles

### 1. `raw_prompt`

File:

- `srp_experiment/baselines/raw_prompt.py`

Role:

- direct carryover baseline
- memory is carried forward with budget-aware clipping

Read/write object:

- reads `initial_state.memory`
- writes a budget-clipped direct prompt memory view

Paper status:

- main comparison baseline

### 2. `summarization`

File:

- `srp_experiment/baselines/summarization.py`

Role:

- summary-compression baseline
- memory is compressed into a shorter surrogate under the shared token regime

Read/write object:

- reads the current memory string
- writes a summary surrogate

Paper status:

- main comparison baseline

### 3. `rag`

File:

- `srp_experiment/baselines/rag.py`

Role:

- retrieval-selection baseline
- memory is chunked, selected, and repacked under the shared retrieval budget

Read/write object:

- reads the local task memory
- writes the retrieved chunk selection

Paper status:

- main comparison baseline

### 4. `srp`

Primary file:

- `srp_experiment/srp/pipeline.py`

Role:

- semantic-state compression / recovery baseline-family head
- runs the protocol operators directly on a semantic runtime state

Read/write object:

- reads and writes `SemanticState`
- state includes memory, constraints, vocabulary, term map, loss notes, and typed semantic representation

Paper status:

- main comparison method

### 5. `rag_srp_v2`

File:

- `srp_experiment/baselines/rag_srp_v2.py`

Role:

- retrieval plus semantic-state compression / recovery
- retrieval first, then SRP-style compression / recovery under the same token-bounded regime

Read/write object:

- reads local task memory for retrieval
- writes a retrieved-memory SRP working state

Paper status:

- main comparison method in the frozen five-method regime

## Exploratory Hybrid Diagnostics

The following files remain preserved but should not be treated as main-paper canonical methods:

- `srp_experiment/baselines/rag_srp.py`
- `srp_experiment/baselines/rag_srp_anchor.py`

Role:

- exploratory hybrid lineage
- diagnostic comparison
- ablation-like history of retrieval-guided SRP ideas

Paper status:

- preserved diagnostic methods
- not part of the semester-stable main comparison by default

## Shared Fairness Regime

All five canonical methods run under the same shared token-bounded regime.

The shared budget layer lives in:

- `srp_experiment/budgeting.py`
- `srp_experiment/.env`

Key shared controls include:

- total token budget
- system prompt reserve
- output reserve
- query reserve
- safety margin
- RAG chunk size
- RAG top-k

This means the methods differ in memory transformation operator, not in access to a looser prompt budget.

## Canonical Terminology

For the current paper, describe the method family as:

- `raw_prompt`: direct carryover baseline
- `summarization`: summary-compression baseline
- `rag`: retrieval-selection baseline
- `srp`: semantic-state compression / recovery method
- `rag_srp_v2`: retrieval-plus-semantic-state method

Do not describe these as off-the-shelf agent-tool reference implementations unless that is explicitly true for a future rebaselined version.

## Practical Rule

If a new method appears, classify it first as one of:

1. main paper comparison candidate
2. exploratory hybrid diagnostic
3. future-work placeholder

Do not let new methods silently enter the main comparison without updating the frozen baseline policy.
