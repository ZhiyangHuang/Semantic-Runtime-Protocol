# SRP Release Freeze Note

Release date: `2026-07-18`

Canonical manuscript:

- `fixed.md`

Manuscript mirror:

- `paper/SRP_ARXIV_DRAFT_V1.md`

Submission snapshot:

- `paper/SRP_PAPER_FINAL_V1.md`

Active evidence:

- `experiments/results/real_world_validation/locomo/run_20260718T2243500187290000`
- `experiments/results/real_world_validation/locomo/baseline_comparison/run_20260718T2244336007040000`

Excluded evidence:

- `LongMemEval` - pending real-data slice, not part of the current release gate

Verification:

- `python scripts/verify_release.py`: passed
- `arxiv_package/main.pdf`: 16 pages
- `arxiv_package/main.pdf` SHA256: `9805787D27BF3379B091E862B37BE1B68DD14A0A5AD4E234FDA66B68648416DD`
- terminology contract: satisfied

Repository boundary:

- Deleted files are concentrated in old experimental result bundles, obsolete audit documents, and superseded validation reports.
- New files are concentrated in the current release surface, the publication build layer, and the 7/18 LoCoMo evidence bundle.
- Modification is concentrated in `README.md`, `ARTIFACT_README.md`, `paper/`, `audit/`, `experiments/external_validation/runner.py`, `scripts/verify_release.py`, and the arXiv packaging layer.
- Historical material remains only in `audit/provenance/` and other compatibility paths.

Release state:

- Frozen for submission.
- No further structural changes should be made on the release branch unless they are required to repair verification or packaging.
