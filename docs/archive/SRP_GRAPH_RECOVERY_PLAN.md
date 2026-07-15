# SRP Graph Recovery Plan

This document tracks Phase VI Priority 3: dependency-aware recovery.

The goal is to compare three recovery paths under a shared budget and metric contract:

- text recovery
- structured recovery
- graph-aware recovery

The first version should stay constrained and deterministic.

## G1 Recovery Interface

- [x] RecoveryPolicy abstraction
- [x] text recovery adapter
- [x] structured recovery adapter
- [x] graph recovery adapter

## G2 Graph Constraint Resolver

- [x] node closure
- [x] dependency closure
- [x] constraint closure
- [x] hallucination blocking

## G3 Recovery Experiment Harness

- [x] graph_recovery_harness.py
- [x] compare 3 recovery modes
- [x] export canonical metrics

## G4 First Graph Recovery Experiment

- [x] same tasks as Round 1
- [x] same budget
- [x] same metrics

## Current status

- The recovery abstraction now supports `text`, `structured`, `graph`, and legacy reconstruction mode.
- Graph recovery is deterministic in the first version.
- The graph-aware path now emits:
  - `graph_dependency_closure_rate`
  - `graph_recovery_precision`
  - `graph_repair_cost`
- The dedicated harness is now implemented and has been run on the fixed Round 1 task set.
- The first run shows graph mode lowers graph repair cost relative to text / structured recovery, while the shared validation metrics remain the same on the current fixed tasks.
- A graph information gap analysis is now available and points to missing node attributes and an explicit modified lifecycle stage in graph v1.
- Next step: use the gap analysis to shape a graph v1.5 schema upgrade, then compare graph v1 against graph v1.5.
- Graph v1.5 schema work is now underway; graph v1 remains frozen so the next comparison can isolate representation changes from recovery logic changes.
- The next fixed experiment is the graph representation ablation: graph v1 versus graph v1.5 under the same recovery policy and task set.
- The first graph representation ablation run is complete and shows v1.5 improving retention / integrity metrics while validation coverage remains flat on the current fixed tasks.
- A semantic extraction audit has now been run on the graph representation results and points to provenance / extraction under-specification as the next bottleneck.
- Graph recovery v2 stays deferred until coverage attribution shows recovery is still the bottleneck.
