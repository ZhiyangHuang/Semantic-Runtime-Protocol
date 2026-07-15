# SRP Evidence Escalation Protocol

This document freezes the protocol for evidence escalation in SRP.
It defines when vector evidence should remain sufficient and when SRP should consult stronger semantic evidence.
It does not define optimization, calibration, or adaptive policy learning.

---

## 1. Position

Evidence escalation sits alongside the semantic backend comparison study.
It is not a replacement for Phase III-A optimization and it is not an adaptive policy mechanism.

```text
Phase II
  Validated Feasible Region
  Boundary Stability
        ->
Phase III-A
  Constrained Parameter Optimization
        ->
Semantic Backend Comparison
  Evidence Source Augmentation
        ->
Evidence Escalation
  Verification Routing Policy
        ->
Phase III-B
  Adaptive Semantic Evolution
```

---

## 2. Purpose

The purpose of evidence escalation is to define a governed routing policy for verification evidence.

It answers:

> When is vector evidence sufficient, when should stronger semantic evidence be consulted, and when should disagreement be routed to governance?

It does not answer:

> How should the runtime mutate parameters online?

---

## 3. Escalation Boundary

Allowed:

- vector-only decision for high-confidence cases
- escalation to semantic evidence for boundary cases
- governance review for disagreement cases
- logging of evidence disagreement as research evidence

Disallowed:

- runtime self-modification
- autonomous deployment
- parameter optimization
- policy learning
- evidence-backed mutation authority

---

## 4. Routing Policy

The default routing policy is:

- high-confidence vector region -> vector-only decision
- boundary region -> escalate to stronger semantic evidence
- evidence-conflict region -> governance review

The local semantic evidence source is an evidence provider, not a controller.

---

## 5. Evidence Categories

### 5.1 High-confidence vector region

The vector signal is decisive and no escalation is needed.

### 5.2 Boundary region

The vector signal is near threshold or otherwise uncertain.
This region should preferentially escalate.

### 5.3 Evidence-conflict region

Vector and semantic evidence disagree.
This region should route to governance.

---

## 6. Authority Constraints

The escalation layer respects the SRP authority split:

- `Runtime` executes
- `Evidence` informs verification
- `Governance` decides

The local semantic evidence backend does not:

- mutate runtime state
- approve deployment
- rewrite history
- override governance

---

## 7. Output Contract

The study may produce:

- `escalation_matrix`
- `verification_routing_summary`
- `agreement_analysis`
- `governance_review_summary`

The study does not produce autonomous runtime updates.

---

## 8. Non-goals

This protocol does not include:

- reinforcement learning
- online adaptation
- policy learning
- runtime self-modification
- parameter optimization

---

## 9. Relation to Other Studies

This protocol depends on the semantic backend comparison evidence package and may later be applied to more detailed vector-vs-semantic-evidence experiments.

For the analysis artifact, see [SRP Evidence Escalation Analysis](SRP_EVIDENCE_ESCALATION_ANALYSIS.md).
For the auditable evidence layer, see [SRP Evidence Escalation Appendix](SRP_EVIDENCE_ESCALATION_APPENDIX.md).
