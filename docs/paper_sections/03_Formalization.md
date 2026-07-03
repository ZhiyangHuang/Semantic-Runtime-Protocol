# Formalization Draft

## 1. Current-Paper Goal

This section gives the minimum formal layer needed for the current semester paper. The goal is not to close SRP as a grand theory. The goal is to give reviewers a clear semantic-state runtime abstraction, a measurable drift notion, and a modest finite-horizon claim that matches the experiment plan and lightweight baselines such as prompt accumulation, summarization memory, and retrieval-based memory.

The current paper should establish four things:

- semantic state is a first-class runtime object
- compression, recovery, validation, and update are explicit operators
- semantic drift can be measured over repeated cycles
- the system can be evaluated with a bounded, reviewer-friendly stability claim

## 2. Runtime State

We model SRP as a semantic-state runtime rather than a plain memory store.

Memory stores records. Runtime governs state transitions.

At interaction step `t`, the runtime state is:

```text
S_t = (M_t, V_t, P_t)
```

where:

- `M_t` denotes structured semantic memory
- `V_t` denotes the active vocabulary state
- `P_t` denotes the policy state governing how state is transformed

This is the current-paper version of the state tuple. It is intentionally minimal but still expressive enough to support compression, recovery, validation, and update under bounded semantic drift.

The minimality question is intentionally left open. The paper should not claim that this tuple is mathematically final.

## 3. State Transition Operators

SRP defines four runtime operators over semantic state.

### 3.1 Compression

```text
C : S_t -> Z_t
```

`C` maps a semantic state to a compact representation `Z_t`. In practice, `Z_t` can be a structured summary, slot-value state, schema-constrained JSON, or another machine-readable encoding.

### 3.2 Recovery

```text
R : Z_t -> S_t'
```

`R` reconstructs an operational semantic state `S_t'` from the compressed form.

### 3.3 Validation

```text
Val : (S_t, S_t') -> [0, 1]
```

`Val` estimates whether the recovered state preserves task-relevant semantics. This can be implemented with embedding similarity, rule-based checks, or LLM-as-judge scoring.

### 3.4 Update

```text
U : (S_t', F_t) -> S_{t+1}
```

`U` updates the semantic state from the recovered state and observed feedback `F_t`, such as downstream task outcome, user correction, or validator output.

## 4. Observable Semantics

The paper should define meaning through observable behavior, not through metaphysical equivalence.

Let `O` be a task-relevant observation operator:

```text
O : S -> Y
```

Examples of `O(S)` include:

- downstream answers
- retained user preferences
- task decisions derived from the state

Semantic error between original and recovered state is:

```text
epsilon(S, S') = d(O(S), O(S'))
```

where `d` is a task-appropriate distance over observable behavior.

The practical goal is bounded degradation:

```text
epsilon(S, S') <= tau
```

for an application-dependent tolerance `tau`.

## 5. State Sufficiency

The paper can soften the state-existence question by avoiding exact equality between full history and state-based prediction.

Instead of requiring:

```text
P(Y_{t+1} | H_t) = P(Y_{t+1} | S_t)
```

the paper can use:

```text
P(Y_{t+1} | H_t) approx P(Y_{t+1} | S_t)
```

and define a state sufficiency error:

```text
epsilon_state = D(P(Y | H), P(Y | S))
```

where `D` is a task-appropriate predictive or behavioral distance.

This is one of the current-paper additions that improves acceptance chances because it makes the theory empirical and testable instead of absolute.

## 6. Iterative Drift

The central failure mode in long-horizon interaction is repeated transformation loss.

Consider the iterative process:

```text
S_0 -> C -> Z_0 -> R -> S_1 -> C -> Z_1 -> R -> S_2 -> ...
```

We define cumulative drift at step `k` as:

```text
Delta_k = d(O(S_0), O(S_k))
```

This is the main measurable object in the paper.

## 7. Bounded Semantic Drift

We say that an SRP instance satisfies bounded semantic drift over horizon `T` if there exists a tolerance sequence `{tau_k}` such that for all `k <= T`:

```text
Delta_k <= tau_k
```

In the strongest practical case, `tau_k` grows sublinearly or remains approximately flat over repeated cycles.

This is the exact form of the claim the experiments should support.

## 8. Finite-Horizon Claim

The paper should use a conservative claim:

> If compression and recovery preserve task-relevant invariants up to bounded local error, and update does not amplify error beyond a bounded factor, then cumulative semantic drift remains bounded over a finite horizon.

This is intentionally weaker than claiming convergence or universal semantic correctness.

## 9. Assumption Set

The finite-horizon argument can be built on three assumptions:

- `A1. Local boundedness`: each compression-recovery step incurs error at most `e`
- `A2. Validator consistency`: the validation score is positively correlated with observable task preservation
- `A3. Non-explosive update`: update does not magnify incoming error by more than factor `lambda`

where `0 <= lambda <= 1` in a contractive case, or `lambda > 1` but still bounded over the tested horizon.

## 10. Stability Region

For future refinement, the finite-horizon story can later be reframed as a stability-region argument.

A stable SRP regime would require:

- drift below threshold `alpha`
- vocabulary error below threshold `beta`
- validator quality above threshold `gamma`

This is a strong direction for the long-term design, but it is not required for the current semester paper.

## 11. Drift Bound Sketch

### Lemma 1. Finite-Horizon Drift Bound

Suppose for each step `t`:

```text
d(O(S_t), O(S_t')) <= e_t
```

and the update operator satisfies:

```text
d(O(U(S_t', F_t)), O(U(S_t, F_t))) <= lambda * d(O(S_t'), O(S_t))
```

Then after `k` compression-recovery-update cycles:

```text
Delta_k <= sum_{i=0}^{k-1} lambda^{k-1-i} e_i
```

If `e_i <= e` for all `i`, then:

```text
Delta_k <= e * sum_{i=0}^{k-1} lambda^i
```

which yields:

- `Delta_k <= k * e` when `lambda = 1`
- `Delta_k <= e / (1 - lambda)` when `0 <= lambda < 1`

### Interpretation

This lemma does not prove optimality. It gives a reviewer-friendly reason why structured validation and constrained update may stabilize long-horizon interaction better than unconstrained summarization.

## 12. Failure Boundary

The first paper should explicitly show where SRP fails or becomes unstable. This improves credibility and makes the theory falsifiable.

Useful failure cases:

- vocabulary corruption
- validator failure
- recovery failure
- concept explosion under repeated updates

This section should stay in the current paper because it helps reviewers see the limits of the proposal.

## 13. What The Current Paper Does Not Claim

To keep the paper credible, the first version should avoid claiming:

- universal semantic correctness
- exact reconstruction of meaning
- full convergence of arbitrary long-horizon interaction
- superiority across all models and tasks

Instead, the paper should claim:

- a semantic-state runtime abstraction for semantic state
- a measurable formulation of iterative semantic drift
- an empirical and partially formal argument for improved finite-horizon stability

## 14. Open Questions To Preserve

These are important, but they should stay in long-term design notes rather than the main paper:

- whether `S_t = (M_t, V_t, P_t)` is minimal
- whether `P(Y_{t+1} | H_t)` can be approximated well enough by `P(Y_{t+1} | S_t)` to justify `S_t` as a real state object
- whether `M_t` is the right unit of storage, or whether concept-level state is better
- whether `V_t` is necessary for a minimal sufficient state, or whether concept state alone is enough
- whether the strongest invariant is semantic equivalence, behavioral equivalence, or vocabulary stability
- whether the strongest invariant should be defined over behavior preservation rather than representation preservation
- whether a failure theorem should be stated alongside the drift lemma
- whether the runtime lifecycle should include freeze, merge, or delete operators
- whether SRP should be framed as a semantic predictive state rather than only a semantic runtime
- whether vocabulary mapping should be elevated from a helper field to a first-class semantic contract
- whether semantic updates should eventually be modeled as transactions with validation, commit, and rollback

## 15. How To Use This In The Paper

This formal section is enough for a first submission if paired with a clean experiment section. The writing strategy should be:

- define state and operators clearly
- define drift in terms of observable behavior
- present a modest finite-horizon lemma
- support the theory with iterative experiments

That combination is much safer than trying to prove a grand semantic theory in the first paper.
