# Release Checklist

Use this checklist when regenerating or reviewing the SRP release surface.

## Manuscript

- [x] `fixed.md` is the canonical manuscript source
- [x] `paper/SRP_ARXIV_DRAFT_V1.md` mirrors the canonical manuscript
- [x] `paper/SRP_PAPER_FINAL_V1.md` mirrors the submission snapshot

## Summary

- [x] `paper/SRP_MAIN_RESULTS_SUMMARY_V1.md` is generated from `paper/main_evidence_manifest.json`
- [x] `paper/SRP_MAIN_RESULTS_SUMMARY_V1.json` matches the markdown summary
- [x] `paper/SRP_MAIN_RESULTS_SUMMARY_V1.metadata.json` records generation metadata

## Coverage

- [x] `experiments/transition_role/report_coverage.py` generates both markdown and JSON reports
- [x] transition-role coverage paths resolve correctly for all instantiated workloads

## Verification

- [x] `python scripts/verify_release.py` passes
- [x] paper-facing links point to the current release docs

## Release Rule

- [x] historical audit artifacts are kept out of the active release surface
