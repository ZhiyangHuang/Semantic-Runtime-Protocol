# SRP Semantic Extraction Audit Report

This report summarizes the first extraction audit run over the graph representation ablation results.

## Main Finding

The current bottleneck is not graph storage capacity alone.

The audit suggests the remaining gap is provenance / extraction under-specification:

- graph v1.5 improves stateful representation completeness
- validation coverage stays flat on the fixed tasks
- provenance completeness is still effectively absent

## Key Observations

| Metric | Observation |
| --- | --- |
| Node capture | Source objects are still partially under-captured at the extraction boundary |
| Relation capture | Dependency clauses are present, but extraction is still under-specified for richer semantic typing |
| Constraint capture | Constraint clauses remain limited on the current fixed tasks |
| Attribute completeness | v1.5 improves this over v1 |
| Lifecycle completeness | v1.5 is still stronger than v1 in stateful representation |
| Provenance completeness | Still missing |

## Interpretation

The evidence now supports a frozen SRR v2 prototype and a next-step shift into coverage attribution analysis.

## Recommended Next Step

Do not expand graph recovery v2 yet.

Instead, measure where coverage is lost across the pipeline:

- extraction loss
- representation loss
- compression loss
- recovery loss
- validation loss
