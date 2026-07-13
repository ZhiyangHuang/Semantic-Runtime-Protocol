# SRP Research Findings

This file records the current research-level observations, not implementation tasks.

## 1. Representation Findings

- Graph v1.5 improves attribute retention, state retention, lifecycle accuracy, and graph integrity relative to graph v1.
- Validation coverage remains flat on the current fixed task set, so richer representation alone is not the dominant limiter on that benchmark.

## 2. Attribution Findings

- The SRP analysis stack now supports coverage, decision, importance, and policy attribution.
- Coverage attribution identifies where loss occurs.
- Decision attribution identifies why objects are dropped.
- Importance attribution identifies why objects are considered low-value.
- Policy attribution identifies which policy rule or threshold caused the decision.
- The first mechanism-attribution matrix is now interpretable as two largely orthogonal effects:
  - `remove_importance_weighting` primarily changes selection composition, overlap, and important-item capture rather than the allocation midpoint.
  - `remove_dependency_retention` primarily shifts dependency and dependency-F1 behavior while leaving allocation comparatively stable.

## 3. Policy Intervention Findings

- Policy intervention shows a clear multi-objective tradeoff.
- `permissive` is best for validation coverage on the current benchmark.
- `conservative` is best for graph integrity and object retention on the current benchmark.
- No single policy dominates all objectives.

## 4. Pareto Findings

- The current policy space is Pareto-like rather than single-objective.
- The front contains the current baseline, permissive, balanced, and conservative configurations.
- The right interpretation is policy design-space exploration, not a single-best optimizer.

## 5. Sensitivity Findings

- The first sensitivity analysis run is mostly flat on the current fixed benchmark.
- This is still a useful result: it suggests the benchmark is not yet sufficiently pressure-rich to expose strong differences for the chosen knobs.
- Stronger benchmark pressure will be needed before sensitivity curves become decisive.

## 6. Boundary Findings

- The first pressure-amplified memory-saturation benchmark now shows an allocation-layer boundary between budgets 32 and 24, with `active_retention_ratio` dropping from about 0.58 to 0.44 as pressure increases.
- The new validation-pressure benchmark shows a dependency boundary and a downstream validation boundary as well, with `dependency_coverage` and `validation_score` changing across the same budget region while the allocation boundary remains visible.
- The result is still scientifically useful: SRP now exhibits a nested boundary structure, where allocation changes can appear before dependency transitions and validation transitions, and a dependency-sensitive benchmark is required to expose the latter.
- The new `dependency_f1_pressure` benchmark finally exposes a sharper dependency-F1 transition, with a boundary between budgets 10 and 8 on the fine sweep. This is the first benchmark where dependency coverage and dependency-F1 can be separated more clearly.
- The follow-up `dependency-ultrafine` sweep over budgets 8 to 12 did not place a new dependency-F1 boundary inside that window. That is still informative: the dependency-F1 transition is workload- and resolution-sensitive rather than uniformly present in every pressure band.
- Boundary-gap analysis now shows that the allocation boundary typically appears slightly earlier than the dependency/validation boundaries, while dependency-F1 is more resolution-sensitive and may only appear under a narrower pressure band.
- Boundary robustness analysis on the current boundary suite shows allocation, dependency, and validation boundaries are relatively stable across seeds, while dependency-F1 is the most fragile and workload-dependent boundary type.
- In the robustness run, `dependency_f1_pressure` kept a dependency-F1 boundary in 4 of 5 seeds, while `memory_saturation` did not expose a dependency-F1 boundary in any seed. This supports the interpretation that dependency-F1 is sensitive to both semantic density and distractor structure.
- Long-horizon boundary drift on `cycles = 1, 3, 5` shows no measurable midpoint drift for allocation, dependency, or dependency-F1 on the current benchmark family. This suggests the observed boundary cascade is stable under repeated runtime evolution on the current workloads.
- The current boundary line is now treated as closed for the present workload family: the evidence supports a stable structural cascade rather than a drifting threshold artifact.
- The next research step is to keep the theory stack compressed and consistent, using the design rationale, core assumptions, theory map, semantic state model, semantic degradation model, preservation objective formalization, runtime representation design, policy mechanism design, runtime lifecycle design, mechanism attribution framework, and the evaluation objective matrix as the stable framework before any baseline comparison.
- The canonical design bridge is [SRP_RUNTIME_REPRESENTATION_DESIGN.md](SRP_RUNTIME_REPRESENTATION_DESIGN.md).
- The canonical policy bridge is [SRP_POLICY_MECHANISM_DESIGN.md](SRP_POLICY_MECHANISM_DESIGN.md).
- The canonical lifecycle bridge is [SRP_RUNTIME_LIFECYCLE_DESIGN.md](SRP_RUNTIME_LIFECYCLE_DESIGN.md).
- The canonical assumption bridge is [SRP_CORE_ASSUMPTIONS.md](SRP_CORE_ASSUMPTIONS.md).
- The canonical state bridge is [SRP_SEMANTIC_STATE_MODEL.md](SRP_SEMANTIC_STATE_MODEL.md).
- The canonical degradation bridge is [SRP_SEMANTIC_DEGRADATION_MODEL.md](SRP_SEMANTIC_DEGRADATION_MODEL.md).
- The canonical preservation bridge is [SRP_PRESERVATION_OBJECTIVE_FORMALIZATION.md](SRP_PRESERVATION_OBJECTIVE_FORMALIZATION.md).
- The canonical attribution bridge is [SRP_MECHANISM_ATTRIBUTION_FRAMEWORK.md](SRP_MECHANISM_ATTRIBUTION_FRAMEWORK.md).
- The canonical overview bridge is [SRP_THEORY_MAP.md](SRP_THEORY_MAP.md).
- The canonical evaluation bridge is [SRP_EVALUATION_OBJECTIVE_MATRIX.md](SRP_EVALUATION_OBJECTIVE_MATRIX.md).
- The canonical ablation spec remains [SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md](SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md).
- The first causal ablation prototype is now available: removing dependency-aware retention shifts dependency boundaries earlier while leaving allocation comparatively stable on the current frozen sweep.
- The second causal ablation variant is now available: removing importance weighting is now wired to runtime metadata and produces a measurable diagnostic signal, but on the current frozen sweep it remains weaker than dependency-aware retention and is concentrated more in downstream validation than in allocation-boundary movement.
- The A1 diagnostic now shows that removing importance weighting changes selection composition and importance overlap more than boundary midpoints, which suggests the mechanism is closer to semantic composition control than to a pure allocation-boundary controller on the current workload family.
- The new comparison layer now reports boundary shifts, metric deltas, and an attribution score for each benchmark.

## 7. Interpretation

- SRP is best understood as a measurable and explainable semantic runtime analysis framework.
- The current research step is to keep the theory stack compressed and consistent, using the design rationale, core assumptions, theory map, semantic state model, semantic degradation model, preservation objective formalization, runtime representation design, policy mechanism design, runtime lifecycle design, mechanism attribution framework, and evaluation objective matrix as the stable framework before any baseline comparison: explain why long-running semantic systems degrade, which preservation objectives SRP is designed to maintain, what the runtime state is, how degradation happens, how those objectives are measured, what information the runtime representation must store to support them, how policy uses that information, how the runtime lifecycle evolves, and how mechanisms map to objective-level preservation behavior.
- The next research step after the design and evaluation bridges is to connect those preservation objectives to mechanism attribution / ablation protocol and later baseline comparison.
- The current attribution matrix suggests that importance weighting regulates semantic selection quality, while dependency-aware retention regulates structural coherence.
