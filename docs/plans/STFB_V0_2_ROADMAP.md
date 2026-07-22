# STFB v0.2 Roadmap

## Purpose

This document defines the next research version of STFB without changing the frozen STFB v0.1 core benchmark, Milestone 0 prototype, or external validation evidence layer.

The v0.2 question is:

> How general are semantic transition failures across more environments and larger instance sets?

## Scope

STFB v0.2 focuses on research expansion, not redefinition.

### In Scope

- larger synthetic instance coverage
- stronger failure coverage within the frozen STFB taxonomy boundary
- statistical evaluation over more cases
- additional external environments only if they introduce new semantic pressure
- cross-environment consistency analysis

### Out of Scope

- changing the STFB core schema
- changing the frozen STFB taxonomy
- changing the frozen baseline contract
- changing the Milestone 0 prototype contract
- turning external validation into a new benchmark family

## Proposed Milestones

### Milestone 1: Scale-Safe Synthetic Expansion

Goal:

- increase the number of STFB-compatible synthetic transition instances without changing the instance contract

Expected outputs:

- more canonical cases
- more balanced failure coverage
- stable runner compatibility

### Milestone 2: Cross-Environment Growth

Goal:

- expand external validation only when a new environment exposes a distinct semantic pressure

Priority order:

1. LongMemEval continuation if a new mechanism is needed
2. ARC continuation if a new reasoning pressure is needed
3. MMLU only if it contributes a mechanism not already covered
4. HumanEval only if code-transition governance becomes a target research line

### Milestone 3: Statistical Interpretation

Goal:

- summarize where each admission strategy is stable, where it diverges, and which failure mechanisms recur across environments

Expected outputs:

- mechanism matrix updates
- divergence summaries
- failure mapping updates

## Success Criteria

STFB v0.2 should provide evidence that:

- semantic transition failures are not limited to the current canonical slices
- the admission semantics remain interpretable across environments
- new environments only enter when they add new semantic pressure

## Non-Goals

STFB v0.2 does not:

- replace SRP as the governance framework
- redefine the core benchmark identity
- collapse external validation into benchmark ranking
- claim universal optimality for any admission policy

## Version Boundary

This roadmap is a research planning artifact only.
It does not modify the frozen STFB v0.1 specification, the Milestone 0 checkpoint, or the external validation freeze.

