# SRP Runtime Semantic Verification Checklist

## Goal

This checklist turns the refined SRP semantic verification design into an implementation-oriented protocol compliance sheet.

It is meant to answer one question:

> Is the current verifier a true runtime semantic protocol layer, or still just a smarter text scorer?

The checklist below assumes the verifier should operate on a typed semantic state, not raw text.

## Protocol Rule 1

> Runtime verification SHALL operate on typed semantic representations rather than directly on lexical surface forms.

This rule unifies the checklist.

It means:

- raw text is only input to semantic parsing
- typed semantic state is the verification target
- lexical surface form is not the primary object of commitment

## 1. Semantic State Must Be Explicit

- [ ] Define the semantic state type in the paper.
- [ ] Choose one concrete representation:
  - [ ] typed object set
  - [ ] typed semantic graph
  - [ ] typed tuple structure
- [ ] Specify the core slots of the state:
  - [ ] facts
  - [ ] constraints
  - [ ] relations
  - [ ] anchors
  - [ ] claims
  - [ ] execution intents
- [ ] Specify any optional slots:
  - [ ] temporal markers
  - [ ] negation markers
  - [ ] sensitive identifiers
  - [ ] provenance pointers

## 2. Parser Must Not Be A Blind Black Box

- [ ] The parser should output structured semantic objects, not only text spans.
- [ ] Each object should carry a confidence value.
- [ ] Each object should carry an evidence pointer.
- [ ] The verifier should be able to inspect parser confidence.
- [ ] The verifier should be able to trace an object back to its source evidence.
- [ ] Low-confidence objects should not be treated as equally reliable as high-confidence objects.

### Parser output shape

Suggested minimum:

```text
Object
  - type
  - value
  - confidence
  - evidence_pointer
```

## 3. Coverage Must Be Weighted

- [ ] Replace flat retention with weighted semantic coverage.
- [ ] Define different weights for different object types.
- [ ] At minimum, distinguish:
  - [ ] facts
  - [ ] constraints
  - [ ] relations
  - [ ] anchors
- [ ] Make missing constraints more costly than missing low-value facts.
- [ ] Report which objects were missing, not only the total coverage score.

### Example weighting policy

```text
constraints > facts > relations > anchors
```

This can be adjusted later, but the paper should make the weighting explicit.

## 4. Object Alignment Must Precede Entailment

- [ ] Do not run entailment directly on raw recovered text.
- [ ] First align source objects and recovered objects.
- [ ] Then apply entailment checks on matched object pairs.
- [ ] Explicitly handle partial coverage.
- [ ] Explicitly handle object mismatch.

### Alignment rule

The verifier should ask:

1. Which source object maps to which recovered object?
2. Which source object has no recovered counterpart?
3. Which recovered object has no source justification?

## 5. Entailment Must Be Bidirectional

- [ ] Check `source -> recovered`.
- [ ] Check `recovered -> source`.
- [ ] Roll back if either direction fails.
- [ ] Treat one-way entailment as incomplete.

### Interpretation

- [ ] both directions pass: semantically stable
- [ ] only one direction passes: risky, likely rollback
- [ ] neither passes: fail

## 6. Capability Verification Must Be Separate

- [ ] Do not reduce capability checking to a keyword blacklist.
- [ ] Check whether the recovered state can already function as:
  - [ ] a direct answer
  - [ ] a decision
  - [ ] a plan
  - [ ] an execution instruction
- [ ] Reject states that are already too executable.

### Hard reject examples

- [ ] "the answer is ..."
- [ ] "therefore the final answer is ..."
- [ ] "the solution is ..."
- [ ] "the task has been completed"
- [ ] "this proves that ..."

## 7. Evidence Sufficiency Must Be A Separate Gate

- [ ] Do not commit if the current evidence is too thin.
- [ ] Add an explicit evidence sufficiency check.
- [ ] Allow rollback or retry when the parser has low confidence or missing support.
- [ ] Separate evidence sufficiency from coverage.

### Evidence sufficiency questions

- [ ] Is there enough evidence to justify the recovered state?
- [ ] Is the object supported by one source or multiple sources?
- [ ] Is the object stable under recovery?
- [ ] Is the object traceable back to the archive or the evidence store?

## 8. Risk Must Be Aggregated, Not Binary

- [ ] Do not force every borderline case into commit or rollback.
- [ ] Use at least three risk levels:
  - [ ] low
  - [ ] medium
  - [ ] high
- [ ] Map risk to action:
  - [ ] low -> commit
  - [ ] medium -> retry / refine
  - [ ] high -> rollback

### Suggested risk logic

- [ ] high leakage risk should always rollback
- [ ] low coverage with high confidence should retry or rollback depending on the threshold
- [ ] medium risk should not silently commit

## 9. Archive Access Must Be Governed

- [ ] Separate runtime semantic state from verbatim archive.
- [ ] Treat the archive as audit-only by default.
- [ ] Access the archive through governed retrieval, not raw prompt replay.
- [ ] Make evidence queries explicit and policy-controlled.

### Access policy checklist

- [ ] runtime state can be used for recovery
- [ ] evidence store can be queried for support
- [ ] verbatim archive is not the default prompt input
- [ ] audit interface is separate from runtime execution

## 10. Commit Rule Must Be Clear

- [ ] Commit only if:
  - [ ] coverage passes
  - [ ] object alignment passes
  - [ ] bidirectional entailment passes
  - [ ] capability check passes
  - [ ] evidence sufficiency passes
  - [ ] leakage check passes
- [ ] Retry if borderline but recoverable.
- [ ] Rollback if leakage or contradiction is detected.

### Simple commit table

| Coverage | Alignment | Entailment | Capability | Evidence | Leakage | Action |
|---|---:|---:|---:|---:|---:|---|
| pass | pass | pass | pass | pass | no | commit |
| pass | pass | pass | pass | fail | no | retry |
| pass | fail | any | any | any | no | rollback |
| any | any | any | fail | any | no | rollback |
| any | any | any | any | any | yes | rollback |

## 11. Calibration Must Be Explicit

- [ ] Build a small calibration set before finalizing thresholds.
- [ ] Include:
  - [ ] valid paraphrases
  - [ ] invalid reversals
  - [ ] borderline compressions
  - [ ] answer-shaped leaks
- [ ] Tune thresholds to accept paraphrase but reject answer leakage.

### Default calibration target

- [ ] accept semantic paraphrase
- [ ] reject polarity reversal
- [ ] reject answer completion
- [ ] reject unsupported conclusions

## 12. What This Is Trying To Become

- [ ] A runtime semantic protocol
- [ ] Not just a text scoring module
- [ ] Not just a prompt engineering wrapper

If these boxes are mostly checked, the design is probably close to a protocol.

If many of them remain unchecked, it is still mostly a smarter verifier over text.
