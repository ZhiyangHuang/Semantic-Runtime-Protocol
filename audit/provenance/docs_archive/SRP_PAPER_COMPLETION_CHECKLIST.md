# SRP Paper Completion Checklist

This checklist tracks paper-readiness work for SRP.
It is a living project artifact, not a result report.

Frozen management version: `v1.0`

## Status Overview

| Layer | Current State | Main Question | Paper Main Result? |
| --- | --- | --- | --- |
| Framework | Done | Is the experiment framework stable? | No |
| Audit | Mostly done | Are runtime contract, scorer, and statistics auditable? | No |
| Strong baseline evidence package | Done | Are representative memory systems implemented and compared fairly? | No |
| Evidence promotion | Approved (frozen scope) | Can the audited evidence be promoted into paper-facing results? | Yes |
| Additional benchmarks | Frozen | Should the evidence package be broadened to more benchmarks? | No |

## Research Progress

### Theory

- [x] Core architecture frozen
- [x] Core claims frozen
- [x] Phase I to Phase VIII evidence chain defined
- [x] Representation invariance boundary defined
- [x] Implementation independence boundary defined

### Evidence

- [x] Phase I observability
- [x] Phase II boundary validation
- [x] Phase III-A governed optimization
- [x] Evidence escalation
- [x] Phase V retention and drift
- [x] Phase VI relation-aware recovery
- [x] Phase VII recommendation stability
- [x] Phase VII-B parameter sensitivity
- [x] Phase VIII-A cross-domain validation
- [x] Phase VIII-B representation invariance experiment
- [x] Phase VIII-C implementation independence experiment

### External Validity

- [x] External validation plan frozen
- [x] External validation implementation plan frozen
- [x] External validation adapter architecture frozen
- [x] Public benchmark family frozen
- [x] Baseline matrix frozen
- [x] Baseline capability matrix frozen
- [x] LoCoMo benchmark ingestion complete
- [x] LoCoMo manual sanity harness implemented
- [x] Temporal attribution protocol frozen
- [x] LoCoMo calibration artifact complete
- [ ] LoCoMo scorer alignment acceptance
- [x] LoCoMo calibration-aware rerun complete
- [x] LongMemEval adapter validation complete
- [x] LongMemEval calibration-aware rerun complete
- [x] LongMemEval evidence contract frozen
- [x] LongMemEval statistical reporting layer
- [x] LongMemEval scorer alignment acceptance
- [x] LongMemEval evidence run
- [x] LongMemEval evidence audit note
- [x] LongMemEval scorer alignment audit
- [x] Evidence audit specification frozen
- [x] Strong memory-system baseline layer frozen
- [x] Strong baseline implementation
- [x] Strong baseline evidence comparison
- [x] Public benchmark evidence package
- [x] Cross-model validation
- [ ] Statistical significance tests
- [x] Confidence intervals / descriptive analysis for fixed slice

### Strong Baseline Matrix

| Baseline | Capability | Implemented | Evidence | Frozen |
| --- | --- | --- | --- | --- |
| Full Context | Yes | Yes | Yes | Yes |
| Sliding Window | Yes | Yes | Yes | Yes |
| Vector RAG | Yes | Yes | Yes | Yes |
| Mem0 | Yes | Yes | Yes | Yes |
| Graphiti | Yes | Yes | Yes | Yes |
| Letta | Yes | Yes | Yes | Yes |
| MemMachine | Yes | Yes | Yes | Yes |

## Paper Preparation

### Reproducibility

- [x] Config-driven experiment entrypoints
- [x] Result package export structure
- [ ] End-to-end reproduction guide
- [ ] Artifact bundle
- [ ] Seeded rerun instructions

### Writing

- [x] Paper draft skeleton
- [x] Paper final draft
- [ ] External validity section
- [ ] Failure analysis
- [ ] Reproducibility / artifact appendix
- [ ] Final proofreading pass

### Submission Readiness

- [ ] Figures finalized
- [ ] Tables finalized
- [ ] References checked
- [ ] Artifact DOI / Zenodo
- [ ] Anonymous version
- [ ] Camera-ready checklist

## Current Next Steps

1. Package the LongMemEval evidence bundle for the paper-facing results and appendix.
2. Keep the current LongMemEval slice descriptive-only unless a larger official benchmark subset is selected for inferential testing.
3. Treat evidence promotion as a decision gate, not a new experimental stage.
4. Use the LoCoMo manual sanity harness, temporal attribution protocol, and calibration-aware rerun as calibration artifacts only.
5. Keep statistical reporting descriptive for the fixed slice unless a larger official benchmark subset is selected for inferential testing.
6. Write the reproduction guide, artifact bundle instructions, and failure analysis section.

## Working Rule

Do not expand the research scope unless new empirical evidence requires revising the theory or evaluation methodology.
