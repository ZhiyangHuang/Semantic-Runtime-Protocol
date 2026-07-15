from __future__ import annotations

from experiments.config import PhaseVIIBParameterSensitivityConfig

from .schema import SensitivityParameters, SensitivityRun


def _run_id(axis_name: str, axis_value: object) -> str:
    if axis_name == "baseline":
        return "sensitivity_baseline"
    return f"sensitivity_{axis_name}_{str(axis_value).replace(' ', '_').replace('.', '_').lower()}"


def build_parameter_sensitivity_runs(config: PhaseVIIBParameterSensitivityConfig) -> list[SensitivityRun]:
    baseline = SensitivityParameters(
        recovery_strategy=config.recovery_strategy,
        activation_threshold=config.baseline_activation_threshold,
        recovery_min_evidence=config.baseline_recovery_min_evidence,
        preserve_evidence=config.baseline_preserve_evidence,
        archive_relations=config.baseline_archive_relations,
        relation_depth=config.baseline_relation_depth,
    )
    runs: list[SensitivityRun] = [
        SensitivityRun(
            run_id=_run_id("baseline", "baseline"),
            axis_name="baseline",
            axis_value="baseline",
            parameters=baseline,
            workload_name=config.workload_name,
            objective_name=config.objective_name,
            evidence_backend=config.evidence_backend,
            notes="Frozen Phase VII-B baseline.",
        )
    ]

    for value in config.archive_relations_values:
        if value == baseline.archive_relations:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_threshold=baseline.activation_threshold,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=baseline.preserve_evidence,
            archive_relations=value,
            relation_depth=baseline.relation_depth,
        )
        runs.append(
            SensitivityRun(
                run_id=_run_id("archive_relations", value),
                axis_name="archive_relations",
                axis_value=value,
                parameters=params,
                workload_name=config.workload_name,
                objective_name=config.objective_name,
                evidence_backend=config.evidence_backend,
                notes="Archive relation retention sensitivity sweep.",
            )
        )

    for value in config.preserve_evidence_values:
        if value == baseline.preserve_evidence:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_threshold=baseline.activation_threshold,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=value,
            archive_relations=baseline.archive_relations,
            relation_depth=baseline.relation_depth,
        )
        runs.append(
            SensitivityRun(
                run_id=_run_id("preserve_evidence", value),
                axis_name="preserve_evidence",
                axis_value=value,
                parameters=params,
                workload_name=config.workload_name,
                objective_name=config.objective_name,
                evidence_backend=config.evidence_backend,
                notes="Evidence preservation sensitivity sweep.",
            )
        )

    for value in config.relation_depth_values:
        if value == baseline.relation_depth:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_threshold=baseline.activation_threshold,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=baseline.preserve_evidence,
            archive_relations=baseline.archive_relations,
            relation_depth=value,
        )
        runs.append(
            SensitivityRun(
                run_id=_run_id("relation_depth", value),
                axis_name="relation_depth",
                axis_value=value,
                parameters=params,
                workload_name=config.workload_name,
                objective_name=config.objective_name,
                evidence_backend=config.evidence_backend,
                notes="Relation depth sensitivity sweep.",
            )
        )

    for value in config.activation_threshold_values:
        if value == baseline.activation_threshold:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_threshold=value,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=baseline.preserve_evidence,
            archive_relations=baseline.archive_relations,
            relation_depth=baseline.relation_depth,
        )
        runs.append(
            SensitivityRun(
                run_id=_run_id("activation_threshold", value),
                axis_name="activation_threshold",
                axis_value=value,
                parameters=params,
                workload_name=config.workload_name,
                objective_name=config.objective_name,
                evidence_backend=config.evidence_backend,
                notes="Activation threshold sensitivity sweep.",
            )
        )

    return runs
