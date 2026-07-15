# SRP Experiment Stack Overview

This document freezes the relationship between SRP's legacy measurement stack, the calibration / validation stack, and the evaluation / optimization studies.

It does not merge the two stacks.
It defines where each stack belongs in the research narrative.

---

## 1. Legacy Measurement Stack

Location:

```text
srp_experiment/
```

Role:

> Historical evaluation infrastructure for runtime behavior measurement.

Primary purpose:

- verify that SRP works as a runtime system
- measure compression and recovery behavior
- compare strategies and benchmark outputs
- support legacy ablation and evaluation workflows

Typical questions:

- Does SRP execute correctly?
- How well does the runtime recover and compress?
- Which benchmark or strategy performs better?

Status:

```text
Legacy / Maintained
```

---

## 2. Calibration and Validation Stack

Location:

```text
experiments/
```

Role:

> Research infrastructure for parameter boundary discovery and validation.

Primary purpose:

- discover parameter observability
- characterize boundary regions
- validate frozen parameter boundaries
- preserve authority separation

Subpackages:

- `experiments/sensitivity/`
- `experiments/calibration/`
- `experiments/validation/`

Typical questions:

- Where can SRP safely evolve?
- Which parameter regions are acceptable?
- Are the frozen boundaries stable under variation?

Status:

```text
Active Research Baseline
```

---

## 3. Evaluation and Optimization Studies

Location:

```text
experiments/evaluation/
experiments/optimization/
```

Role:

> Research infrastructure for semantic evidence comparison and constrained parameter optimization.

Primary purpose:

- compare evidence sources
- rank candidate configurations inside validated feasible regions
- preserve authority separation while increasing evidence quality

Typical questions:

- Is vector evidence sufficient, or should SRP escalate to local semantic evidence?
- Which parameter configuration performs best inside the frozen feasible region?
- How should SRP report tradeoffs without transferring runtime authority?

Status:

```text
Active Research Extension
```

---

## 4. Narrative Boundary

The legacy measurement stack answers:

> Does SRP work?

The calibration and validation stack answers:

> Where can SRP safely evolve?

The evaluation and optimization studies answer:

> How should SRP compare evidence sources and rank configurations inside known safe regions?

The evidence escalation analysis answers:

> When should SRP move from vector evidence to stronger semantic evidence, and when should disagreement be routed to governance?

The evidence escalation appendix provides the auditable records for those routing decisions.

The two stacks are related, but they are not the same research problem.

---

## 5. Usage Rule

Use `srp_experiment/` as background and historical evidence for runtime feasibility.

Use `experiments/` as the main contribution path for boundary characterization, closure validation, and future adaptive boundary design.

Use `experiments/evaluation/` and `experiments/optimization/` for evidence-source comparison and constrained parameter ranking inside frozen boundaries.

Use `SRP_RESEARCH_FREEZE_V1.md` as the current baseline checkpoint for the combined research stack.
