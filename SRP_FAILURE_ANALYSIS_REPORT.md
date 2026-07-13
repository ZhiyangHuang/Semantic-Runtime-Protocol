# SRP Failure Analysis Report

This report summarizes the first-pass semantic failure taxonomy built from the current fixed-harness records.

Data source:

- `srp_experiment/tmp/fixed_harnesses/*/*_records.jsonl`

Analysis output:

- `srp_experiment/tmp/semantic_failure_taxonomy/semantic_failure_taxonomy.json`
- `srp_experiment/tmp/semantic_failure_taxonomy/semantic_failure_taxonomy.md`

---

## Key Result

The dominant observed failure modes in the current SRP records are:

| Failure Type | Count | Main Signal |
| --- | --- | --- |
| `object_loss` | 550 | Objects are lost across lifecycle transitions, especially after compression and repair-related handoffs |
| `dependency_break` | 39 | Validation fails because required labels are not preserved; mostly `constraint_loss` with some `identity_collision` |
| `hallucinated_reconstruction` | 167 | Recovery introduces unsupported objects not grounded in the source |

Observed substructure:

- `dependency_break`
  - `constraint_loss`: 33
  - `identity_collision`: 6
- `hallucinated_reconstruction`
  - `unsupported_reconstruction`: 167
- `object_loss`
  - spread across lifecycle transitions such as `compressed_to_recovered`, `recovered_to_repaired`, `repaired_to_allocated`, `source_to_allocated`, `source_to_executed`, `source_to_recovered`, and `source_to_repaired`

---

## Interpretation

The current evidence suggests that SRP is not failing in a single place.

The first-pass taxonomy points to three recurring pressure points:

1. Lifecycle object loss is still the largest aggregate issue.
2. Validation failures are mostly dependency-preservation failures rather than pure object-count failures.
3. Hallucinated reconstruction is still a meaningful recovery-side failure mode.

This is useful because it gives the next algorithm upgrade a target:

- strengthen the semantic representation so relations and constraints survive better
- make recovery dependency-aware rather than only object-aware
- keep allocation accountable for important-object preservation

---

## Current Status

Completed:

- first-pass taxonomy extraction from fixed-harness records
- JSON export
- markdown export

Still under validation:

- allocation-failure characterization
- temporal-drift characterization on multi-round records
- more detailed identity-collision case labeling on broader long-horizon runs

---

## Next Action

Use this taxonomy to drive the Phase VI semantic state upgrade:

1. failure taxonomy refinement
2. semantic runtime graph upgrade
3. dependency-aware recovery
4. long-horizon drift analysis

