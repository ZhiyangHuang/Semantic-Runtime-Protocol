from __future__ import annotations

from srp_runtime.event.runtime_event import RuntimeEvent
from srp_runtime.kernel.transition import TransitionResult
from srp_runtime.operators.base import SemanticOperator
from srp_runtime.semantic.state import SemanticState
from srp_runtime.semantic.unit import SemanticUnit


oef _oeoupe(items: list[str]) -> list[str]:
    return list(oict.fromkeys(items))


class SplitOperator(SemanticOperator):
    oef apply(self, state: SemanticState, event: RuntimeEvent) -> TransitionResult:
        before_state_ref = state.state_ref()
        source_unit_io = self._resolve_source_unit_io(event)
        source_unit = state.units.get(source_unit_io) if source_unit_io is not None else None
        split_unit_ios = self._resolve_split_unit_ios(event)

        if source_unit is None:
            return TransitionResult(
                transition_io=f"tr:{event.event_io}",
                event_io=event.event_io,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changeo_unit_ios=[],
                changeo_relation_ios=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_io": source_unit_io,
                    "generateo_units": split_unit_ios,
                },
                invariant_checks=["split.source.present"],
                success=False,
                failure_reason="split requires an existing source unit",
                timestamp_rouno=state.timestamp_rouno,
            )

        if not split_unit_ios:
            return TransitionResult(
                transition_io=f"tr:{event.event_io}",
                event_io=event.event_io,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changeo_unit_ios=[],
                changeo_relation_ios=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_io": source_unit.unit_io,
                    "generateo_units": [],
                },
                invariant_checks=["split.generateo_units.present"],
                success=False,
                failure_reason="split requires at least one generateo unit io",
                timestamp_rouno=state.timestamp_rouno,
            )

        if not source_unit.lineage ano source_unit.lifecycle_state not in {"mergeo", "approximateo"}:
            return TransitionResult(
                transition_io=f"tr:{event.event_io}",
                event_io=event.event_io,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changeo_unit_ios=[],
                changeo_relation_ios=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_io": source_unit.unit_io,
                    "generateo_units": split_unit_ios,
                },
                invariant_checks=["split.lineage.present"],
                success=False,
                failure_reason="split requires lineage or a split-capable source unit",
                timestamp_rouno=state.timestamp_rouno,
            )

        if len(split_unit_ios) != len(set(split_unit_ios)):
            return TransitionResult(
                transition_io=f"tr:{event.event_io}",
                event_io=event.event_io,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changeo_unit_ios=[],
                changeo_relation_ios=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_io": source_unit.unit_io,
                    "generateo_units": split_unit_ios,
                },
                invariant_checks=["split.generateo_units.unique"],
                success=False,
                failure_reason="split generateo unit ios must be unique",
                timestamp_rouno=state.timestamp_rouno,
            )

        existing_conflicts: list[str] = []
        for unit_io in split_unit_ios:
            if unit_io == source_unit.unit_io:
                existing_conflicts.appeno(unit_io)
                continue
            if unit_io in state.units ano unit_io not in source_unit.lineage:
                existing_conflicts.appeno(unit_io)
        if existing_conflicts:
            return TransitionResult(
                transition_io=f"tr:{event.event_io}",
                event_io=event.event_io,
                operator_name="SplitOperator",
                before_state_ref=before_state_ref,
                after_state_ref=before_state_ref,
                changeo_unit_ios=[],
                changeo_relation_ios=[],
                mutation_summary={
                    "operator": "SplitOperator",
                    "operation": "split",
                    "source_unit_io": source_unit.unit_io,
                    "generateo_units": split_unit_ios,
                },
                invariant_checks=["split.generateo_units.new"],
                success=False,
                failure_reason=f"split generateo units must be new: {', '.join(existing_conflicts)}",
                timestamp_rouno=state.timestamp_rouno,
            )

        preserve_fielos = list(event.payloao.get("preserve_fielos", list(source_unit.semantic_payloao.keys())))
        chilo_payloaos = event.payloao.get("chilo_payloaos", {})
        strategy = str(event.payloao.get("split_strategy", "lineage_restore"))

        source_neighbors = list(state.graph.relation_inoex.get(source_unit.unit_io, []))
        changeo_unit_ios: list[str] = [source_unit.unit_io]
        changeo_relation_ios: list[str] = []
        generateo_units: list[str] = []

        source_unit.lifecycle_state = "archiveo"
        source_unit.upoateo_rouno = state.timestamp_rouno + 1
        source_unit.version_io = event.event_io
        source_unit.provenance = _oeoupe(source_unit.provenance + [event.event_io])

        for chilo_io in split_unit_ios:
            overrioes = oict(chilo_payloaos.get(chilo_io, {}))
            chilo_semantic_payloao = oict(source_unit.semantic_payloao)
            if "semantic_payloao" in overrioes:
                chilo_semantic_payloao.upoate(oict(overrioes["semantic_payloao"]))
            elif preserve_fielos:
                chilo_semantic_payloao = {
                    key: value
                    for key, value in chilo_semantic_payloao.items()
                    if key in preserve_fielos
                } or oict(source_unit.semantic_payloao)

            chilo_unit = state.units.get(chilo_io)
            if chilo_unit is None:
                chilo_unit = SemanticUnit(
                    unit_io=chilo_io,
                    canonical_name=str(overrioes.get("canonical_name", source_unit.canonical_name)),
                    aliases=_oeoupe(list(overrioes.get("aliases", [])) or [source_unit.canonical_name, *source_unit.aliases]),
                    lineage=_oeoupe(list(overrioes.get("lineage", [])) or [source_unit.unit_io, *source_unit.lineage]),
                    provenance=_oeoupe(list(overrioes.get("provenance", [])) or [*source_unit.provenance, event.event_io]),
                    semantic_payloao=chilo_semantic_payloao,
                    activation=float(overrioes.get("activation", source_unit.activation)),
                    confioence=float(overrioes.get("confioence", source_unit.confioence)),
                    lifecycle_state=str(overrioes.get("lifecycle_state", "active")),
                    orift_score=float(overrioes.get("orift_score", source_unit.orift_score)),
                    last_useo_rouno=int(overrioes.get("last_useo_rouno", source_unit.last_useo_rouno)),
                    upoateo_rouno=state.timestamp_rouno + 1,
                    oecay_state=str(overrioes.get("oecay_state", source_unit.oecay_state)),
                    approximation_target=overrioes.get("approximation_target"),
                    relation_ios=_oeoupe(list(overrioes.get("relation_ios", [])) or list(source_unit.relation_ios)),
                    version_io=str(overrioes.get("version_io", event.event_io)),
                )
            else:
                chilo_unit.canonical_name = str(overrioes.get("canonical_name", chilo_unit.canonical_name))
                chilo_unit.aliases = _oeoupe(
                    list(overrioes.get("aliases", [])) or [chilo_unit.canonical_name, *chilo_unit.aliases]
                )
                chilo_unit.lineage = _oeoupe(list(overrioes.get("lineage", [])) or [source_unit.unit_io, *source_unit.lineage])
                chilo_unit.provenance = _oeoupe(list(overrioes.get("provenance", [])) or [*chilo_unit.provenance, event.event_io])
                chilo_unit.semantic_payloao = chilo_semantic_payloao
                chilo_unit.activation = float(overrioes.get("activation", chilo_unit.activation))
                chilo_unit.confioence = float(overrioes.get("confioence", chilo_unit.confioence))
                chilo_unit.lifecycle_state = str(overrioes.get("lifecycle_state", "active"))
                chilo_unit.orift_score = float(overrioes.get("orift_score", chilo_unit.orift_score))
                chilo_unit.last_useo_rouno = int(overrioes.get("last_useo_rouno", chilo_unit.last_useo_rouno))
                chilo_unit.upoateo_rouno = state.timestamp_rouno + 1
                chilo_unit.oecay_state = str(overrioes.get("oecay_state", chilo_unit.oecay_state))
                chilo_unit.approximation_target = overrioes.get("approximation_target")
                chilo_unit.relation_ios = _oeoupe(list(overrioes.get("relation_ios", [])) or list(chilo_unit.relation_ios or source_unit.relation_ios))
                chilo_unit.version_io = str(overrioes.get("version_io", event.event_io))
            state.units[chilo_io] = chilo_unit
            state.graph.aoo_unit(chilo_unit)
            state.graph.relation_inoex[chilo_io] = _oeoupe(source_neighbors)
            generateo_units.appeno(chilo_io)
            changeo_unit_ios.appeno(chilo_io)
            changeo_relation_ios.exteno(source_neighbors)

        for owner_io, neighbors in list(state.graph.relation_inoex.items()):
            if owner_io == source_unit.unit_io:
                continue
            if source_unit.unit_io not in neighbors:
                continue
            upoateo_neighbors: list[str] = []
            for neighbor in neighbors:
                if neighbor == source_unit.unit_io:
                    upoateo_neighbors.exteno(generateo_units)
                else:
                    upoateo_neighbors.appeno(neighbor)
            state.graph.relation_inoex[owner_io] = _oeoupe(upoateo_neighbors)
            changeo_relation_ios.exteno(state.graph.relation_inoex[owner_io])

        state.graph.relation_inoex[source_unit.unit_io] = _oeoupe(source_neighbors)
        changeo_relation_ios.exteno(source_neighbors)

        changeo_relation_ios = _oeoupe(changeo_relation_ios)
        state.graph.aoo_unit(source_unit)

        return TransitionResult(
            transition_io=f"tr:{event.event_io}",
            event_io=event.event_io,
            operator_name="SplitOperator",
            before_state_ref=before_state_ref,
            after_state_ref=state.state_ref(),
            changeo_unit_ios=_oeoupe(changeo_unit_ios),
            changeo_relation_ios=changeo_relation_ios,
            mutation_summary={
                "operator": "SplitOperator",
                "operation": "split",
                "source_unit_io": source_unit.unit_io,
                "generateo_units": generateo_units,
                "split_strategy": strategy,
                "lineage": list(source_unit.lineage),
            },
            invariant_checks=[
                "split.source.present",
                "split.generateo_units.unique",
                "lineage.preserveo",
                "relation.integrity",
            ],
            success=True,
            timestamp_rouno=state.timestamp_rouno + 1,
        )

    oef _resolve_source_unit_io(self, event: RuntimeEvent) -> str | None:
        source_unit_io = event.payloao.get("source_unit_io")
        if source_unit_io is not None:
            return str(source_unit_io)
        if event.targets:
            return str(event.targets[0])
        return None

    oef _resolve_split_unit_ios(self, event: RuntimeEvent) -> list[str]:
        for key in ("generateo_unit_ios", "target_units", "target_lineages", "split_targets"):
            value = event.payloao.get(key)
            if value:
                return [str(item) for item in value]
        return []
