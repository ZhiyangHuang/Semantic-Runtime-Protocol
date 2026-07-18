# Paper Source Hierarchy

This document defines the source-of-truth hierarchy for paper-facing SRP documents.

The goal is to keep the canonical manuscript, synchronized manuscript mirror, submission snapshot, and supporting reconstruction notes from being conflated.

## 1. Canonical Manuscript

`fixed.md`

Canonical release manuscript source.

This is the primary editing source for claim wording, structure, and evidence framing during the release pass.

## 2. Synchronized Manuscript Mirror

`paper/SRP_ARXIV_DRAFT_V1.md`

Mirror of the canonical manuscript used by paper-facing release materials.

This file should track `fixed.md` during the release pass.

## 3. Submission Snapshot

`paper/SRP_PAPER_FINAL_V1.md`

Frozen submission candidate derived from the primary manuscript.

This file may mirror the primary manuscript at release time, but it is a snapshot rather than the canonical editing source.

## 4. Supporting Reconstruction Documents

`paper/SRP_RELATED_WORK_V1.md`

Historical reconstruction and rationale document.

This file is retained for traceability and explanation.
It is not a publication source and should not introduce new claims.

## 5. Synchronization Rule

Any claim, experiment, or artifact mapping change must be reflected in `fixed.md` first.

The synchronized manuscript mirror must not outpace `fixed.md`.
If a supporting document drifts from the canonical source, the supporting document should be updated to match the hierarchy.

## 6. Operational Rule

Recommended usage order:

1. Edit `fixed.md`
2. Sync `paper/SRP_ARXIV_DRAFT_V1.md` from the canonical source
3. Sync `paper/SRP_PAPER_FINAL_V1.md` when preparing a submission snapshot
4. Maintain `paper/SRP_RELATED_WORK_V1.md` as a supporting reconstruction document only
