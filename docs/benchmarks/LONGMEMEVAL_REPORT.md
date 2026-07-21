# LongMemEval Report

## Release Artifacts

- shared-alignment artifact: `experiments/results/longmemeval_full_v5/`
- original research evaluation: retained under `experiments/external_validation/`
- status: closed with a dual-evaluation surface

## Summary

LongMemEval is intentionally split into two evaluation surfaces:

- Track A: original research evaluation with the official scorer
- Track B: shared benchmark alignment with the bridge artifact

Key properties:
- scorer authority remains with `experiments.external_validation`
- SRP diagnostics remain separate from the official score
- the no-payload-in-repository policy is preserved

## Related Audits

- `LONGMEMEVAL_ARTIFACT_AUDIT.md`
- `LONGMEMEVAL_CLOSURE_REVIEW.md`
- `LONGMEMEVAL_DUAL_EVALUATION_MODEL.md`
