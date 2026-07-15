# LongMemEval Strong Baseline Evidence Package Manifest

This directory freezes the LongMemEval strong-baseline evidence package for SRP.
It is an evidence artifact, not a calibration artifact and not a theory revision.

## Frozen Contents

- Benchmark: `longmemeval`
- Baselines: `full_context, sliding_window, vector_rag, mem0, graphiti, letta, memmachine, srp`
- Seeds: `11, 23, 37`
- Model: `Qwen/Qwen3-4B-AWQ`
- Tokenizer: `Qwen/Qwen3-4B-AWQ`
- Prompt template: `longmemeval_shared_generation_prompt_v1`
- Endpoint: `http://172.25.253.78:8000`
- Runtime manifest: `runtime_manifest.json`
- Evidence report: `longmemeval_evidence_report.md`
- Statistical summary: `longmemeval_evidence_statistical_summary.json`
- Records: `longmemeval_evidence_records.jsonl`
- CSV export: `longmemeval_evidence_records.csv`
- Trace inventory: `longmemeval_evidence_generation_traces.json`
- Scorer alignment closure: `longmemeval_scorer_alignment_closure.md`
- Evidence promotion decision: `SRP_LONGMEMEVAL_EVIDENCE_PROMOTION_DECISION.md`

## Intended Use

This package is intended for paper-facing evidence review under the frozen runtime contract.
It supports descriptive statistics, scorer auditing, and baseline comparison under the same shared generation backend.

## Boundary

Promotion is now a paper decision under the frozen audit specification and frozen runtime contract.
