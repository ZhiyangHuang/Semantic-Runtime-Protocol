# Transition Role Protocol

## Status

v1.2 research boundary.

This directory defines the experimental protocol layer for Semantic Runtime
Protocol. It does not define a benchmark suite, a dataset registry, or a new
evaluation metric.

## Purpose

The purpose of the Transition Role Protocol is to separate semantic workloads
by the kind of governance pressure they introduce, while keeping the SRP core
protocol unchanged.

The organizing question is:

> Given a semantic workload, which transition role does it instantiate, and do
> the same governance invariants remain stable under that role?

## Registry

The protocol registry is defined in [registry.yaml](registry.yaml).
It is the canonical place to enumerate transition roles, their invariants, and
their shared diagnostics.

The registry is protocol-level metadata, not a benchmark catalog.

## Versioned Layer Model

```text
Theory
    |
    v
SRP Protocol
    |
    v
Transition Role Protocol
    |
    v
Semantic Workload
    |
    v
Dataset / Runtime
```

The first two layers are frozen by v1.0 and v1.1.
This directory defines the v1.2 research layer.

## Protocol Object

A transition role is a protocol object, not a directory name and not a
benchmark label.

The minimum contract for a role is:

- `id`
- `purpose`
- `invariants`
- `diagnostics`
- `workload_requirements`
- `compatible_workloads`

`compatible_workloads` is descriptive only. It does not define the role or the
diagnostics.

## Role Lifecycle

1. A workload is observed.
2. The workload is mapped to a transition role.
3. The shared SRP diagnostics are run under a frozen runtime contract.
4. Governance consistency is compared across workloads that share the role.
5. Results are recorded as evidence, not as leaderboard scores.

## Initial Research Questions

### Governance Consistency

Can the same governance protocol remain stable across different semantic
workloads that instantiate the same transition role?

### Transition Role Consistency

Do workloads assigned to the same transition role exhibit comparable boundary
behavior under frozen contracts?

### Diagnostic Transferability

Can the same SRP diagnostics explain governance behavior across multiple
workloads without redefining the metrics per benchmark?

## Non-Goals

This protocol does not:

- define a new memory architecture
- redefine benchmark scoring
- compare leaderboard performance
- introduce learned authority
- require a new claim boundary for each workload

## Relationship to `data/external`

`data/external` registers source provenance and routing metadata.
This directory defines the protocol that the registry points to.

The registry maps workloads to roles, but the protocol should remain stable
before any registry expansion is considered.

## Validation Entry Point

The current registry and external source mapping can be validated with:

```bash
python -m experiments.transition_role.validate_registry
```

This command checks role schema consistency, external registry consistency,
and adapter capability metadata under the frozen protocol boundary.

The cross-role validation matrix can be checked with:

```bash
python -m experiments.transition_role.validate_matrix
```

This matrix is the first protocol-validation schedule for v1.2. It keeps the
initial role/workload plan explicit without redefining the SRP core protocol.

## Workload Entry Points

Role-coverage workloads are implemented under `experiments.transition_role.workloads`.
The first instantiated slice is `LoCoMo` under `temporal_state_evolution`.
The second bridge slice is `Reasoning Sources` under `inference_proposal`.

## Coverage Report

The current role coverage report can be generated with:

```bash
python -m experiments.transition_role.report_coverage
```

The report summarizes role coverage across workloads, rather than benchmark
ranking across datasets.
