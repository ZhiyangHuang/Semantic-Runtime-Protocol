# One-Page Execution Plan

## Project

**Semantic Runtime Protocol (SRP): A Minimal Study of Bounded Semantic Drift in Long-Horizon LLM Interaction**

## Semester Objective

The goal of this project is to complete a realistic undergraduate research study within one semester. Rather than pursuing a large systems paper, the project focuses on a narrow and testable question:

> Can explicit semantic-state management improve finite-horizon stability under repeated compression-recovery cycles, relative to lightweight baselines?

The intended output is a disciplined semester-version paper, a reproducible experiment pipeline, and a faculty-reviewable research package.

## Scope

To keep the project feasible within one semester, the study is intentionally constrained.

### Paper Scope

- one main claim
- one short paper or workshop-style draft
- finite-horizon evaluation only
- minimal formalization rather than a full theory

### Experimental Scope

- `1` main model
- `2` core task families
- `3` main methods in the paper body
- cycle settings of `3`, `5`, and `7`
- `1-2` small ablations if time permits

### Main Methods

- summarization
- strongest baseline
- SRP

Appendix-only baselines, if useful:

- raw prompt
- RAG

## Research Design

The study treats semantic state as a structured runtime object rather than raw prompt history alone. The working context can be thought of as an MCP-like packaged context window selected under the model's token limit, and SRP tries to manage that window dynamically rather than rely on manual editing. The minimal SRP pipeline consists of:

- compression
- recovery
- validation
- update

This runtime framing is intentionally distinct from memory storage alone: memory keeps records, while runtime governs transitions, validation, recovery, and update across cycles.

When user-facing communication matters, the system may also need a reverse-expansion step so that compressed concepts are made understandable again before being shown back to the user.

The main evaluation question is whether this structure reduces semantic drift while preserving downstream task behavior and remaining reasonably token-efficient, relative to the strongest non-SRP baseline.

The primary metric is semantic drift because it captures the failure mode that the semantic runtime is meant to control.

## Reviewer Risks To Keep Visible

The current version should keep a few open questions visible rather than forcing them closed too early:

- Is SRP best described as a runtime, a protocol, or a semantic communication layer?
- What is the minimal semantic-state object?
- Which drift metric is most defensible in the first paper?
- Where exactly does SRP differ from prompt compression and retrieval memory?
- Should the theory be framed as a practical semantic runtime only, or as an early semantic predictive state?
- Should SRP eventually support semantic transaction-style commit and rollback semantics?

These are not blockers for the semester version, but they are important for framing the paper honestly.

## Planned Evaluation

### Core Tasks

- multi-turn instruction consistency
- iterative compression-recovery cycles

### Main Metrics

- semantic drift
- task success
- token cost

### Main Outputs

- drift-over-iterations figure
- quality table
- efficiency table
- camera-ready SRP vs strongest-baseline table

### Current Semester Boundaries

- keep the main paper finite-horizon only
- keep the formalization practical rather than philosophical
- keep the experiment small enough to replay
- move broad governance and enterprise ideas to future work
- treat transaction-style commit or rollback ideas as future runtime extensions unless the core paper is already stable

## Deliverables By Semester End

- one complete short paper draft
- one reproducible experiment repo
- one clean results package with figures and LaTeX tables
- one polished research pitch for future faculty or graduate applications

## Working Timeline

### Weeks 1-2

- lock the problem scope
- finalize the minimal experiment design
- ensure the code pipeline runs end to end

### Weeks 3-4

- stabilize the main experiment
- generate figures and summary tables
- identify the strongest baseline clearly

### Weeks 5-6

- write and revise the paper draft
- tighten the claims
- present a faculty-reviewable version

## What Is Deliberately Out of Scope

The following are intentionally deferred beyond the semester version:

- large-scale multi-model benchmarking
- full theoretical guarantees
- enterprise-scale runtime design
- large benchmark construction
- broad agent framework claims

These are treated as future work rather than core semester requirements.

## Why This Scope Is Appropriate

This plan is designed for a single undergraduate researcher with one semester remaining. The focus is on finishing a credible, reviewable, and reproducible project rather than attempting a large speculative system that may remain incomplete.

## Faculty Support Requested

The most useful forms of support would be:

- feedback on scope and research framing
- periodic discussion of experiment design and paper clarity
- possible independent study or project supervision
- advice on whether the framing is strong enough for a short paper or workshop submission

## Expected Outcome

If completed successfully, this project should provide:

- a credible semester-version paper draft
- a clear demonstration of independent research ability
- stronger preparation for recommendation letters and future academic applications
- a technically legible project for AI systems and evaluation roles
