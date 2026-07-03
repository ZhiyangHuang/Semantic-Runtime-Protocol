# One-Page Executive Summary

## Project Title

**Semantic Runtime Protocol (SRP): A Minimal Study of Bounded Semantic Drift in Long-Horizon LLM Interaction**

## Project Snapshot

This project is a semester-scoped undergraduate research study on long-horizon LLM stability. Its purpose is to investigate whether explicit semantic-state management can improve finite-horizon behavior under repeated compression-recovery cycles, relative to lightweight baselines such as prompt accumulation, summarization memory, and retrieval-based memory.

The project is intentionally narrow. It is designed to produce a credible semester-version paper, a reproducible experiment pipeline, and a faculty-reviewable research package within one remaining semester.

## Central Research Question

The study is organized around a single question:

> Can explicit semantic-state management improve finite-horizon stability under repeated compression-recovery cycles, relative to lightweight baselines?

This is the only claim the semester version is intended to support.

## Core Idea

The project introduces **Semantic Runtime Protocol (SRP)** as a minimal abstraction for representing semantic state as a structured runtime object rather than raw prompt history alone. The central distinction is that memory stores state, while runtime governs state transition, validation, recovery, and update.

In the current version, SRP is defined through four practical operators:

- compression
- recovery
- validation
- update

These operators are the smallest closed loop that makes semantic runtime distinct from memory storage alone.

The goal is not to propose a full semantic operating system. The goal is to test whether this minimal protocol provides a cleaner and more stable way to manage task-relevant semantics over repeated interaction steps.

## Current Scope

### Included

- a minimal SRP abstraction
- a finite-horizon experiment
- a reproducible implementation pipeline
- a short paper or workshop-style draft
- a faculty-reviewable semester research package

### Excluded

- large-scale multi-model benchmarking
- full theoretical guarantees
- broad agent-system replacement claims
- enterprise-scale runtime design
- protocol standardization
- advanced extensions beyond the semester study

These excluded directions remain part of the broader SRP vision, but they are intentionally deferred.

## Experimental Design

The semester version is deliberately constrained:

- `1` main model
- `2` core task families
- `4` main methods in the paper body
- cycle settings of `3`, `5`, and `7`
- `1-2` small ablations only if time permits

Main body methods:

- raw prompt
- summarization
- retrieval-based memory
- srp

Main task families:

- multi-turn instruction consistency
- iterative compression-recovery cycles

Main metrics:

- semantic drift
- task success
- token cost

The primary evaluation lens is bounded semantic drift because it captures the failure mode that the semantic-state runtime abstraction is meant to control.

## Main Outputs

The current paper only requires a small number of core results:

- one drift-over-iterations figure
- one quality table
- one efficiency table
- one camera-ready SRP vs strongest-baseline table

If these outputs are formal-evidence quality and reproducible, the project is already strong enough for the semester version.

## Reproducibility Status

The project already includes a runnable experiment pipeline, batch configuration, summary collection, and paper-ready table formatting. The implementation is meant to support disciplined evaluation rather than continued feature expansion.

## Current Pilot Status

The experiment stack has now been exercised on a real local backend rather than only the deterministic mock scaffold.

Current pilot run:

- backend: local `vLLM`
- model: `Qwen/Qwen3-4B-AWQ`
- methods: `raw prompt`, `summarization`, `retrieval-based memory`, `srp`
- cycles: `3`
- tasks: `3` toy tasks with shared rotating evaluation queries

This pilot is important because it confirms that the first-paper pipeline is now closed at the systems level:

- the local backend is callable from the experiment runner
- `results.json` is generated on a real model run
- `summary.json` is aggregated correctly
- shared-query evaluation is recorded per cycle and remains consistent across methods

The current pilot results do **not** yet support a strong paper claim that SRP outperforms the lightweight baselines. In this run:

- `raw_prompt`: `mean_drift = 0.7953`, `mean_task_success = 1.0`, `mean_query_success = 0.8389`, `mean_tokens = 318.44`
- `summarization`: `mean_drift = 0.7591`, `mean_task_success = 0.9167`, `mean_query_success = 0.8944`, `mean_tokens = 83`
- `retrieval-based memory`: `mean_drift = 0.7276`, `mean_task_success = 0.9167`, `mean_query_success = 0.8889`, `mean_tokens = 87.33`
- `srp`: `mean_drift = 0.8438`, `mean_task_success = 0.75`, `mean_query_success = 0.7056`, `mean_tokens = 106.22`

The correct interpretation is therefore:

- the real local experiment environment is working
- the shared evaluation flow is now grounded in a real backend
- the current SRP implementation still needs improvement before the first paper can claim an advantage over the baselines

This is useful progress, because it turns the project from a mock-only scaffold into a real pilot study with falsifiable behavior.

The latest tuned local pilot is stronger than this first real run.

Latest tuned pilot:

- backend: local `vLLM`
- model: `Qwen/Qwen3-4B-AWQ`
- methods: `raw prompt`, `summarization`, `retrieval-based memory`, `srp`
- cycles: `5` and `7`
- tasks: `3` toy tasks with shared rotating evaluation queries

Current tuned local pilot summary:

- `raw_prompt`: `mean_drift = 0.3541`, `mean_task_success = 0.9167`, `mean_query_success = 1.0`, `mean_tokens = 150.27`
- `summarization`: `mean_drift = 0.5558`, `mean_task_success = 0.5833`, `mean_query_success = 0.8667`, `mean_tokens = 25.27`
- `retrieval-based memory`: `mean_drift = 0.1219`, `mean_task_success = 0.9167`, `mean_query_success = 1.0`, `mean_tokens = 33.67`
- `srp`: `mean_drift = 0.6474`, `mean_task_success = 0.9567`, `mean_query_success = 0.8222`, `mean_tokens = 25.93`

The same tuned SRP path has now also been checked at `7` cycles:

- `raw_prompt`: `mean_drift = 0.3598`, `mean_task_success = 0.9286`, `mean_query_success = 1.0`, `mean_tokens = 181.10`
- `summarization`: `mean_drift = 0.5745`, `mean_task_success = 0.5833`, `mean_query_success = 0.8730`, `mean_tokens = 24.81`
- `retrieval-based memory`: `mean_drift = 0.1601`, `mean_task_success = 0.9167`, `mean_query_success = 1.0`, `mean_tokens = 35.24`
- `srp`: `mean_drift = 0.6902`, `mean_task_success = 0.9310`, `mean_query_success = 0.8095`, `mean_tokens = 27.24`

The newest local pilot now uses an anchor-guided SRP recovery design rather than the earlier free-running tuned4 recovery. Under this Round 6 variant:

- at `5` cycles, `srp` now reaches `mean_drift = 0.4169`, `mean_task_success = 0.9500`, `mean_query_success = 0.7778`, `mean_tokens = 27.33`
- at `7` cycles, `srp` now reaches `mean_drift = 0.4081`, `mean_task_success = 0.9167`, `mean_query_success = 0.8254`, `mean_tokens = 29.00`

Compared with the first untuned local pilot, the tuned SRP path is now:

- lower in drift
- much stronger in task success
- lower in token cost
- more credible as a concrete runtime implementation

However, the current tuned pilot still does **not** justify a strong claim that SRP is the strongest overall method on the present toy benchmark. The best reading is narrower:

- SRP improves materially when protocol leakage is reduced and recovery remains concrete
- SRP becomes more competitive under the `5`-cycle local pilot than under the earlier `3`-cycle untuned pilot
- anchor-guided recovery makes the main SRP path more balanced than the earlier tuned4 version
- SRP continues to preserve substantially more task success than plain summarization at `5` and `7` cycles
- the strongest retrieval baseline still outperforms SRP on drift under the current toy task suite

This means the project has moved from:

- "the pipeline works"

to:

- "the pipeline works, SRP behavior is tunable, and the first paper can now discuss real local pilot evidence plus visible failure boundaries"

## Stage Freeze

For the current semester, the following directions are intentionally frozen unless the core paper is complete:

- new large-scale benchmark expansion
- additional model sweeps
- extra task families
- complex formal extensions
- broader architectural generalization
- advanced future-work protocol features

The working rule is simple:

> The system should not expand until the current paper, tables, and reproducible experiment are complete.

## Expected Deliverables

By the end of the semester, the intended outputs are:

- one credible short paper draft
- one reproducible experiment repository suitable for formal evidence
- one professor-facing execution plan
- one set of paper-ready figures and tables
- one narrow and defensible academic narrative

## Why This Version Matters

The broader SRP blueprint remains valuable as a long-term direction, but the present version is designed as a disciplined first step: small enough to finish, clear enough to evaluate, and concrete enough to support faculty feedback, recommendation potential, and future academic or professional use.
