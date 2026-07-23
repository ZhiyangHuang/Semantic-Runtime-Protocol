# SRP arXiv Submission Checklist

Release target: `srp-v1.0.0-arxiv`

This checklist defines the final submission gate for the SRP arXiv release.
The purpose is not to expand the system scope, but to verify that the frozen
paper artifact, evidence boundary, and release metadata remain consistent.

---

## 1. PDF Visual Verification

Status: [ ]

Verify the final rendered PDF.

Checklist:

- [ ] Figure 1 clearly communicates:
      `proposal -> verification -> governance -> execution`

- [ ] Figure 2 clearly communicates:
      SRP positioning relative to retrieval, memory, agents, and RL

- [ ] Tables do not overflow page boundaries

- [ ] Equations render correctly

- [ ] Section numbering is consistent

- [ ] References render correctly

- [ ] No unexpected blank pages or layout artifacts

Table writing convention:

- [ ] Follow [SRP_TABLE_WRITING_CONVENTION.md](./SRP_TABLE_WRITING_CONVENTION.md) when adding or editing paper tables

---

## 2. Main Narrative Consistency

Status: [ ]

The paper must preserve one central message:

> SRP governs the admissibility of semantic state transitions.

Required concepts:

- [ ] semantic state transitions
- [ ] transition admissibility
- [ ] `evidence != authority`
- [ ] `recommendation != execution`
- [ ] `measure -> bound -> authorize -> audit`

Verify consistency in:

- [ ] Abstract
- [ ] Introduction
- [ ] Method
- [ ] Experiments
- [ ] Discussion
- [ ] Conclusion

---

## 3. Terminology Boundary Check

Status: [ ]

Ensure SRP is not reframed as:

- [ ] memory system
- [ ] RAG improvement
- [ ] retrieval optimization
- [ ] benchmark leaderboard method
- [ ] semantic truth determination system
- [ ] recovery-only mechanism

Preferred terminology:

- semantic runtime governance
- semantic transition governance
- admission boundary
- authority separation
- governed semantic mutation

---

## 4. arXiv Metadata Verification

Status: [ ]

Verify submission metadata matches the frozen artifact.

Checklist:

- [ ] Title matches:
      `Semantic Runtime Protocol: Evidence-Controlled Governance of Semantic State Transitions`

- [ ] Category selected:
      `cs.AI`

- [ ] Optional cross-list:
      `cs.SE`

- [ ] Author information verified

- [ ] Abstract matches submitted version

- [ ] Version corresponds to:
      `srp-v1.0.0-arxiv`

---

## 5. Release Freeze Verification

Status: [ ]

The following artifacts are frozen:

- [ ] `paper/SRP_ARXIV_DRAFT_V1.md`
- [ ] `paper/SRP_PAPER_FINAL_V1.md`
- [ ] `fixed.md`
- [ ] `paper/latex/body_content.md`
- [ ] `docs/release/SRP_V1_0_0_ARXIV_RELEASE_NOTE.md`

Before submission:

- [ ] `git status` clean
- [ ] release tag exists
- [ ] evidence manifest unchanged
- [ ] claim ledger unchanged
- [ ] no benchmark scope expansion

Reproducibility consistency:

- [x] review [SRP_REPRODUCIBILITY_CONSISTENCY_CHECKLIST.md](./SRP_REPRODUCIBILITY_CONSISTENCY_CHECKLIST.md)
- [x] runtime-overhead values have a matching release artifact
- [x] Phase VIII representation-robustness values have a matching release artifact
- [x] Phase VIII implementation-robustness values have a matching release artifact

---

## Final Release Decision

Submission approved:

[ ]

Reviewer:

Date:

Release tag:

`srp-v1.0.0-arxiv`
