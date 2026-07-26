from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .evaluator import BackendComparisonReport


@dataclass(frozen=True)
class SemanticBackendComparisonMarkdownReport:
    report: BackendComparisonReport
    config: dict[str, Any]

    def render(self) -> str:
        lines: list[str] = []
        lines.append("# SRP Semantic Backend Comparison Report")
        lines.append("")
        lines.append("This report freezes the semantic evidence backend comparison for SRP.")
        lines.append("It is a comparison report, not a calibration artifact and not an optimization artifact.")
        lines.append("")
        lines.append("## 1. Purpose")
        lines.append("")
        lines.append(
            "This study evaluates whether a local semantic evidence backend improves SRP verification quality "
            "without acquiring runtime authority."
        )
        lines.append("")
        lines.append("It answers:")
        lines.append("")
        lines.append("> When should SRP escalate from vector evidence to local-model evidence?")
        lines.append("")
        lines.append("It does not introduce optimization, runtime mutation, or adaptive learning.")
        lines.append("")
        lines.append("## 2. Evaluation Boundary")
        lines.append("")
        lines.append("- Runtime is fixed")
        lines.append("- Optimization parameters are fixed")
        lines.append("- Candidate set is fixed")
        lines.append("- Only the evidence backend changes")
        lines.append("")
        lines.append("The local model is treated as an evidence provider, not a controller.")
        lines.append("")
        lines.append("## 3. Compared Backends")
        lines.append("")
        lines.append(f"- Baseline backend: `{self.report.baseline_backend}`")
        lines.append(f"- Variant backend: `{self.report.variant_backend}`")
        baseline_modes = sorted({record.vector_outcome.mode for record in self.report.records})
        variant_modes = sorted({record.variant_outcome.mode for record in self.report.records})
        lines.append(f"- Baseline mode(s): `{', '.join(baseline_modes)}`")
        lines.append(f"- Variant mode(s): `{', '.join(variant_modes)}`")
        lines.append("")
        lines.append("## 4. Experimental Setup")
        lines.append("")
        lines.append("| Setting | Value |")
        lines.append("| --- | --- |")
        lines.append(f"| Comparison cases | `{self.report.summary.get('case_count', 0)}` |")
        lines.append(f"| Mean vector latency | `{self.report.summary.get('mean_vector_latency_seconds', 0.0)}` s |")
        lines.append(f"| Mean variant latency | `{self.report.summary.get('mean_variant_latency_seconds', 0.0)}` s |")
        lines.append(f"| Vector accuracy | `{self.report.summary.get('vector_accuracy', 0.0)}` |")
        lines.append(f"| Variant accuracy | `{self.report.summary.get('variant_accuracy', 0.0)}` |")
        lines.append(f"| Vector repeat stability | `{self.report.summary.get('vector_repeat_stability_rate', 0.0)}` |")
        lines.append(f"| Variant repeat stability | `{self.report.summary.get('variant_repeat_stability_rate', 0.0)}` |")
        lines.append(f"| Review rate | `{self.report.summary.get('review_rate', 0.0)}` |")
        lines.append("")
        lines.append("## 5. Boundary Agreement Results")
        lines.append("")
        lines.append(f"- Agreement rate: `{self.report.summary.get('agreement_rate', 0.0)}`")
        lines.append(f"- Disagreement count: `{self.report.summary.get('disagreement_count', 0)}`")
        lines.append(f"- Escalated cases: `{self.report.summary.get('escalated_case_count', 0)}`")
        lines.append(f"- Authority violation cases: `{self.report.summary.get('authority_violation_case_count', 0)}`")
        lines.append("")
        lines.append("| Case | Category | Vector | Variant | Final | Expected |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for record in self.report.records:
            lines.append(
                f"| `{record.case.case_id}` | `{record.case.category}` | `{record.vector_outcome.decision}` | "
                f"`{record.variant_outcome.decision}` | `{record.final_decision}` | "
                f"`{'accept' if record.expected_verdict else 'reject'}` |"
            )
        lines.append("")
        lines.append("## 6. Verification Quality")
        lines.append("")
        lines.append(f"- Vector false acceptance: `{self.report.summary.get('vector_false_acceptance', 0)}`")
        lines.append(f"- Vector false rejection: `{self.report.summary.get('vector_false_rejection', 0)}`")
        lines.append(f"- Variant false acceptance: `{self.report.summary.get('variant_false_acceptance', 0)}`")
        lines.append(f"- Variant false rejection: `{self.report.summary.get('variant_false_rejection', 0)}`")
        lines.append(f"- Authority violation final accept rate: `{self.report.summary.get('authority_violation_final_accept_rate', 0.0)}`")
        lines.append("")
        lines.append("## 7. Escalation Routing")
        lines.append("")
        lines.append(f"- Boundary case review count: `{self.report.summary.get('boundary_review_count', 0)}`")
        lines.append(f"- Variant local-model count: `{self.report.summary.get('variant_local_model_count', 0)}`")
        lines.append(f"- Variant offline-heuristic count: `{self.report.summary.get('variant_offline_heuristic_count', 0)}`")
        lines.append(f"- Variant fallback count: `{self.report.summary.get('variant_fallback_count', 0)}`")
        lines.append("")
        lines.append("## 8. Cost Tradeoff")
        lines.append("")
        lines.append(
            "The local evidence backend adds overhead relative to the vector baseline, but it can provide additional "
            "semantic evidence when the vector signal is ambiguous."
        )
        lines.append("")
        lines.append("## 9. Authority Preservation")
        lines.append("")
        lines.append("- `Runtime` executes")
        lines.append("- `Evidence` provides verification signals")
        lines.append("- `Governance` decides")
        lines.append("- The local model does not mutate state")
        lines.append("- The local model does not approve deployment")
        lines.append("")
        lines.append("## 10. Limitations")
        lines.append("")
        lines.append("- The comparison uses a small fixed case set")
        lines.append("- The variant backend may run in offline fallback mode if the local endpoint is unavailable")
        lines.append("- The study does not claim universal superiority of local-model evidence")
        lines.append("")
        lines.append("## 11. Future Extension")
        lines.append("")
        lines.append("The next useful step is to characterize boundary escalation policy:")
        lines.append("")
        lines.append("- when vector evidence is sufficient")
        lines.append("- when local evidence should be consulted")
        lines.append("- how evidence disagreement should be routed to governance")
        lines.append("")
        lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
