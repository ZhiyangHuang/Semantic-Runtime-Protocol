# Paper Source Hierarchy

This document defines the source-of-truth hierarchy for paper-facing SRP documents.

The goal is to keep the primary manuscript, submission snapshot, and supporting reconstruction notes from being conflated.

## 1. Primary Manuscript

`paper/SRP_ARXIV_DRAFT_V1.md`

Canonical arXiv-oriented manuscript.

This is the primary paper source for claim wording, structure, and evidence framing.

## 2. Submission Snapshot

`paper/SRP_PAPER_FINAL_V1.md`

Frozen submission candidate derived from the primary manuscript.

This file may mirror the primary manuscript at release time, but it is a snapshot rather than the canonical editing source.

## 3. Supporting Reconstruction Documents

`paper/SRP_RELATED_WORK_V1.md`

Historical reconstruction and rationale document.

This file is retained for traceability and explanation.
It is not a publication source and should not introduce new claims.

## 4. Synchronization Rule

Any claim, experiment, or artifact mapping change must be reflected in the primary manuscript first.

Supporting reconstruction documents must not outpace the primary manuscript.
If a supporting document drifts from the primary manuscript, the supporting document should be updated to match the primary source hierarchy.

## 5. Operational Rule

Recommended usage order:

1. Edit `paper/SRP_ARXIV_DRAFT_V1.md`
2. Sync `paper/SRP_PAPER_FINAL_V1.md` when preparing a submission snapshot
3. Maintain `paper/SRP_RELATED_WORK_V1.md` as a supporting reconstruction document only

