# Paper Source Reference Audit

This document records a reference audit for paper-facing SRP files.

Goal:

- confirm that `fixed.md` remains the canonical manuscript source
- confirm that `paper/SRP_ARXIV_DRAFT_V1.md` is treated as a synchronized manuscript mirror
- confirm that `paper/SRP_PAPER_FINAL_V1.md` is treated as a submission snapshot
- confirm that `paper/SRP_RELATED_WORK_V1.md` is only used as a supporting reconstruction document

No content changes were made as part of this audit.

## Review Scope

The following reference surfaces were checked:

- repository root documentation
- paper directory index
- audit documents
- release script
- archive documents

## Findings

| Path | Reference Behavior | Status | Notes |
| --- | --- | --- | --- |
| `README.md` | Points readers to `fixed.md` as the canonical manuscript and `paper/SRP_PAPER_FINAL_V1.md` as the release snapshot | PASS | Public repo entry point now separates canonical editing source from release snapshot. |
| `paper/README.md` | Lists `fixed.md` as canonical source and `SRP_ARXIV_DRAFT_V1.md` as synchronized mirror | PASS | Source hierarchy is now explicit and simplified. |
| `audit/PAPER_SOURCE_HIERARCHY.md` | Declares canonical / mirror / snapshot / reconstruction roles | PASS | This is the canonical source hierarchy record. |
| `audit/CLAIM_EVIDENCE_MAP.md` | Uses `paper/SRP_ARXIV_DRAFT_V1.md` as the main claim source, with `paper/SRP_PAPER_FINAL_V1.md` only as a finalized mirror if present | PASS | The claim map remains aligned with the synchronized manuscript mirror. |
| `audit/SRP_V1_STATIC_AUDIT_MAPPING.md` | Maps the current draft to the pre-release QA checklist | PASS | Still anchored on the primary manuscript. |
| `scripts/verify_release.py` | Requires `paper/SRP_PAPER_FINAL_V1.md` as a release file | PASS | Release verification follows the submission snapshot, not the reconstruction doc. |
| `audit/provenance/docs_archive/SRP_PAPER_DRAFT_V1.md` | References `SRP_RELATED_WORK_V1.md` as supporting context in historical material | PASS | Archive references are historical and do not affect current manuscript hierarchy. |

## Reference Summary

### Primary manuscript

- `fixed.md`

### Synchronized manuscript mirror

- `paper/SRP_ARXIV_DRAFT_V1.md`

### Submission snapshot

- `paper/SRP_PAPER_FINAL_V1.md`

### Supporting reconstruction document

- `paper/SRP_RELATED_WORK_V1.md`

## Conclusion

The paper source hierarchy is consistent:

- the canonical manuscript remains `fixed.md`
- the synchronized manuscript mirror remains the arXiv draft
- the final manuscript remains the release snapshot
- the related-work reconstruction file remains supporting-only

No structural changes are required based on this reference audit.


