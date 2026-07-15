# SRP Policy Boundary Analysis Report

This report records the first pressure-amplified boundary run for SRP policy analysis.

## Setup

- benchmarks:
  - `memory_saturation`
  - `validation_pressure`
  - `dependency_f1_pressure`
- execution state source: `active`
- allocation policy: `random`
- budgets: `4, 8, 12, 16, 24, 32`
- seeds: `0, 1, 2, 3, 4`

## Main Result

The allocation layer shows a clear transition boundary on both benchmarks, and the validation-pressure benchmark now also exposes dependency and validation transitions.

- `memory_saturation`
  - `allocation_dominant_metric`: `active_retention_ratio`
  - `allocation_transition_detected`: `true`
  - `allocation_boundary_upper_budget`: `32`
  - `allocation_boundary_lower_budget`: `24`
  - `allocation_boundary_pressure_index_upper`: `2.3125`
  - `allocation_boundary_pressure_index_lower`: `3.083333`
- `validation_pressure`
  - `allocation_dominant_metric`: `active_retention_ratio`
  - `allocation_transition_detected`: `true`
  - `dependency_transition_detected`: `true`
  - `dependency_dominant_metric`: `dependency_coverage`
  - `validation_transition_detected`: `true`
  - `validation_dominant_metric`: `validation_score`
  - `validation_boundary_upper_budget`: `32`
  - `validation_boundary_lower_budget`: `24`

The new validation-pressure benchmark exposes downstream dependency and validation boundaries as well, so the analysis now distinguishes:

- allocation transition
- dependency transition
- validation transition

## Interpretation

The current policy boundary suite now exposes allocation, dependency, and validation transitions.

The newer `dependency_f1_pressure` benchmark exposes a dependency-F1 boundary on the fine sweep, which is useful because it separates dependency recall from precision-sensitive dependency correctness.

A follow-up `dependency-ultrafine` sweep over budgets 8 to 12 did not place a new dependency-F1 boundary inside that narrower window. That suggests the F1 transition is workload- and resolution-sensitive rather than uniformly visible in every budget band.

## Robustness

The boundary robustness run over the current boundary suite shows:

- allocation boundaries are stable across seeds on all three benchmarks
- dependency and validation boundaries are also relatively stable
- dependency-F1 is the least stable boundary type and depends strongly on workload construction

On the robustness run:

- `dependency_f1_pressure` retained a dependency-F1 boundary in 4 of 5 seeds
- `memory_saturation` did not expose a dependency-F1 boundary in any seed

That makes dependency-F1 a useful stress test for the boundary framework rather than a universal feature of every pressure band.

## Long-Horizon Drift

The long-horizon drift sweep over `cycles = 1, 3, 5` shows no measurable midpoint drift for allocation, dependency, or dependency-F1 on the current benchmark family.

That means the boundary cascade is not only seed-stable, but also stable under repeated runtime evolution on the current workloads.

This is still a useful result because it separates:

- allocation sensitivity
- dependency sensitivity
- downstream validation sensitivity
- pressure-dependent boundary types

## Next Step

- deepen pressure amplification
- test whether the validation boundary remains stable under long-horizon or importance-shift workloads
- use the boundary suite as a bridge to robustness analysis
