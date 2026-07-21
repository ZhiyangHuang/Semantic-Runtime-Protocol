# Experiment Pipeline Audit

Date: 2026-07-20

Scope: repository audit only. No benchmark code was modified.

## Audit Summary

The repository currently contains a real LongMemEval validation pipeline and transition-role coverage artifacts, but it does not contain standalone MMLU, ARC, or HumanEval benchmark runners/results. Those three benchmarks are therefore blocked at the audit stage.

## Inventory

| Benchmark | Existing Code | Dataset | Runner | Metrics | Results | Status |
| --- | --- | --- | --- | --- | --- | --- |
| MMLU | missing | missing | missing | missing | missing | blocked |
| ARC | missing | missing | missing | missing | missing | blocked |
| HumanEval | missing | missing | missing | missing | missing | blocked |
| LongMemEval | partial | external registry only, payload not stored in repo | `experiments/evaluation/run_longmemeval_*.py`, `experiments/real_world_validation/longmemeval/runner.py` | `answer_accuracy`, `semantic_coverage`, `semantic_drift`, `fact_accuracy`, `relation_accuracy`, `recovery_accuracy`, `closure_accuracy`, `hallucinated_relation_rate`, `evidence_cost` | `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/` | complete |

## Evidence Notes

- `data/external/README.md` states the directory is a registry, not a dataset mirror.
- `data/external/*/manifest.json` files state that benchmark payloads are not stored in the repository.
- `experiments/results/external_validation_longmemeval_reality_check_smoke_v2/longmemeval_reality_check_report.md` is the only standalone benchmark report artifact found for the current release surface.
- `experiments/results/transition_role/coverage/role_coverage_report.md` is a protocol coverage artifact, not a benchmark result page.

## Audit Conclusion

The repository is not yet in a state where a full MMLU / ARC / HumanEval evidence completion pass can proceed safely.
The next required step is to design or locate the missing benchmark-specific runners and data access paths before any implementation work begins.
