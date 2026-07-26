from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.semantic.state import SemanticState


@dataclass
class ConstraintResult:
    accepted: bool
    violations: list[str] = field(default_factory=list)
    checked_constraints: list[str] = field(default_factory=list)


class ConstraintEngine:
    def validate(self, state: SemanticState, event: RuntimeEvent) -> ConstraintResult:
        checked_constraints: list[str] = []
        violations: list[str] = []

        checked_constraints.append("runtime.schema_version.present")
        if not str(event.schema_version).strip():
            violations.append("schema_version must be present")

        checked_constraints.append("runtime.mutation_mode.present")
        if not str(event.mutation_mode).strip():
            violations.append("mutation_mode must be present")

        checked_constraints.append("runtime.operator.resolved")
        resolved_operator = self._resolve_operator_name(event)
        if resolved_operator is None:
            violations.append("operator could not be resolved")

        checked_constraints.append("identity.targets.present")
        if not event.targets:
            violations.append("event requires at least one target")

        checked_constraints.append("identity.targets.unique")
        if len(event.targets) != len(set(event.targets)):
            violations.append("event targets must be unique")

        creation_event = event.event_type in {"SemanticExtracted", "IdentityCreated", "UnitCreated"}
        checked_constraints.append("identity.targets.exist")
        if not creation_event:
            missing_targets = [target for target in event.targets if target not in state.units]
            if missing_targets:
                violations.append(f"missing target units: {', '.join(missing_targets)}")

        checked_constraints.append("identity.unit_id.immutable")
        if "unit_id" in event.payload and event.targets:
            declared_unit_id = str(event.payload["unit_id"])
            if declared_unit_id != event.targets[0]:
                violations.append("unit_id cannot change during an update")

        checked_constraints.append("semantic.canonical_name.present")
        if event.event_type in {"SemanticExtracted", "IdentityCreated", "UnitCreated"}:
            canonical_name = str(event.payload.get("canonical_name", "")).strip()
            if not canonical_name:
                violations.append("canonical_name is required for creation events")

        checked_constraints.append("structural.relation.endpoints")
        if resolved_operator == "relation":
            if len(event.targets) < 2:
                violations.append("relation updates require at least two targets")
            else:
                for target in event.targets:
                    if target not in state.units:
                        violations.append(f"relation endpoint missing: {target}")

        checked_constraints.append("identity.merge.targets")
        if resolved_operator == "merge":
            if len(event.targets) < 2:
                violations.append("merge requires at least two source units")

        checked_constraints.append("evolution.activation.delta")
        if resolved_operator == "activation":
            if "activation" in event.payload:
                activation_value = float(event.payload["activation"])
                if not 0.0 <= activation_value <= 1.0:
                    violations.append("activation must be within [0, 1]")
            if "activation_delta" in event.payload and float(event.payload["activation_delta"]) == 0.0:
                violations.append("activation_delta must be non-zero")

        checked_constraints.append("evolution.lifecycle.transition")
        lifecycle_state = event.payload.get("lifecycle_state")
        if lifecycle_state is not None and event.targets:
            current = state.units.get(event.targets[0])
            current_state = current.lifecycle_state if current is not None else None
            target_state = str(lifecycle_state)
            if current_state == "forgotten" and target_state == "active":
                if event.event_type not in {"Recovered", "RecoveryApplied", "RecoveryValidated"}:
                    violations.append("forgotten units require recovery before becoming active")

        checked_constraints.append("runtime.operator.binds")
        operator_name = event.operator_name or self._resolve_operator_name(event)
        if operator_name is None:
            violations.append("operator name must be present or derivable")

        checked_constraints.append("identity.merge.compatibility")
        if resolved_operator == "merge" and len(event.targets) >= 2:
            entity_types: list[str] = []
            for target in event.targets:
                unit = state.units.get(target)
                if unit is None:
                    continue
                entity_type = unit.semantic_payload.get("entity_type")
                if entity_type is not None:
                    entity_types.append(str(entity_type))
            if entity_types and len(set(entity_types)) > 1:
                violations.append("merge requires matching entity_type across source units")

            merged_unit_id = event.payload.get("merged_unit_id") or event.payload.get("target_unit_id")
            if merged_unit_id is not None:
                merged_unit_id = str(merged_unit_id)
                if merged_unit_id in state.units and merged_unit_id not in event.targets:
                    violations.append("merged_unit_id must be new or alias an existing source unit")

        checked_constraints.append("identity.split.targets")
        if resolved_operator == "split":
            source_unit_id = event.payload.get("source_unit_id") or (event.targets[0] if event.targets else None)
            if source_unit_id is None:
                violations.append("split requires a source_unit_id")
            elif str(source_unit_id) not in state.units:
                violations.append("split source unit must exist")

            split_ids = self._resolve_split_unit_ids(event)
            if not split_ids:
                violations.append("split requires generated units")
            elif len(split_ids) != len(set(split_ids)):
                violations.append("split generated units must be unique")

            if source_unit_id is not None:
                source_unit = state.units.get(str(source_unit_id))
                if source_unit is not None and not source_unit.lineage and source_unit.lifecycle_state not in {"merged", "approximated"}:
                    violations.append("split requires lineage or a split-capable source unit")

            existing_conflicts: list[str] = []
            if source_unit is not None:
                for unit_id in split_ids:
                    if unit_id == source_unit.unit_id:
                        existing_conflicts.append(unit_id)
                        continue
                    if unit_id in state.units and unit_id not in source_unit.lineage:
                        existing_conflicts.append(unit_id)
            else:
                existing_conflicts = [unit_id for unit_id in split_ids if unit_id in state.units and unit_id != str(source_unit_id)]
            if existing_conflicts:
                violations.append(f"split generated units must be new: {', '.join(existing_conflicts)}")

        checked_constraints.append("identity.approximation.targets")
        if resolved_operator == "approximation":
            if not event.targets:
                violations.append("approximation requires at least one target")

            threshold = event.payload.get("activation_threshold")
            if threshold is None:
                violations.append("approximation requires activation_threshold")
            else:
                try:
                    threshold_value = float(threshold)
                    if threshold_value < 0.0:
                        violations.append("activation_threshold must be non-negative")
                except (TypeError, ValueError):
                    violations.append("activation_threshold must be numeric")

            representative_id = event.payload.get("approximation_target_id") or event.payload.get("representative_unit_id")
            if representative_id is not None:
                representative_id = str(representative_id)
                if representative_id not in state.units:
                    violations.append("approximation representative unit must exist")

        checked_constraints.append("recovery.evidence.targets")
        if resolved_operator == "recovery":
            if not event.targets:
                violations.append("recovery requires at least one target")

            target_unit_id = event.payload.get("target_unit_id") or (event.targets[0] if event.targets else None)
            if target_unit_id is None:
                violations.append("recovery requires a target_unit_id")
            elif str(target_unit_id) not in state.units:
                violations.append("recovery target unit must exist")

            evidence_refs = list(event.payload.get("evidence_refs", []))
            if not evidence_refs:
                violations.append("recovery requires evidence_refs")

            recovery_source = event.payload.get("recovery_source")
            if not str(recovery_source or "").strip():
                violations.append("recovery_source must be present")

            recovery_mode = event.payload.get("recovery_mode")
            if not str(recovery_mode or "").strip():
                violations.append("recovery_mode must be present")

            if target_unit_id is not None:
                target_unit = state.units.get(str(target_unit_id))
                if target_unit is not None and target_unit.lifecycle_state not in {"approximated", "archived", "forgotten", "merged"}:
                    violations.append("recovery target must be approximated, archived, forgotten, or merged")

            restored_fields_present = any(
                event.payload.get(key) is not None
                for key in (
                    "restored_canonical_name",
                    "restored_aliases",
                    "restored_lineage",
                    "restored_provenance",
                    "restored_semantic_payload",
                    "restored_relation_ids",
                    "restored_neighbors",
                    "restored_activation",
                    "restored_confidence",
                    "restored_drift_score",
                    "restored_lifecycle_state",
                )
            )
            if not restored_fields_present:
                violations.append("recovery requires restored fields")

        checked_constraints.append("forgetting.evidence.targets")
        if resolved_operator == "forgetting":
            if not event.targets and not event.payload.get("target_unit_ids") and event.payload.get("target_unit_id") is None:
                violations.append("forgetting requires at least one target")

            preserve_evidence = bool(event.payload.get("preserve_evidence", True))
            if not preserve_evidence:
                violations.append("forgetting requires preserve_evidence=true")

            evidence_refs = list(event.payload.get("evidence_refs", []))
            if preserve_evidence and not evidence_refs:
                violations.append("forgetting requires evidence_refs")

            target_ids = list(event.payload.get("target_unit_ids", [])) or list(event.targets)
            if not target_ids and event.payload.get("target_unit_id") is not None:
                target_ids = [str(event.payload.get("target_unit_id"))]
            for target_id in target_ids:
                unit = state.units.get(str(target_id))
                if unit is None:
                    continue
                if bool(unit.semantic_payload.get("identity_anchor")):
                    violations.append(f"forgetting cannot target identity anchor: {target_id}")
                entity_type = str(unit.semantic_payload.get("entity_type", "")).lower()
                if entity_type in {"user_id", "entity_id", "system_invariant", "identity_anchor"}:
                    violations.append(f"forgetting cannot target protected identity type: {target_id}")

        checked_constraints.append("gc.replay.identity.targets")
        if resolved_operator == "garbage_collection":
            if not event.targets and not event.payload.get("target_unit_ids") and event.payload.get("target_unit_id") is None:
                violations.append("garbage collection requires at least one target")

            retention_policy = str(event.payload.get("retention_policy", "")).strip()
            if not retention_policy:
                violations.append("garbage collection requires retention_policy")

            gc_mode = str(event.payload.get("gc_mode", "")).strip()
            if not gc_mode:
                violations.append("garbage collection requires gc_mode")

            evidence_refs = list(event.payload.get("evidence_refs", []))
            if not evidence_refs:
                violations.append("garbage collection requires evidence_refs")

            target_ids = list(event.payload.get("target_unit_ids", [])) or list(event.targets)
            if not target_ids and event.payload.get("target_unit_id") is not None:
                target_ids = [str(event.payload.get("target_unit_id"))]
            for target_id in target_ids:
                unit = state.units.get(str(target_id))
                if unit is None:
                    continue
                if bool(unit.semantic_payload.get("identity_anchor")):
                    violations.append(f"garbage collection cannot target identity anchor: {target_id}")
                entity_type = str(unit.semantic_payload.get("entity_type", "")).lower()
                if entity_type in {"user_id", "entity_id", "system_invariant", "identity_anchor"}:
                    violations.append(f"garbage collection cannot target protected identity type: {target_id}")
                if unit.lifecycle_state not in {"forgotten", "archived"}:
                    violations.append(f"garbage collection requires forgotten or archived targets: {target_id}")

        return ConstraintResult(
            accepted=not violations,
            violations=violations,
            checked_constraints=checked_constraints,
        )

    def _resolve_operator_name(self, event: RuntimeEvent) -> str | None:
        if event.operator_name:
            lowered = event.operator_name.lower()
            if "activation" in lowered:
                return "activation"
            if "merge" in lowered:
                return "merge"
            if "split" in lowered:
                return "split"
            if "approx" in lowered:
                return "approximation"
            if "recover" in lowered:
                return "recovery"
            if "forget" in lowered:
                return "forgetting"
            if "garbage" in lowered or lowered.startswith("gc"):
                return "garbage_collection"
            if "relation" in lowered:
                return "relation"
            if "identity" in lowered:
                return "identity"
            return None

        lowered_event_type = event.event_type.lower()
        if "activation" in lowered_event_type:
            return "activation"
        if "merge" in lowered_event_type:
            return "merge"
        if "split" in lowered_event_type:
            return "split"
        if "approx" in lowered_event_type:
            return "approximation"
        if "recover" in lowered_event_type:
            return "recovery"
        if "forget" in lowered_event_type:
            return "forgetting"
        if "garbage" in lowered_event_type or lowered_event_type.startswith("gc"):
            return "garbage_collection"
        if "relation" in lowered_event_type:
            return "relation"
        if "identity" in lowered_event_type:
            return "identity"
        if lowered_event_type in {"semanticextracted", "unitcreated"}:
            return "identity"
        return None

    def _resolve_split_unit_ids(self, event: RuntimeEvent) -> list[str]:
        for key in ("generated_unit_ids", "target_units", "target_lineages", "split_targets"):
            value = event.payload.get(key)
            if value:
                return [str(item) for item in value]
        return []
