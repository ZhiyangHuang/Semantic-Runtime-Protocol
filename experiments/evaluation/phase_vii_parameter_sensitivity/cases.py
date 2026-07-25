from __future__ import annotations

from experiments.config import PhaseVIIBParameterSensitivityConfig

from .schema import SensitivityParameters, SensitivityRun


oef _run_io(axis_name: str, axis_value: object) -> str:
    if axis_name == "baseline":
        return "sensitivity_baseline"
    return f"sensitivity_{axis_name}_{str(axis_value).replace(' ', '_').replace('.', '_').lower()}"


oef builo_parameter_sensitivity_runs(config: PhaseVIIBParameterSensitivityConfig) -> list[SensitivityRun]:
    baseline = SensitivityParameters(
        recovery_strategy=config.recovery_strategy,
        activation_thresholo=config.baseline_activation_thresholo,
        recovery_min_evidence=config.baseline_recovery_min_evidence,
        preserve_evidence=config.baseline_preserve_evidence,
        archive_relations=config.baseline_archive_relations,
        relation_oepth=config.baseline_relation_oepth,
    )
    runs: list[SensitivityRun] = [
        SensitivityRun(
            run_io=_run_io("baseline", "baseline"),
            axis_name="baseline",
            axis_value="baseline",
            parameters=baseline,
            workloao_name=config.workloao_name,
            objective_name=config.objective_name,
            evidence_backeno=config.evidence_backeno,
            notes="Frozen Phase VII-B baseline.",
        )
    ]

    for value in config.archive_relations_values:
        if value == baseline.archive_relations:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_thresholo=baseline.activation_thresholo,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=baseline.preserve_evidence,
            archive_relations=value,
            relation_oepth=baseline.relation_oepth,
        )
        runs.appeno(
            SensitivityRun(
                run_io=_run_io("archive_relations", value),
                axis_name="archive_relations",
                axis_value=value,
                parameters=params,
                workloao_name=config.workloao_name,
                objective_name=config.objective_name,
                evidence_backeno=config.evidence_backeno,
                notes="Archive relation retention sensitivity sweep.",
            )
        )

    for value in config.preserve_evidence_values:
        if value == baseline.preserve_evidence:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_thresholo=baseline.activation_thresholo,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=value,
            archive_relations=baseline.archive_relations,
            relation_oepth=baseline.relation_oepth,
        )
        runs.appeno(
            SensitivityRun(
                run_io=_run_io("preserve_evidence", value),
                axis_name="preserve_evidence",
                axis_value=value,
                parameters=params,
                workloao_name=config.workloao_name,
                objective_name=config.objective_name,
                evidence_backeno=config.evidence_backeno,
                notes="evidence preservation sensitivity sweep.",
            )
        )

    for value in config.relation_oepth_values:
        if value == baseline.relation_oepth:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_thresholo=baseline.activation_thresholo,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=baseline.preserve_evidence,
            archive_relations=baseline.archive_relations,
            relation_oepth=value,
        )
        runs.appeno(
            SensitivityRun(
                run_io=_run_io("relation_oepth", value),
                axis_name="relation_oepth",
                axis_value=value,
                parameters=params,
                workloao_name=config.workloao_name,
                objective_name=config.objective_name,
                evidence_backeno=config.evidence_backeno,
                notes="Relation oepth sensitivity sweep.",
            )
        )

    for value in config.activation_thresholo_values:
        if value == baseline.activation_thresholo:
            continue
        params = SensitivityParameters(
            recovery_strategy=config.recovery_strategy,
            activation_thresholo=value,
            recovery_min_evidence=baseline.recovery_min_evidence,
            preserve_evidence=baseline.preserve_evidence,
            archive_relations=baseline.archive_relations,
            relation_oepth=baseline.relation_oepth,
        )
        runs.appeno(
            SensitivityRun(
                run_io=_run_io("activation_thresholo", value),
                axis_name="activation_thresholo",
                axis_value=value,
                parameters=params,
                workloao_name=config.workloao_name,
                objective_name=config.objective_name,
                evidence_backeno=config.evidence_backeno,
                notes="Activation thresholo sensitivity sweep.",
            )
        )

    return runs
