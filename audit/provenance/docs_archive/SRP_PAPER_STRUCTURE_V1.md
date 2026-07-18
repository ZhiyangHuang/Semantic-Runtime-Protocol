# SRP Paper Structure V1

This document defines the paper-level structure for the current SRP research baseline.
It is a writing and positioning artifact, not a new experiment, not a mechanism design, and not a policy document.

## 1. Paper Goal

The paper should present SRP as a governed semantic evolution framework with:

- validated semantic evolution boundaries
- constrained optimization inside verified regions
- evidence-controlled verification and escalation
- explicit authority separation

It should not present SRP as a generic optimizer, a memory wrapper, or an autonomous adaptation engine.

## 2. Frozen Claims

The paper should freeze the following claims:

### Claim 1: Validated Semantic Evolution Boundaries

SRP identifies and validates feasible operating regions before optimization or adaptation.

### Claim 2: Governed Optimization inside Validated Regions

Optimization occurs only inside previously validated regions and remains advisory.

### Claim 3: Evidence-Controlled Semantic Verification

SRP can increase verification strength through additional semantic evidence without transferring authority.

## 3. Contribution Map

| Contribution | Core Question | SRP Evidence |
| --- | --- | --- |
| Validated semantic evolution boundaries | Where can SRP safely evolve? | Phase I, Phase II, Closure Validation |
| Governed optimization | Which configuration is preferred inside a verified region? | Phase III-A Round 1 |
| Evidence-controlled verification | When should SRP escalate evidence sources? | Semantic Backend Comparison, Evidence Escalation |

## 4. Architecture Figure

The paper should include a top-level figure that shows the frozen layering:

```text
                Governance
                    |
                    v
Runtime <---- Validation
   ^                |
   |                v
Calibration ----> Optimization

Evidence Layer
   |
   v
Backend Comparison
   |
   v
Escalation
```

The figure should emphasize:

- runtime executes
- calibration observes
- validation verifies
- optimization recommends
- evidence informs
- governance decides

## 5. Recommended Paper Outline

### 5.1 Introduction

- problem statement
- why semantic evolution needs governance
- what SRP contributes

### 5.2 SRP Runtime Background

- semantic transition kernel
- governed semantic evolution runtime
- authority split

### 5.3 Phase I and Phase II

- parameter observability
- constrained boundary discovery
- validated feasible regions
- closure validation

### 5.4 Phase III-A Constrained Optimization

- objective model
- candidate ranking
- governance approval
- advisory-only recommendation

### 5.5 Semantic Evidence Comparison

- vector baseline
- semantic evidence augmentation
- evidence escalation policy
- governance routing on disagreement

### 5.6 Discussion

- what SRP does and does not optimize
- why authority separation matters
- why evidence is not authority

### 5.7 Limitations

- current case set size
- offline heuristic fallback in the comparison package
- no Phase III-B adaptive learning yet

### 5.8 Conclusion

- SRP validates boundaries before optimization
- SRP optimizes only inside verified regions
- SRP escalates evidence without transferring authority

## 6. Related Work Positioning

The paper should position SRP against:

- RAG systems
- memory and retrieval systems
- agentic autonomy
- reinforcement learning for adaptation

SRP differs by:

- governing semantic state evolution
- validating boundaries before optimization
- separating evidence from authority
- delaying adaptive learning until governance is defined

## 7. Writing Rules

- Do not claim universal optimality
- Do not claim autonomous adaptation
- Do not claim local model authority
- Do not blur calibration, validation, optimization, and evidence
- Do not re-open the frozen baseline unless a new research phase is explicitly started

## 8. Recommended Next Artifact

After this structure document, the next useful paper-level artifact is a contribution map figure or a concise abstract draft.

