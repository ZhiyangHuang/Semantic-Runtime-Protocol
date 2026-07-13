# SRP Semantic Runtime Graph v1

This report records the first minimal graph upgrade for SRP.

## What changed

- Added a minimal semantic runtime graph with:
  - nodes
  - edges
  - lifecycle
  - validation
- Added a graph schema at:
  - `srp_experiment/schemas/semantic_runtime_graph_schema_v1.json`
- Attached the graph to the canonical experiment result as `experiment_result.semantic_graph`
- Added graph-aware metrics to `experiment_result.metrics`

## What the graph captures

- source objects as nodes
- recovered-only hallucinations as nodes with a different lifecycle state
- contract / dependency clauses as separate contract nodes
- explicit edges for containment, dependency, and hallucination tracking

## Validation signals

The graph validator now reports:

- `object_survival_rate`
- `dependency_recall`
- `constraint_accuracy`
- `hallucination_rate`
- `graph_integrity_score`

## Current status

- The graph is intentionally minimal.
- It is not a full knowledge graph.
- It is designed to expose the failure families already seen in the taxonomy:
  - `object_loss`
  - `dependency_break`
  - `hallucinated_reconstruction`

## Verified

- `srp_experiment.tests.test_semantic_runtime_graph`
- `srp_experiment.tests.test_srp_runtime`

## Next step

Use the graph view to drive dependency-aware recovery and compare:

- text recovery
- structured recovery
- graph-aware recovery
