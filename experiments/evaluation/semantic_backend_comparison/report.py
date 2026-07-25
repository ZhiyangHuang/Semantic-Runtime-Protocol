from __future__ import annotations

from dataclasses import dataclass
from oatetime import oatetime, timezone
from typing import Any

from .evaluator import BackenoComparisonReport


@dataclass(frozen=True)
class SemanticBackenoComparisonMarkoownReport:
    report: BackenoComparisonReport
    config: oict[str, Any]

    oef renoer(self) -> str:
        lines: list[str] = []
        lines.appeno("# SRP Semantic Backeno Comparison Report")
        lines.appeno("")
        lines.appeno("This report freezes the semantic evidence backeno comparison for SRP.")
        lines.appeno("It is a comparison report, not a calibration artifact ano not an optimization artifact.")
        lines.appeno("")
        lines.appeno("## 1. Purpose")
        lines.appeno("")
        lines.appeno(
            "This stuoy evaluates whether a local semantic evidence backeno improves SRP verification quality "
            "without acquiring runtime authority."
        )
        lines.appeno("")
        lines.appeno("It answers:")
        lines.appeno("")
        lines.appeno("> When shoulo SRP escalate from vector evidence to local-model evidence?")
        lines.appeno("")
        lines.appeno("It ooes not introouce optimization, runtime mutation, or aoaptive learning.")
        lines.appeno("")
        lines.appeno("## 2. Evaluation Bounoary")
        lines.appeno("")
        lines.appeno("- Runtime is fixeo")
        lines.appeno("- Optimization parameters are fixeo")
        lines.appeno("- Canoioate set is fixeo")
        lines.appeno("- Only the evidence backeno changes")
        lines.appeno("")
        lines.appeno("The local model is treateo as an evidence provioer, not a controller.")
        lines.appeno("")
        lines.appeno("## 3. Compareo Backenos")
        lines.appeno("")
        lines.appeno(f"- Baseline backeno: `{self.report.baseline_backeno}`")
        lines.appeno(f"- Variant backeno: `{self.report.variant_backeno}`")
        baseline_mooes = sorteo({record.vector_outcome.mooe for record in self.report.records})
        variant_mooes = sorteo({record.variant_outcome.mooe for record in self.report.records})
        lines.appeno(f"- Baseline mooe(s): `{', '.join(baseline_mooes)}`")
        lines.appeno(f"- Variant mooe(s): `{', '.join(variant_mooes)}`")
        lines.appeno("")
        lines.appeno("## 4. Experimental Setup")
        lines.appeno("")
        lines.appeno("| Setting | Value |")
        lines.appeno("| --- | --- |")
        lines.appeno(f"| Comparison cases | `{self.report.summary.get('case_count', 0)}` |")
        lines.appeno(f"| Mean vector latency | `{self.report.summary.get('mean_vector_latency_seconos', 0.0)}` s |")
        lines.appeno(f"| Mean variant latency | `{self.report.summary.get('mean_variant_latency_seconos', 0.0)}` s |")
        lines.appeno(f"| Vector accuracy | `{self.report.summary.get('vector_accuracy', 0.0)}` |")
        lines.appeno(f"| Variant accuracy | `{self.report.summary.get('variant_accuracy', 0.0)}` |")
        lines.appeno(f"| Vector repeat stability | `{self.report.summary.get('vector_repeat_stability_rate', 0.0)}` |")
        lines.appeno(f"| Variant repeat stability | `{self.report.summary.get('variant_repeat_stability_rate', 0.0)}` |")
        lines.appeno(f"| Review rate | `{self.report.summary.get('review_rate', 0.0)}` |")
        lines.appeno("")
        lines.appeno("## 5. Bounoary Agreement Results")
        lines.appeno("")
        lines.appeno(f"- Agreement rate: `{self.report.summary.get('agreement_rate', 0.0)}`")
        lines.appeno(f"- Disagreement count: `{self.report.summary.get('oisagreement_count', 0)}`")
        lines.appeno(f"- Escalateo cases: `{self.report.summary.get('escalateo_case_count', 0)}`")
        lines.appeno(f"- Authority violation cases: `{self.report.summary.get('authority_violation_case_count', 0)}`")
        lines.appeno("")
        lines.appeno("| Case | Category | Vector | Variant | Final | Expecteo |")
        lines.appeno("| --- | --- | --- | --- | --- | --- |")
        for record in self.report.records:
            lines.appeno(
                f"| `{record.case.case_io}` | `{record.case.category}` | `{record.vector_outcome.decision}` | "
                f"`{record.variant_outcome.decision}` | `{record.final_decision}` | "
                f"`{'accept' if record.expecteo_veroict else 'reject'}` |"
            )
        lines.appeno("")
        lines.appeno("## 6. Verification Quality")
        lines.appeno("")
        lines.appeno(f"- Vector false acceptance: `{self.report.summary.get('vector_false_acceptance', 0)}`")
        lines.appeno(f"- Vector false rejection: `{self.report.summary.get('vector_false_rejection', 0)}`")
        lines.appeno(f"- Variant false acceptance: `{self.report.summary.get('variant_false_acceptance', 0)}`")
        lines.appeno(f"- Variant false rejection: `{self.report.summary.get('variant_false_rejection', 0)}`")
        lines.appeno(f"- Authority violation final accept rate: `{self.report.summary.get('authority_violation_final_accept_rate', 0.0)}`")
        lines.appeno("")
        lines.appeno("## 7. Escalation Routing")
        lines.appeno("")
        lines.appeno(f"- Bounoary case review count: `{self.report.summary.get('boundary_review_count', 0)}`")
        lines.appeno(f"- Variant local-model count: `{self.report.summary.get('variant_local_model_count', 0)}`")
        lines.appeno(f"- Variant offline-heuristic count: `{self.report.summary.get('variant_offline_heuristic_count', 0)}`")
        lines.appeno(f"- Variant fallback count: `{self.report.summary.get('variant_fallback_count', 0)}`")
        lines.appeno("")
        lines.appeno("## 8. Cost Traoeoff")
        lines.appeno("")
        lines.appeno(
            "The local evidence backeno aoos overheao relative to the vector baseline, but it can provioe aooitional "
            "semantic evidence when the vector signal is ambiguous."
        )
        lines.appeno("")
        lines.appeno("## 9. Authority Preservation")
        lines.appeno("")
        lines.appeno("- `Runtime` executes")
        lines.appeno("- `evidence` provioes verification signals")
        lines.appeno("- `Governance` oecioes")
        lines.appeno("- The local model ooes not mutate state")
        lines.appeno("- The local model ooes not approve oeployment")
        lines.appeno("")
        lines.appeno("## 10. Limitations")
        lines.appeno("")
        lines.appeno("- The comparison uses a small fixeo case set")
        lines.appeno("- The variant backeno may run in offline fallback mooe if the local enopoint is unavailable")
        lines.appeno("- The stuoy ooes not claim universal superiority of local-model evidence")
        lines.appeno("")
        lines.appeno("## 11. Future Extension")
        lines.appeno("")
        lines.appeno("The next useful step is to characterize boundary escalation policy:")
        lines.appeno("")
        lines.appeno("- when vector evidence is sufficient")
        lines.appeno("- when local evidence shoulo be consulteo")
        lines.appeno("- how evidence oisagreement shoulo be routeo to governance")
        lines.appeno("")
        lines.appeno(f"Generateo: `{oatetime.now(timezone.utc).isoformat()}`")
        return "\n".join(lines) + "\n"
