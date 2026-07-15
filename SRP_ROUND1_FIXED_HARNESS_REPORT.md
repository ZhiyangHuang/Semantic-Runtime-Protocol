# SRP Round 1 Fixed Harness Report

This report summarizes the first run of the fixed SRP harness bundle.

Bundle outputs were written under:

- `srp_experiment/tmp/fixed_harnesses/`

The bundle included:

- `controlled`
- `recovery`
- `reconstruction`
- `object_aware_compression`

---

## 1. Executive Summary

Round 1 already gives us a usable baseline for paper-style evaluation.

What we learned:

- `recovery` separates well on the current benchmark.
- `reconstruction` also separates well enough to form a baseline comparison.
- `object_aware_compression` did not separate on the current benchmark.
- mechanism verification shows object support does change chunk scores, but not the selected top-k set in Round 1.
- The current benchmark is therefore strong enough for baseline reporting, but not yet strong enough for object-support claims.

Interpretation:

- We should keep the Round 1 results as the baseline.
- We should only upgrade benchmark pressure for the weak `object_aware_compression` line.
- The next pressure upgrade should focus on dependency branching, subject collision, and budget pressure.

---

## 2. Controlled Harness

Summary source:

- [controlled_harness_summary.md](./srp_experiment/tmp/fixed_harnesses/controlled/controlled_harness_summary.md)

| Suite | Records | Validation Passed | Repair Attempted | Important Recall | Task Critical Recall | Token Overhead |
| --- | --- | --- | --- | --- | --- | --- |
| structured_recovery | 1 | 0 | 1 | 1.0 | 0.5 |  |
| object_retention | 1 | 0 | 1 | 1.0 | 0.5 |  |
| repair_loop | 1 | 0 | 1 | 1.0 | 0.0 | 0 |

Observations:

- Repair is consistently triggered in this suite.
- Important recall is stable at `1.0`.
- The `repair_loop` task is the most constrained one and still does not pass validation in Round 1.

---

## 3. Recovery Ablation

Summary source:

- [recovery_ablation_summary.md](./srp_experiment/tmp/fixed_harnesses/recovery/recovery_ablation_summary.md)

| Suite | Policy | Validation Coverage | Important Recall | Task Critical Recall | Recovered Object Count | Hallucinated Count | Object Inflation Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- |
| text_only_recovery | unrestricted | 0.497059 | 1.0 | 0.5 | 11 | 4 | 1.833333 |
| structured_only_recovery | minimal | 0.407059 | 1.0 | 0.5 | 10 | 3 | 0.833333 |
| hybrid_recovery | constrained | 0.536765 | 1.0 | 0.5 | 11 | 0 | 1.0 |

Observations:

- `hybrid_recovery` is the strongest Round 1 setting on this benchmark.
- It achieves the highest `validation_coverage`.
- It also eliminates hallucinated objects in this run.
- `structured_only_recovery` is smaller and more minimal, but loses coverage.

Draft conclusion:

- Hybrid recovery improves validation coverage while avoiding hallucinated objects relative to text-only recovery.

---

## 4. Reconstruction Policy

Summary source:

- [reconstruction_policy_summary.md](./srp_experiment/tmp/fixed_harnesses/reconstruction/reconstruction_policy_summary.md)

| Suite | Policy | Validation Coverage | Recovered Object Count | Hallucinated Count | Reconstruction Precision | Reconstruction Selectivity | Minimality Score |
| --- | --- | --- | --- | --- | --- | --- | --- |
| unrestricted | unrestricted | 0.497059 | 11 | 4 | 1.0 | 1.0 | 0 |
| constrained | constrained | 0.407059 | 11 | 4 | 1.0 | 1.0 | 0 |
| minimal | minimal | 0.407059 | 10 | 3 | 0.7 | 0.7 | 0.3 |

Observations:

- `minimal` is the only policy that clearly moves toward a smaller reconstruction footprint.
- It does so at a cost in coverage and reconstruction precision.
- `unrestricted` and `constrained` are indistinguishable on this run.

Draft conclusion:

- Minimal reconstruction starts to express a “least sufficient state” behavior, but the tradeoff is visible immediately in coverage.

---

## 5. Object-Aware Compression

Summary source:

- [object_aware_compression_summary.md](./srp_experiment/tmp/fixed_harnesses/object_aware_compression/object_aware_compression_summary.md)

| Suite | Object Support | Validation Coverage | Weighted Object Retention | Lost Important Objects | Critical Failures Before |
| --- | --- | --- | --- | --- | --- |
| chunk_score_only | False | 0.463356 | 0.684211 | 0 | 5 |
| chunk_score_plus_object_support | True | 0.463356 | 0.684211 | 0 | 5 |

Observations:

- The two compression settings are indistinguishable on the current benchmark.
- Object support did not change `weighted_object_retention`.
- Object support did not reduce `critical_failures_before`.

Draft conclusion:

- This is not evidence that object support is useless.
- It is evidence that the current benchmark does not apply enough object competition pressure to separate the policies.

Mechanism verification addendum:

- `score_changed_chunk_count = 6`
- `score_changed_rate = 1.0`
- `topk_changed_rate = 0.0`
- `topk_delta_count = 0`
- `rank_flip_rate = 0.0`
- `object_support_gain` is positive in every scenario

Interpretation:

- object support is participating in scoring
- the current top-k selection is still not sensitive enough to convert score changes into a different selected set
- the issue is not "object support is dead"; it is "the current decision surface still hides the difference"

Decision boundary sweep addendum:

- Top-k was swept through `10, 8, 6, 4, 2, 1`
- `first_changed_top_k` stayed empty in every scenario
- `topk_changed_rate = 0.0` across the sweep
- `rank_flip_rate = 0.0` across the sweep
- the smallest observed decision margin still did not produce a selected-set change

Interpretation:

- object support changes the score surface
- the current controlled tasks still sit on the same side of the decision boundary
- the next benchmark should therefore add asymmetric decoys and tighter top-k pressure, not just more content

Threshold analysis framing:

- Stage 2 should not be framed as "make object support win"
- Stage 2 should be framed as "find the conditions under which object support starts to win"
- the natural control variables are decoy count, keyword overlap, top-k budget, and object-support strength
- `decision_flip_distance` is the key quantity for tracking how far each condition sits from a top-k change

---

## 6. Round 1 Conclusions

What we can already say:

1. Recovery and reconstruction are good enough for baseline comparison.
2. Object-aware compression is not yet benchmark-separated.
3. Object support changes scores, but not yet the top-k selection in Round 1.
4. The current benchmark is useful, but only partially stress-tested.

What we should not claim yet:

- We should not claim object-aware compression improves retention on the current benchmark.
- We should not claim object support has no mechanism effect.
- We should not claim the object-support mechanism is ineffective in general.

What we should do next:

1. Keep this bundle as the Round 1 baseline.
2. Treat the decision boundary sweep as the formal Stage 1 result for object-aware compression.
3. Define Stage 2 as a threshold analysis over decoy strength, top-k budget, and object-support gain.
4. Add pressure through:
   - dependency branching
   - subject collision
   - budget pressure

---

## 7. Next Action

Recommended next step:

- build a threshold-analysis harness for object-aware compression and sweep decoy count, keyword overlap, top-k budget, and object-support strength

Recommended follow-up order:

1. Threshold analysis for object-aware compression
2. Identify the region where top-k selection begins to change
3. Keep recovery and reconstruction as fixed baseline references unless new seeds or tasks are needed
