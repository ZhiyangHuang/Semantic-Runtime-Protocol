# Verify Release Boundary Review

This review checks whether `scripts/verify_release.py` expresses the release boundary correctly.

No code changes were made.

## Checked File

- `scripts/verify_release.py`

## Review Result

- Core paths are separated from legacy evidence paths.
- Runtime requirements remain distinct from legacy snapshot requirements.
- Legacy evidence is treated as a separate snapshot surface, not as the active runtime source of truth.
- Artifact promotion is not conflated with the release script boundary.

## Observations

### 1. Path Classification

The script uses separate lists for:

- `CORE_REQUIRED_PATHS`
- `LEGACY_EVIDENCE_PATHS`

This is the correct boundary expression.

### 2. Error Semantics

The script reports missing core and missing legacy evidence separately.

That distinction is important because core failure and legacy snapshot failure do not have the same meaning.

### 3. Release Condition

The release check treats core paths as required and legacy paths as expected legacy evidence for the release snapshot.

That keeps the runtime boundary explicit while still preserving historical reproducibility.

### 4. Artifact Boundary

`scripts/verify_release.py` does not define artifact promotion.

Artifact governance is handled by:

- `audit/ARTIFACT_POLICY.md`
- `audit/ARTIFACT_PROMOTION_DECISION.md`
- `audit/RELEASE_CHECKLIST.md`

## Conclusion

`scripts/verify_release.py` boundary is consistent with the current repository architecture:

- core runtime is separate
- curated artifacts are separate
- legacy evidence is separate

No code changes are required for this boundary review.

