# SRP External Validation Baseline Capability Matrix V1

This document freezes the baseline capability contract for SRP external validation.
It is an analysis artifact, not an experiment result, not a benchmark ranking, and not a claim that all capabilities are evaluated identically on every workload.

## 1. Purpose

Define what each baseline is expected to cover so the external-validation suite can compare systems across the same capability classes without collapsing SRP into a single accuracy score.

The question is not which system is universally best.
The question is:

> Which semantic capabilities are present, partial, or absent across the baseline families that SRP is compared against?

## 2. Capability Dimensions

The matrix uses the following capability dimensions:

- Retrieval: can the system retrieve relevant memory or context
- Relation: can the system represent or recover semantic relations
- Temporal: can the system preserve or reason over change over time
- Update: can the system incorporate new evidence or preference changes
- Governance: can the system explicitly validate, constrain, or authorize semantic change

Capability values:

- `core` = core capability
- `partial` = supported but not a core mechanism
- `implicit` = present only as an indirect consequence of another mechanism
- `none` = not a defined capability
- `weak` = present but limited or unstable under the benchmarked setting

## 3. Baseline Capability Matrix

| System | Retrieval | Relation | Temporal | Update | Governance |
| --- | --- | --- | --- | --- | --- |
| Full context | core | implicit | core | none | none |
| Sliding window | core | implicit | partial | none | none |
| Summarization memory | partial | none | partial | partial | none |
| Vector retrieval / RAG-style memory | core | none | weak | partial | none |
| Graph or structured memory | core | core | partial | partial | none |
| MemGPT / Letta | core | partial | core | core | partial |
| Mem0 | core | partial | core | core | partial |
| Graphiti | core | core | core | partial | partial |
| MemMachine | core | partial | core | core | partial |
| SRP | core | core | core | core | core |

## 4. Interpretation Rules

This matrix should be read as a comparison contract, not a leaderboard.

It is intended to help the paper answer three questions:

1. Which systems expose relation and temporal structure as explicit memory capabilities?
2. Which systems can incorporate updates without a governance boundary?
3. Which systems support explicit semantic validation and authorized recovery?

## 5. Relation to the Paper

The matrix supports the external-validation story by separating:

- retrieval-first memory
- structured memory
- agent memory systems
- governed semantic evolution

It is used to keep baseline comparisons conceptually aligned across LoCoMo, LongMemEval, and TGB 2.0 without turning the paper into a generic memory benchmark.
