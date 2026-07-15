from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .context import DecisionContext
from .result import DecisionResult


@dataclass
class DecisionEngine:
    """Milestone 2 operator-selection boundary.

    The first reference implementation remains conservative:
    it performs explicit operator binding, bounded candidate filtering,
    and deterministic ambiguity handling without learning-based ranking.
    """

    def select_operator(self, context: DecisionContext, event=None) -> DecisionResult:
        available = list(context.available_operators)
        constraint_context = context.constraint_context or {}
        constraint_evidence_refs = list(constraint_context.get("constraint_evidence_refs", []))
        metric_evidence_refs = list(constraint_context.get("metric_evidence_refs", []))

        explicit_operator = self._resolve_explicit_operator(context, event)
        if explicit_operator is not None:
            success = self._is_operator_allowed(explicit_operator, available, constraint_context)
            accepted_candidates = [explicit_operator] if success else []
            rejected_candidates = [] if success else [explicit_operator]
            explanation = (
                f"selected explicit operator {explicit_operator}"
                if success
                else f"explicit operator {explicit_operator} is not eligible in the current context"
            )
            return DecisionResult(
                decision_id=self._build_decision_id(context, explicit_operator),
                event_id=context.event_ref,
                selected_operator=explicit_operator if success else None,
                candidate_operators=self._candidate_list(available, explicit_operator, success),
                accepted_candidates=accepted_candidates,
                rejected_candidates=rejected_candidates,
                constraint_evidence_refs=constraint_evidence_refs,
                metric_evidence_refs=metric_evidence_refs,
                explanation=explanation,
                success=success,
                semantic_time=context.semantic_time,
                version_id=context.version_id,
            )

        candidates = self._filter_candidates(available, constraint_context)
        event_candidates = self._derive_event_candidates(event)
        if event_candidates:
            candidates = [candidate for candidate in candidates if candidate in set(event_candidates)]
        if len(candidates) == 1:
            selected_operator = candidates[0]
            return DecisionResult(
                decision_id=self._build_decision_id(context, selected_operator),
                event_id=context.event_ref,
                selected_operator=selected_operator,
                candidate_operators=list(available),
                accepted_candidates=[selected_operator],
                rejected_candidates=[op for op in available if op != selected_operator],
                constraint_evidence_refs=constraint_evidence_refs,
                metric_evidence_refs=metric_evidence_refs,
                explanation=f"selected sole eligible operator {selected_operator}",
                success=True,
                semantic_time=context.semantic_time,
                version_id=context.version_id,
            )

        if len(candidates) == 0:
            return DecisionResult(
                decision_id=self._build_decision_id(context, None),
                event_id=context.event_ref,
                selected_operator=None,
                candidate_operators=list(available),
                accepted_candidates=[],
                rejected_candidates=list(available),
                constraint_evidence_refs=constraint_evidence_refs,
                metric_evidence_refs=metric_evidence_refs,
                explanation="no eligible operator candidates",
                success=False,
                semantic_time=context.semantic_time,
                version_id=context.version_id,
            )

        return DecisionResult(
            decision_id=self._build_decision_id(context, None),
            event_id=context.event_ref,
            selected_operator=None,
            candidate_operators=list(available),
            accepted_candidates=list(candidates),
            rejected_candidates=[op for op in available if op not in candidates],
            constraint_evidence_refs=constraint_evidence_refs,
            metric_evidence_refs=metric_evidence_refs,
            explanation=f"ambiguous operator decision: {', '.join(candidates)}",
            success=False,
            semantic_time=context.semantic_time,
            version_id=context.version_id,
        )

    def _resolve_explicit_operator(self, context: DecisionContext, event) -> str | None:
        for source in (event, context.constraint_context):
            if source is None:
                continue
            operator_name = getattr(source, "operator_name", None)
            if operator_name is None and isinstance(source, dict):
                operator_name = source.get("operator_name") or source.get("selected_operator")
            if operator_name is not None:
                operator_name = str(operator_name).strip()
                if operator_name:
                    return operator_name
        return None

    def _filter_candidates(self, available: list[str], constraint_context: dict[str, object]) -> list[str]:
        allowed = constraint_context.get("allowed_operators")
        rejected = constraint_context.get("rejected_operators", [])
        allowed_set = set(str(operator) for operator in allowed) if allowed is not None else None
        rejected_set = set(str(operator) for operator in rejected)

        candidates: list[str] = []
        for operator_name in available:
            if allowed_set is not None and operator_name not in allowed_set:
                continue
            if operator_name in rejected_set:
                continue
            candidates.append(operator_name)
        return candidates

    def _derive_event_candidates(self, event) -> list[str]:
        if event is None:
            return []
        event_type = str(getattr(event, "event_type", "") or "").lower()
        if "activation" in event_type:
            return ["ActivationUpdate"]
        if "merge" in event_type:
            return ["Merge"]
        if "split" in event_type:
            return ["Split"]
        if "approx" in event_type:
            return ["Approximation"]
        if "recover" in event_type:
            return ["Recovery"]
        if "forget" in event_type:
            return ["Forgetting"]
        if "garbage" in event_type or event_type.startswith("gc"):
            return ["GarbageCollection"]
        if "relation" in event_type:
            return ["RelationUpdate"]
        if "identity" in event_type or event_type in {"semanticextracted", "unitcreated"}:
            return ["IdentityUpdate"]
        return []

    def _is_operator_allowed(
        self,
        operator_name: str,
        available: Iterable[str],
        constraint_context: dict[str, object],
    ) -> bool:
        available_set = set(available)
        if available_set and operator_name not in available_set:
            return False

        allowed = constraint_context.get("allowed_operators")
        if allowed is not None and operator_name not in set(str(operator) for operator in allowed):
            return False

        rejected = constraint_context.get("rejected_operators", [])
        if operator_name in set(str(operator) for operator in rejected):
            return False

        return True

    def _candidate_list(self, available: list[str], selected: str | None, success: bool) -> list[str]:
        if success and selected is not None:
            return [selected]
        return list(available)

    def _build_decision_id(self, context: DecisionContext, selected_operator: str | None) -> str:
        operator_part = selected_operator or "unresolved"
        return f"decision:{context.event_ref}:{operator_part}:{context.semantic_time}"
