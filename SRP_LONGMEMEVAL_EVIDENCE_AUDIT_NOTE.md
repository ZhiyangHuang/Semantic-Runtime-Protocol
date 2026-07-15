# SRP LongMemEval Evidence Audit Note

This note freezes the audit boundary for the LongMemEval evidence run.
It is an audit artifact, not a promotion decision, not a new benchmark run, and not a theory revision.

## 1. Audit Purpose

The LongMemEval evidence run is intended to support external validity only after its runtime contract, scoring path, and diagnostic metrics are auditable.

The audit checks whether the reported results can be interpreted without conflating:

- memory reconstruction quality
- answer generation fidelity
- scorer alignment
- recovery cost accounting

## 2. What Was Verified

- Same benchmark split
- Same seed set
- Same shared local-vLLM endpoint
- Same model name
- Same tokenizer
- Same prompt template id
- Same temperature
- Same max token budget
- Same shared generation backend across baselines and SRP
- Same evaluation script

## 3. Metric Interpretation Boundary

The following distinctions are frozen:

- `semantic_coverage` measures target semantic-unit recovery
- `relation_accuracy` measures target relation recovery
- `hallucinated_relation_rate` measures extra relations recovered beyond the target state
- `answer_accuracy` measures answer similarity under the benchmark scorer
- `evidence_cost` measures internal recovery cost units, not raw token count

Because these quantities measure different layers, they may not all move in lockstep.

The current LongMemEval evidence candidate favors semantic recall over aggressive relation pruning.
In practice, this means recovered relations can remain as explicit semantic candidates when they are plausible but not yet fully verified.
Future provenance-aware versions of SRP may attach observed/inferred labels, confidence scores, evidence identifiers, user-verification status, and a `promotion_state` field (`candidate`, `verified`, `rejected`) so that pruning can be deferred to a later governance step instead of being forced into the recovery layer.
In that framing, `hallucinated_relation_rate` is better read as a tendency to generate extra semantic candidates beyond the target state, not as permission to treat them as verified facts.

## 4. Statistical Reporting Boundary

The current LongMemEval slice is a predefined validation slice with 48 records.
Its statistics are reported as descriptive statistics only.

This means:

- mean, standard deviation, and 95% CI may be reported for the fixed slice
- the slice-level CI is not treated as benchmark-wide inferential evidence
- the sample-size limitation must be stated explicitly in the report

Inferential statistics are deferred until a larger benchmark slice is used.

## 5. Threats to Validity

The current LongMemEval evidence slice is intentionally narrow and should be interpreted with the following limitations in mind:

- The evidence slice contains 48 predefined records and is intended for pipeline validation rather than complete benchmark evaluation.
- Statistical summaries are descriptive only and should not be interpreted as inferential claims about the full LongMemEval benchmark.
- Scorer alignment is now `pass` for the frozen LongMemEval evidence slice because the remaining temporal and multi-hop acceptance items have been closed on the current slice.
- Promotion to paper-facing evidence is now a decision gate rather than an unresolved audit issue.

## 6. Why Promotion Is Ready for Decision

Promotion to external-validity evidence is ready for decision because the LongMemEval result now satisfies the frozen audit boundary:

- failure decomposition is interpretable and reproducible
- the shared runtime contract is stable across reruns
- scorer alignment is satisfied on the frozen slice

The scorer-alignment closure targets are listed explicitly in `SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md` and are now satisfied for the frozen LongMemEval slice.

The current result is therefore a promotable evidence package under a frozen evaluation contract.

## 7. Relation to the Paper

The paper may reference LongMemEval as a promoted evidence package under the frozen runtime contract, while still stating the slice-level limitations explicitly.
