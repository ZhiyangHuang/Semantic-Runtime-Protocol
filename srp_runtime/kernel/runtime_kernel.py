from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.constraints.constraint_engine import ConstraintEngine, ConstraintResult
from srp_runtime.event.runtime_event import EventResult, RuntimeEvent
from srp_runtime.decision import DecisionContext, DecisionResult
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.kernel.runtime_services import RuntimeKernelConfig, RuntimeServices
from srp_runtime.metric.semantic_metric import MetricResult, SemanticMetric
from srp_runtime.operators.approximation import ApproximationOperator
from srp_runtime.operators.activation import ActivationUpdateOperator
from srp_runtime.operators.forgetting import ForgettingOperator
from srp_runtime.operators.garbage_collection import GarbageCollectionOperator
from srp_runtime.operators.identity import IdentityUpdateOperator
from srp_runtime.operators.merge import MergeOperator
from srp_runtime.operators.recovery import RecoveryOperator
from srp_runtime.operators.relation import RelationUpdateOperator
from srp_runtime.operators.split import SplitOperator
from srp_runtime.semantic.state import SemanticState, SemanticStateView
from srp_runtime.semantic.unit import SemanticUnit
from srp_runtime.trace.trace_builder import TraceBuilder, TraceRecord


@dataclass
class ValidationResult:
    event_id: str
    accepted: bool
    violations: list[str] = field(default_factory=list)
    checked_constraints: list[str] = field(default_factory=list)


class RuntimeKernel:
    def __init__(
        self,
        state: SemanticState | None = None,
        constraint_engine: ConstraintEngine | None = None,
        metric: SemanticMetric | None = None,
        trace_builder: TraceBuilder | None = None,
        services: RuntimeServices | None = None,
        config: RuntimeKernelConfig | None = None,
    ) -> None:
        self._state = state or SemanticState(state_id="default")
        self._constraint_engine = constraint_engine or ConstraintEngine()
        self._metric = metric or SemanticMetric()
        self._trace_builder = trace_builder or TraceBuilder()
        self._services = services or RuntimeServices()
        self._config = config or RuntimeKernelConfig()
        self._identity_operator = IdentityUpdateOperator()
        self._activation_operator = ActivationUpdateOperator()
        self._merge_operator = MergeOperator()
        self._approximation_operator = ApproximationOperator()
        self._split_operator = SplitOperator()
        self._recovery_operator = RecoveryOperator()
        self._forgetting_operator = ForgettingOperator()
        self._gc_operator = GarbageCollectionOperator()
        self._relation_operator = RelationUpdateOperator()
        self._event_stream: list[RuntimeEvent] = []
        self._trace_records: list[TraceRecord] = []
        self._decision_results: list[DecisionResult] = []
        self._commits: list[object] = []
        self._checkpoints: list[object] = []

    def submit_event(self, event: RuntimeEvent) -> EventResult:
        validation = self.validate_event(event)
        if not validation.accepted:
            return EventResult(
                event_id=event.event_id,
                status="rejected",
                reason="; ".join(validation.violations) if validation.violations else None,
            )

        transition = self.apply_event(event)
        return EventResult(
            event_id=event.event_id,
            status="applied" if transition.success else "failed",
            affected_units=transition.changed_unit_ids,
            reason=transition.failure_reason,
        )

    def validate_event(self, event: RuntimeEvent) -> ValidationResult:
        result: ConstraintResult = self._constraint_engine.validate(self._state, event)
        return ValidationResult(
            event_id=event.event_id,
            accepted=result.accepted,
            violations=list(result.violations),
            checked_constraints=list(result.checked_constraints),
        )

    def apply_event(self, event: RuntimeEvent) -> TransitionResult:
        decision_result = self._select_decision_result(event)
        effective_event = self._apply_decision_to_event(event, decision_result)
        if decision_result is not None and not decision_result.success:
            before_state_ref = self._state.state_ref()
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name=event.operator_name or "unresolved",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": event.operator_name or "unresolved",
                    "event_type": event.event_type,
                    "decision_id": decision_result.decision_id,
                    "decision_explanation": decision_result.explanation,
                },
                invariant_checks=[],
                metric_evidence_ref=None,
                metric_evidence=None,
                success=False,
                failure_reason=decision_result.explanation or "decision boundary rejected the event",
                timestamp_round=self._state.timestamp_round,
            )

        validation = self.validate_event(effective_event)
        operator = self._select_operator(effective_event)
        operator_name = effective_event.operator_name or operator.__class__.__name__
        before_state_ref = self._state.state_ref()
        metric_result = self._build_metric_evidence(effective_event)
        metric_evidence_ref = None if metric_result is None else f"metric:{event.event_id}"
        if not validation.accepted:
            return TransitionResult(
                transition_id=f"tr:{event.event_id}",
                event_id=event.event_id,
                operator_name=operator_name,
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changed_unit_ids=[],
                changed_relation_ids=[],
                mutation_summary={
                    "operator": operator_name,
                    "event_type": event.event_type,
                },
                invariant_checks=list(validation.checked_constraints),
                metric_evidence_ref=metric_evidence_ref,
                metric_evidence=None if metric_result is None else self._metric_result_to_dict(metric_result),
                success=False,
                failure_reason="; ".join(validation.violations) if validation.violations else None,
                timestamp_round=self._state.timestamp_round,
            )
        transition = operator.apply(self._state, effective_event)
        self._state.version_id = event.event_id
        self._state.timestamp_round += 1
        self._event_stream.append(effective_event)
        transition.before_state_ref = before_state_ref
        transition.after_state_ref = self._state.state_ref()
        transition.timestamp_round = self._state.timestamp_round
        transition.success = True
        transition.failure_reason = None
        transition.operator_name = operator_name
        transition.mutation_summary.setdefault("event_type", event.event_type)
        transition.metric_evidence_ref = metric_evidence_ref
        transition.metric_evidence = None if metric_result is None else self._metric_result_to_dict(metric_result)
        if metric_result is not None:
            transition.mutation_summary.setdefault("metric_score", metric_result.total_distance)
            transition.mutation_summary.setdefault("metric_explanation", metric_result.explanation)
        trace = self._trace_builder.record_transition(effective_event, transition)
        self._trace_records.append(trace)
        self._maybe_commit_and_checkpoint(effective_event, transition, trace, decision_result)
        return transition

    def get_state(self) -> SemanticStateView:
        return SemanticStateView(
            state_id=self._state.state_id,
            version_id=self._state.version_id,
            timestamp_round=self._state.timestamp_round,
            unit_ids=list(self._state.units.keys()),
        )

    def _select_operator(self, event: RuntimeEvent):
        operator_name = self._normalize_operator_name(event.operator_name)
        if operator_name == "activationupdateoperator":
            return self._activation_operator
        if operator_name == "mergeoperator":
            return self._merge_operator
        if operator_name == "approximationoperator":
            return self._approximation_operator
        if operator_name == "splitoperator":
            return self._split_operator
        if operator_name == "recoveryoperator":
            return self._recovery_operator
        if operator_name == "forgettingoperator":
            return self._forgetting_operator
        if operator_name == "garbagecollectionoperator" or operator_name.startswith("gc"):
            return self._gc_operator
        if operator_name == "relationupdateoperator":
            return self._relation_operator
        if operator_name == "identityupdateoperator":
            return self._identity_operator

        event_type = event.event_type.lower()
        if "merge" in event_type:
            return self._merge_operator
        if "approx" in event_type:
            return self._approximation_operator
        if "split" in event_type:
            return self._split_operator
        if "recover" in event_type:
            return self._recovery_operator
        if "forget" in event_type:
            return self._forgetting_operator
        if "garbage" in event_type or event_type.startswith("gc"):
            return self._gc_operator
        if "activation" in event_type:
            return self._activation_operator
        if "relation" in event_type:
            return self._relation_operator
        return self._identity_operator

    def _select_decision_result(self, event: RuntimeEvent) -> DecisionResult | None:
        if not self._config.enable_decision_layer or self._services.decision_engine is None:
            return None
        context = DecisionContext(
            event_ref=event.event_id,
            state_ref=self._state.state_ref(),
            available_operators=self._available_operator_names(),
            constraint_context={
                "operator_name": event.operator_name,
                "constraint_evidence_refs": [],
                "metric_evidence_refs": [],
            },
            semantic_time=self._state.timestamp_round,
            version_id=self._state.version_id,
            lifecycle_state="active",
            metric_snapshot_ref=None,
        )
        decision_result = self._services.decision_engine.select_operator(context, event=event)
        self._decision_results.append(decision_result)
        return decision_result

    def _apply_decision_to_event(
        self,
        event: RuntimeEvent,
        decision_result: DecisionResult | None,
    ) -> RuntimeEvent:
        selected_operator = None
        if decision_result is not None:
            selected_operator = decision_result.selected_operator
            if selected_operator is None and not decision_result.success:
                return event
        if selected_operator is None:
            return event
        if event.operator_name == selected_operator:
            return event
        return RuntimeEvent(
            event_id=event.event_id,
            event_type=event.event_type,
            schema_version=event.schema_version,
            causal_parent=event.causal_parent,
            actor=event.actor,
            targets=list(event.targets),
            payload=dict(event.payload),
            mutation_mode=event.mutation_mode,
            operator_name=selected_operator,
            confidence=event.confidence,
        )

    def _maybe_commit_and_checkpoint(
        self,
        event: RuntimeEvent,
        transition: TransitionResult,
        trace: TraceRecord,
        decision_result: DecisionResult | None,
    ) -> None:
        if not transition.success:
            return

        if self._config.enable_commit_layer and self._services.commit_manager is not None and decision_result is not None:
            commit = self._services.commit_manager.commit_transition(transition, trace, decision_result)
            self._commits.append(commit)

            if self._config.enable_checkpoint_layer and self._services.checkpoint_manager is not None:
                checkpoint = self._services.checkpoint_manager.create_checkpoint(
                    commit,
                    state_ref=transition.after_state_ref,
                    event_position=len(self._event_stream),
                )
                self._checkpoints.append(checkpoint)

    def _available_operator_names(self) -> list[str]:
        return [
            "IdentityUpdate",
            "ActivationUpdate",
            "Merge",
            "Approximation",
            "Split",
            "Recovery",
            "Forgetting",
            "GarbageCollection",
            "RelationUpdate",
        ]

    def _normalize_operator_name(self, operator_name: str | None) -> str:
        if operator_name is None:
            return ""
        normalized = str(operator_name).strip().lower()
        aliases = {
            "identityupdate": "identityupdateoperator",
            "activationupdate": "activationupdateoperator",
            "merge": "mergeoperator",
            "approximation": "approximationoperator",
            "split": "splitoperator",
            "recovery": "recoveryoperator",
            "forgetting": "forgettingoperator",
            "garbagecollection": "garbagecollectionoperator",
            "gc": "garbagecollectionoperator",
            "relationupdate": "relationupdateoperator",
        }
        return aliases.get(normalized, normalized)

    def _build_metric_evidence(self, event: RuntimeEvent) -> MetricResult | None:
        if not event.targets:
            return None

        source_unit = self._state.units.get(event.targets[0])
        target_unit = self._select_metric_peer(event, source_unit)
        if source_unit is None or target_unit is None:
            return None
        return self._metric.distance(
            source_unit,
            target_unit,
            graph=self._state.graph,
            current_round=self._state.timestamp_round,
        )

    def _select_metric_peer(
        self,
        event: RuntimeEvent,
        source_unit: SemanticUnit | None,
    ) -> SemanticUnit | None:
        if source_unit is None:
            return None

        if len(event.targets) >= 2:
            peer_id = event.targets[1]
            return self._state.units.get(peer_id)

        approximation_peer_id = (
            event.payload.get("approximation_target_id")
            or event.payload.get("representative_unit_id")
        )
        if approximation_peer_id is not None:
            approximation_peer_id = str(approximation_peer_id)
            if approximation_peer_id in self._state.units:
                return self._state.units.get(approximation_peer_id)

        sorted_unit_ids = sorted(unit_id for unit_id in self._state.units.keys() if unit_id != source_unit.unit_id)
        if sorted_unit_ids:
            return self._state.units.get(sorted_unit_ids[0])
        return source_unit

    def _metric_result_to_dict(self, result: MetricResult) -> dict[str, object]:
        return {
            "source_id": result.source_id,
            "target_id": result.target_id,
            "total_distance": result.total_distance,
            "component_scores": dict(result.component_scores),
            "comparable": result.comparable,
            "explanation": result.explanation,
        }

    @property
    def event_stream(self) -> list[RuntimeEvent]:
        return list(self._event_stream)

    @property
    def trace_records(self) -> list[TraceRecord]:
        return list(self._trace_records)

    @property
    def decision_results(self) -> list[DecisionResult]:
        return list(self._decision_results)

    @property
    def commits(self) -> list[object]:
        return list(self._commits)

    @property
    def checkpoints(self) -> list[object]:
        return list(self._checkpoints)
