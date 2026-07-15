# SRP Contribution Map V1

This document freezes the contribution structure for the SRP paper.
It is a visualization artifact, not a new experiment, not a mechanism design, and not a policy document.

## 1. Contribution Topology

```text
                         Governance
                             |
                             v
                +---------------------------+
                |      Semantic Runtime      |
                |  runtime executes state    |
                |  transitions               |
                +---------------------------+
                   ^                   ^
                   |                   |
                   |                   |
         +----------------+   +----------------------+
         |   Calibration   |   |      Validation      |
         |  observes       |   |  verifies boundaries |
         |  parameters      |   |  invariants          |
         +----------------+   +----------------------+
                   |
                   v
         +---------------------------+
         |   Phase III-A Optimization |
         |  candidate generation      |
         |  objective scoring         |
         |  advisory recommendation   |
         +---------------------------+
                   |
                   v
         +---------------------------+
         |       Evidence Layer       |
         | vector evidence            |
         | semantic evidence          |
         | escalation routing         |
         +---------------------------+
```

## 2. Core Separation Claims

- `Evidence != Authority`
- `Optimization != Runtime Control`
- `Calibration != Learning`
- `Validation != Mutation`

These separations are the central thesis of the paper.

## 3. Contribution Blocks

### 3.1 Validated Semantic Evolution Boundaries

What it contributes:

- Phase I parameter observability
- Phase II constrained boundary discovery
- closure validation of frozen regions

What it answers:

> Where can SRP safely evolve?

### 3.2 Governed Optimization inside Validated Regions

What it contributes:

- Phase III-A constrained optimization
- objective-based candidate ranking
- advisory-only recommendation

What it answers:

> Which configuration is preferred inside a verified region?

### 3.3 Evidence-Controlled Semantic Verification

What it contributes:

- semantic backend comparison
- evidence escalation analysis
- escalation protocol and appendix

What it answers:

> When should SRP escalate from vector evidence to stronger semantic evidence?

## 4. Narrative Guardrails

The contribution map should prevent the paper from being read as:

- a memory system paper
- a RAG enhancement paper
- an RL adaptation paper
- a local model controller paper

Instead, the paper should be read as a governed semantic evolution framework with explicit authority separation.

## 5. Figure Usage Rule

This map should be used to guide:

- abstract drafting
- introduction framing
- related work positioning
- figure design
- claim selection

It should be treated as the paper's coordinate system.

