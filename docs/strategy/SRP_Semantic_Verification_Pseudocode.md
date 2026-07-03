# SRP Semantic Verification Pseudocode

## Purpose

This note turns the semantic verification design into a more operational form.

The goal is to decide whether a recovered state should:

- commit
- rollback
- or be marked for manual inspection

This version is intentionally practical.
It is not the final implementation.

## Inputs

For each SRP cycle, the verifier receives:

- `source_state`
- `recovered_state`
- `validation_targets`
- optional `anchor_state`

The verifier should not receive:

- `expected_keywords` from benchmark shaping
- future answer labels
- hidden chain-of-thought traces

## High-Level Idea

The verifier is a three-gate filter:

1. preserve the important state
2. keep semantic direction aligned
3. block answer leakage

Only if all three pass should the cycle commit.

## Pseudocode

```text
function verify_cycle(source_state, recovered_state, validation_targets, anchor_state=None):
    preservation = check_state_preservation(source_state, recovered_state, validation_targets)
    direction = check_semantic_direction(source_state, recovered_state)
    leakage = check_answer_leakage(recovered_state)

    if leakage == true:
        return {
            "passed": false,
            "action": "rollback",
            "reason": "answer_leakage_detected",
            "preservation": preservation,
            "direction": direction,
            "leakage": leakage
        }

    if preservation.score < PRESERVATION_THRESHOLD:
        return {
            "passed": false,
            "action": "rollback",
            "reason": "insufficient_state_preservation",
            "preservation": preservation,
            "direction": direction,
            "leakage": leakage
        }

    if direction.score < DIRECTION_THRESHOLD:
        return {
            "passed": false,
            "action": "rollback",
            "reason": "semantic_direction_mismatch",
            "preservation": preservation,
            "direction": direction,
            "leakage": leakage
        }

    return {
        "passed": true,
        "action": "commit",
        "reason": "all_checks_passed",
        "preservation": preservation,
        "direction": direction,
        "leakage": leakage
    }
```

## Subcheck 1: State Preservation

This check asks whether the recovered state still contains the required semantic payload.

```text
function check_state_preservation(source_state, recovered_state, validation_targets):
    fact_hits = measure_fact_retention(source_state, recovered_state)
    constraint_hits = measure_constraint_retention(validation_targets, recovered_state)
    relation_hits = measure_relation_retention(source_state, recovered_state)
    anchor_hits = measure_anchor_alignment(anchor_state, recovered_state)

    score = weighted_sum(
        fact_hits,
        constraint_hits,
        relation_hits,
        anchor_hits
    )

    return {
        "score": score,
        "fact_hits": fact_hits,
        "constraint_hits": constraint_hits,
        "relation_hits": relation_hits,
        "anchor_hits": anchor_hits
    }
```

### Recommended interpretation

- facts should survive
- constraints should survive
- relations should survive when relevant
- anchor-compatible meaning should survive

### What this check should not do

- it should not require exact wording
- it should not require the original keywords
- it should not reject legitimate paraphrase

## Subcheck 2: Semantic Direction

This check asks whether the recovered wording stays on the same side of meaning.

```text
function check_semantic_direction(source_state, recovered_state):
    entailment_score = measure_entailment(source_state, recovered_state)
    contradiction_score = measure_contradiction(source_state, recovered_state)
    polarity_flip_score = measure_polarity_flip(source_state, recovered_state)
    over_specificity_score = measure_answer_like_specificity(recovered_state)

    score = entailment_score - contradiction_score - polarity_flip_score - over_specificity_score

    return {
        "score": score,
        "entailment_score": entailment_score,
        "contradiction_score": contradiction_score,
        "polarity_flip_score": polarity_flip_score,
        "over_specificity_score": over_specificity_score
    }
```

### Recommended interpretation

- paraphrase is allowed
- lexical substitution is allowed
- semantic compaction is allowed
- contradiction is not allowed
- reversal is not allowed
- answer-like over-specificity is not allowed

## Subcheck 3: Answer Leakage

This check asks whether the recovered state has turned into an answer.

```text
function check_answer_leakage(recovered_state):
    if contains_explicit_answer_templates(recovered_state):
        return true

    if contains_task_completion_language(recovered_state):
        return true

    if contains_solution_summary_language(recovered_state):
        return true

    if contains_benchmark_shaped_phrases(recovered_state):
        return true

    return false
```

### Hard reject examples

- "the answer is ..."
- "therefore the final answer is ..."
- "the solution is ..."
- "the task has been completed"
- "this proves that ..."

## Decision Table

| Preservation | Direction | Leakage | Action | Meaning |
|---|---:|---:|---|---|
| pass | pass | no | commit | good semantic recovery |
| pass | fail | no | rollback | meaning drifted or reversed |
| fail | pass | no | rollback | state lost key content |
| fail | fail | no | rollback | both state and meaning are unstable |
| any | any | yes | rollback | answer leakage is a hard stop |

## Threshold Guidance

The thresholds should be conservative at first.

Suggested starting point:

- `PRESERVATION_THRESHOLD = 0.70`
- `DIRECTION_THRESHOLD = 0.65`

These are only starting values.

They should be calibrated on:

- valid paraphrases
- invalid reversals
- borderline compressions

## What Makes A Case Borderline

A borderline case is one where:

- the facts are mostly preserved
- the wording changes a lot
- the state is still semantically similar
- but the output starts to feel too close to a solution

These cases should usually rollback at first.

If later we want to allow them, we should do so only after explicit calibration.

## What This Design Tries To Balance

This verifier tries to balance three competing goals:

- let SRP transform wording across long tasks
- keep meaning from flipping
- stop answer caching from leaking into memory

That balance is the main reason for separating the checks.

## Why This Is Safer For SRP

This design is safer than pure keyword matching because it:

- does not require verbatim overlap
- can tolerate lexical change
- can still catch semantic drift

It is safer than a free-form LLM judge because it:

- keeps leakage as a hard stop
- prevents answer-shaped rewrites from being rewarded
- forces explicit preservation and direction checks

## Where It Fits In SRP

This verifier should sit at the commit/rollback boundary.

It should not influence:

- compression prompt wording
- recovery prompt wording
- runtime vocabulary shaping

Its job is only to decide whether the recovered state is admissible.

## My Current Judgment

This is the most SRP-compatible version of a semantic verifier that still seems practical.

It is likely suitable for SRP if we want:

- long-task lexical flexibility
- controlled semantic translation
- lower dependence on benchmark-shaped keywords

It may be too strict if we want:

- very aggressive abstraction
- highly creative recovery
- broad open-ended paraphrase

If that becomes a priority, we would need to relax the thresholds very carefully.

