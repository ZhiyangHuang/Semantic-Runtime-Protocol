from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent.parent / "configs"


def read_env_file(path: str | Path) -> dict[str, str]:
    """Read a simple KEY=VALUE config file without mutating process environment."""
    env_path = Path(path)
    loaded: dict[str, str] = {}
    if not env_path.exists():
        return loaded

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            loaded[key] = value
    return loaded


def apply_env_values(values: Mapping[str, str], override: bool = True) -> dict[str, str]:
    """Apply config values to the current process environment."""
    applied: dict[str, str] = {}
    for key, value in values.items():
        if override or key not in os.environ:
            os.environ[key] = value
        applied[key] = value
    return applied


def load_env_file(path: str | Path, override: bool = True) -> dict[str, str]:
    """Read a config file and optionally project it into the process environment."""
    values = read_env_file(path)
    if values:
        apply_env_values(values, override=override)
    return values


def _csv_values(raw: str | None) -> tuple[str, ...]:
    if not raw:
        return ()
    return tuple(item.strip() for item in raw.split(",") if item.strip())


def _csv_floats(raw: str | None) -> tuple[float, ...]:
    return tuple(float(item) for item in _csv_values(raw))


def _csv_ints(raw: str | None) -> tuple[int, ...]:
    return tuple(int(item) for item in _csv_values(raw))


def _csv_bools(raw: str | None) -> tuple[bool, ...]:
    return tuple(item.strip().lower() in {"1", "true", "yes", "on"} for item in _csv_values(raw))


def _get_str(values: Mapping[str, str], key: str, default: str) -> str:
    raw = values.get(key)
    return default if raw is None or raw == "" else raw


def _get_bool(values: Mapping[str, str], key: str, default: bool) -> bool:
    raw = values.get(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_float(values: Mapping[str, str], key: str, default: float) -> float:
    raw = values.get(key)
    return default if raw is None or raw == "" else float(raw)


@dataclass(frozen=True)
class PhaseIIValidationConfig:
    phase: str = "phase_ii_validation"
    validation_mode: str = "closure_validation"
    validation_dimensions: tuple[str, ...] = (
        "boundary_stability",
        "cross_condition_robustness",
        "reproducibility",
        "evidence_consistency",
    )
    validation_backend: str = "vector"
    governance_required: bool = True
    runtime_mutation_allowed: bool = False
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseIIIAOptimizationConfig:
    phase: str = "phase_iii_a"
    optimization_mode: str = "grid_search"
    parameter_axes: tuple[str, ...] = ("activation_threshold", "recovery_min_evidence")
    activation_threshold_values: tuple[float, ...] = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
    recovery_min_evidence_values: tuple[int, ...] = (1, 2, 3)
    objective_semantic_weight: float = 0.4
    objective_recovery_weight: float = 0.3
    objective_resource_weight: float = 0.2
    objective_stability_weight: float = 0.1
    ranking_enabled: bool = True
    governance_approval_required: bool = True
    runtime_mutation_allowed: bool = False
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def objective_weights(self) -> dict[str, float]:
        return {
            "semantic_quality_weight": self.objective_semantic_weight,
            "recovery_success_weight": self.objective_recovery_weight,
            "resource_cost_weight": self.objective_resource_weight,
            "instability_penalty_weight": self.objective_stability_weight,
        }


@dataclass(frozen=True)
class SemanticBackendComparisonConfig:
    phase: str = "evaluation_study"
    experiment_name: str = "semantic_backend_comparison"
    baseline_backend: str = "vector"
    variant_backend: str = "vector_local_model"
    verification_backend: str = "vector_local_model"
    local_model_enabled: bool = True
    fallback_to_heuristic: bool = True
    local_model_url: str = "http://172.25.253.78:8000"
    local_model_name: str = "Qwen/Qwen3-4B-AWQ"
    vector_similarity_threshold: float = 0.5
    model_timeout_seconds: int = 500
    authority_mode: str = "evidence_only"
    model_can_mutate_state: bool = False
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseVRetentionConfig:
    phase: str = "phase_v_retention"
    evaluation_mode: str = "retention_drift"
    parameter_axes: tuple[str, ...] = (
        "activation_threshold",
        "recovery_min_evidence",
        "preserve_evidence",
        "archive_relations",
    )
    activation_threshold_values: tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9)
    recovery_min_evidence_values: tuple[int, ...] = (1, 2, 3)
    preserve_evidence_values: tuple[bool, ...] = (False, True)
    archive_relations_values: tuple[bool, ...] = (False, True)
    baseline_activation_threshold: float = 0.5
    baseline_recovery_min_evidence: int = 1
    baseline_preserve_evidence: bool = False
    baseline_archive_relations: bool = False
    semantic_drift_weights: tuple[float, ...] = (0.45, 0.45, 0.10)
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseVIRelationRecoveryConfig:
    phase: str = "phase_vi_relation_recovery"
    experiment_name: str = "relation_aware_recovery"
    recovery_modes: tuple[str, ...] = (
        "vector_only",
        "relation_expansion",
        "relation_closure",
    )
    top_k: int = 2
    relation_depth: int = 1
    closure_validation: bool = True
    evidence_budget: float = 1.0
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseVIIParameterSensitivityConfig:
    phase: str = "phase_vii_parameter_stability"
    workload_name: str = "phase_vi_relation_recovery_mvp"
    objective_name: str = "governed_reconstruction"
    evidence_backend: str = "relation_closure"
    seeds: tuple[int, ...] = (11, 23, 37, 41, 53, 67, 71, 83, 97, 101)
    baseline_activation_threshold: float = 0.9
    baseline_recovery_min_evidence: int = 1
    baseline_objective_value: float = 0.54
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseVIIBParameterSensitivityConfig:
    phase: str = "phase_vii_parameter_sensitivity"
    evaluation_mode: str = "governance_tradeoff_analysis"
    workload_name: str = "phase_vi_relation_recovery_mvp"
    objective_name: str = "governed_reconstruction"
    evidence_backend: str = "relation_closure"
    recovery_strategy: str = "relation_closure"
    baseline_activation_threshold: float = 0.9
    baseline_recovery_min_evidence: int = 1
    baseline_preserve_evidence: bool = False
    baseline_archive_relations: bool = False
    baseline_relation_depth: int = 1
    archive_relations_values: tuple[bool, ...] = (False, True)
    preserve_evidence_values: tuple[bool, ...] = (False, True)
    relation_depth_values: tuple[int, ...] = (0, 1, 2, 3)
    activation_threshold_values: tuple[float, ...] = (0.1, 0.3, 0.5, 0.7, 0.9)
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseVIIICrossDomainValidationConfig:
    phase: str = "phase_viii_cross_domain"
    evaluation_mode: str = "cross_domain_validation"
    domain_names: tuple[str, ...] = ("code_memory", "knowledge_reasoning", "agent_planning")
    recovery_modes: tuple[str, ...] = ("vector_only", "relation_expansion", "relation_closure")
    top_k: int = 2
    relation_depth: int = 1
    closure_validation: bool = True
    evidence_budget: float = 1.0
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseVIIIRepresentationInvarianceConfig:
    phase: str = "phase_viii_representation_invariance"
    evaluation_mode: str = "representation_invariance"
    encoder_names: tuple[str, ...] = (
        "e5-small-v2",
        "bge-small-en-v1.5",
        "bge-base-en-v1.5",
        "all-MiniLM-L6-v2",
    )
    parser_names: tuple[str, ...] = ("rule_parser", "hybrid_parser", "llm_parser")
    recovery_modes: tuple[str, ...] = ("vector_only", "relation_expansion", "relation_closure")
    top_k: int = 2
    relation_depth: int = 1
    closure_validation: bool = True
    evidence_budget: float = 1.0
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PhaseVIIIImplementationIndependenceConfig:
    phase: str = "phase_viii_implementation_independence"
    evaluation_mode: str = "implementation_independence"
    backend_names: tuple[str, ...] = (
        "flat_semantic_store",
        "graph_semantic_store",
        "vector_overlay_store",
    )
    recovery_modes: tuple[str, ...] = ("vector_only", "relation_expansion", "relation_closure")
    top_k: int = 2
    relation_depth: int = 1
    closure_validation: bool = True
    evidence_budget: float = 1.0
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationConfig:
    phase: str = "external_validation"
    benchmark_names: tuple[str, ...] = ("locomo", "longmemeval", "tgb2")
    baseline_names: tuple[str, ...] = (
        "full_context",
        "sliding_window",
        "summarization_memory",
        "vector_rag",
        "graph_memory",
        "mem0",
        "letta",
        "graphiti",
        "memmachine",
        "srp",
    )
    seeds: tuple[int, ...] = (11, 23, 37)
    benchmark_sample_limit: int = 0
    data_root: str = ""
    output_dir: str = "experiments/results/external_validation"
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationManualSanityConfig:
    phase: str = "external_validation_manual_sanity"
    benchmark_name: str = "locomo"
    baseline_names: tuple[str, ...] = (
        "full_context",
        "sliding_window",
        "vector_rag",
        "srp",
    )
    case_limit: int = 12
    seed: int = 11
    benchmark_sample_limit: int = 0
    data_root: str = "data/locomo"
    output_dir: str = "experiments/results/external_validation_locomo_sanity"
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationCalibrationAwareConfig:
    phase: str = "external_validation_calibration_aware"
    benchmark_names: tuple[str, ...] = ("locomo",)
    baseline_names: tuple[str, ...] = (
        "full_context",
        "sliding_window",
        "vector_rag",
        "srp",
    )
    seeds: tuple[int, ...] = (11, 23, 37)
    benchmark_sample_limit: int = 2
    data_root: str = "data/locomo"
    source_output_dir: str = "experiments/results/external_validation_locomo_mvp"
    output_dir: str = "experiments/results/external_validation_locomo_calibration_aware"
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationLongMemEvalAdapterValidationConfig:
    phase: str = "external_validation_longmemeval_adapter_validation"
    benchmark_name: str = "longmemeval"
    baseline_names: tuple[str, ...] = (
        "full_context",
        "sliding_window",
        "vector_rag",
        "srp",
    )
    seeds: tuple[int, ...] = (11, 23, 37)
    benchmark_sample_limit: int = 2
    data_root: str = "data/longmemeval"
    source_output_dir: str = "experiments/results/external_validation_longmemeval_mvp"
    output_dir: str = "experiments/results/external_validation_longmemeval_calibration_aware"
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalValidationLongMemEvalEvidenceConfig:
    phase: str = "external_validation_longmemeval_evidence"
    benchmark_name: str = "longmemeval"
    baseline_names: tuple[str, ...] = (
        "full_context",
        "sliding_window",
        "vector_rag",
        "srp",
    )
    seeds: tuple[int, ...] = (11, 23, 37)
    benchmark_sample_limit: int = 0
    data_root: str = "data/longmemeval"
    output_dir: str = "experiments/results/external_validation_longmemeval_evidence"
    model_provider: str = "local_vllm"
    model_backend: str = "vllm"
    model_endpoint: str = "http://172.25.253.78:8000"
    model_name: str = "Qwen/Qwen3-4B-AWQ"
    model_tokenizer: str = "Qwen/Qwen3-4B-AWQ"
    prompt_template_id: str = "longmemeval_shared_generation_prompt_v1"
    temperature: float = 0.0
    max_output_tokens: int = 96
    model_timeout_seconds: int = 500
    same_endpoint_across_baselines: bool = True
    source_path: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_phase_ii_validation_config(path: str | Path | None = None) -> PhaseIIValidationConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_ii_validation.env"
    values = read_env_file(config_path)
    return PhaseIIValidationConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_ii_validation"),
        validation_mode=_get_str(values, "VALIDATION_MODE", "closure_validation"),
        validation_dimensions=_csv_values(
            values.get("VALIDATION_DIMENSIONS")
        )
        or PhaseIIValidationConfig.validation_dimensions,
        validation_backend=_get_str(values, "VALIDATION_BACKEND", "vector"),
        governance_required=_get_bool(values, "GOVERNANCE_REQUIRED", True),
        runtime_mutation_allowed=_get_bool(values, "RUNTIME_MUTATION_ALLOWED", False),
        source_path=str(config_path),
    )


def load_phase_iii_a_config(path: str | Path | None = None) -> PhaseIIIAOptimizationConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_iii_a.env"
    values = read_env_file(config_path)
    return PhaseIIIAOptimizationConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_iii_a"),
        optimization_mode=_get_str(values, "OPTIMIZATION_MODE", "grid_search"),
        parameter_axes=_csv_values(values.get("PARAMETER_AXES"))
        or PhaseIIIAOptimizationConfig.parameter_axes,
        activation_threshold_values=_csv_floats(values.get("ACTIVATION_THRESHOLD_VALUES"))
        or PhaseIIIAOptimizationConfig.activation_threshold_values,
        recovery_min_evidence_values=_csv_ints(values.get("RECOVERY_MIN_EVIDENCE_VALUES"))
        or PhaseIIIAOptimizationConfig.recovery_min_evidence_values,
        objective_semantic_weight=_get_float(values, "OBJECTIVE_SEMANTIC_WEIGHT", 0.4),
        objective_recovery_weight=_get_float(values, "OBJECTIVE_RECOVERY_WEIGHT", 0.3),
        objective_resource_weight=_get_float(values, "OBJECTIVE_RESOURCE_WEIGHT", 0.2),
        objective_stability_weight=_get_float(values, "OBJECTIVE_STABILITY_WEIGHT", 0.1),
        ranking_enabled=_get_bool(values, "RANKING_ENABLED", True),
        governance_approval_required=_get_bool(values, "GOVERNANCE_APPROVAL_REQUIRED", True),
        runtime_mutation_allowed=_get_bool(values, "RUNTIME_MUTATION_ALLOWED", False),
        source_path=str(config_path),
    )


def load_semantic_backend_comparison_config(
    path: str | Path | None = None,
) -> SemanticBackendComparisonConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "semantic_backend_comparison.env"
    values = read_env_file(config_path)
    return SemanticBackendComparisonConfig(
        phase=_get_str(values, "SRP_PHASE", "evaluation_study"),
        experiment_name=_get_str(values, "EXPERIMENT_NAME", "semantic_backend_comparison"),
        baseline_backend=_get_str(values, "BASELINE_BACKEND", "vector"),
        variant_backend=_get_str(values, "VARIANT_BACKEND", "vector_local_model"),
        verification_backend=_get_str(values, "VERIFICATION_BACKEND", "vector_local_model"),
        local_model_enabled=_get_bool(values, "LOCAL_MODEL_ENABLED", True),
        fallback_to_heuristic=_get_bool(values, "FALLBACK_TO_HEURISTIC", True),
        local_model_url=_get_str(values, "LOCAL_MODEL_URL", "http://172.25.253.78:8000"),
        local_model_name=_get_str(values, "LOCAL_MODEL_NAME", "Qwen/Qwen3-4B-AWQ"),
        vector_similarity_threshold=_get_float(values, "VECTOR_SIMILARITY_THRESHOLD", 0.5),
        model_timeout_seconds=int(_get_float(values, "MODEL_TIMEOUT_SECONDS", 500)),
        authority_mode=_get_str(values, "AUTHORITY_MODE", "evidence_only"),
        model_can_mutate_state=_get_bool(values, "MODEL_CAN_MUTATE_STATE", False),
        source_path=str(config_path),
    )


def load_phase_v_retention_config(path: str | Path | None = None) -> PhaseVRetentionConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_v_retention.env"
    values = read_env_file(config_path)
    return PhaseVRetentionConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_v_retention"),
        evaluation_mode=_get_str(values, "EVALUATION_MODE", "retention_drift"),
        parameter_axes=_csv_values(values.get("PARAMETER_AXES"))
        or PhaseVRetentionConfig.parameter_axes,
        activation_threshold_values=_csv_floats(values.get("ACTIVATION_THRESHOLD_VALUES"))
        or PhaseVRetentionConfig.activation_threshold_values,
        recovery_min_evidence_values=_csv_ints(values.get("RECOVERY_MIN_EVIDENCE_VALUES"))
        or PhaseVRetentionConfig.recovery_min_evidence_values,
        preserve_evidence_values=_csv_bools(values.get("PRESERVE_EVIDENCE_VALUES"))
        or PhaseVRetentionConfig.preserve_evidence_values,
        archive_relations_values=_csv_bools(values.get("ARCHIVE_RELATIONS_VALUES"))
        or PhaseVRetentionConfig.archive_relations_values,
        baseline_activation_threshold=_get_float(values, "BASELINE_ACTIVATION_THRESHOLD", 0.5),
        baseline_recovery_min_evidence=int(_get_float(values, "BASELINE_RECOVERY_MIN_EVIDENCE", 1)),
        baseline_preserve_evidence=_get_bool(values, "BASELINE_PRESERVE_EVIDENCE", False),
        baseline_archive_relations=_get_bool(values, "BASELINE_ARCHIVE_RELATIONS", False),
        semantic_drift_weights=_csv_floats(values.get("SEMANTIC_DRIFT_WEIGHTS"))
        or PhaseVRetentionConfig.semantic_drift_weights,
        source_path=str(config_path),
    )


def load_phase_vi_relation_recovery_config(path: str | Path | None = None) -> PhaseVIRelationRecoveryConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_vi_relation_recovery.env"
    values = read_env_file(config_path)
    return PhaseVIRelationRecoveryConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_vi_relation_recovery"),
        experiment_name=_get_str(values, "EXPERIMENT_NAME", "relation_aware_recovery"),
        recovery_modes=_csv_values(values.get("RECOVERY_MODES"))
        or PhaseVIRelationRecoveryConfig.recovery_modes,
        top_k=int(_get_float(values, "TOP_K", 2)),
        relation_depth=int(_get_float(values, "RELATION_DEPTH", 1)),
        closure_validation=_get_bool(values, "CLOSURE_VALIDATION", True),
        evidence_budget=_get_float(values, "EVIDENCE_BUDGET", 1.0),
        source_path=str(config_path),
    )


def load_phase_vii_parameter_sensitivity_config(path: str | Path | None = None) -> PhaseVIIParameterSensitivityConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_vii_parameter_stability.env"
    values = read_env_file(config_path)
    return PhaseVIIParameterSensitivityConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_vii_parameter_stability"),
        workload_name=_get_str(values, "WORKLOAD_NAME", "phase_vi_relation_recovery_mvp"),
        objective_name=_get_str(values, "OBJECTIVE_NAME", "governed_reconstruction"),
        evidence_backend=_get_str(values, "EVIDENCE_BACKEND", "relation_closure"),
        seeds=_csv_ints(values.get("SEEDS")) or PhaseVIIParameterSensitivityConfig.seeds,
        baseline_activation_threshold=_get_float(values, "BASELINE_ACTIVATION_THRESHOLD", 0.9),
        baseline_recovery_min_evidence=int(_get_float(values, "BASELINE_RECOVERY_MIN_EVIDENCE", 1)),
        baseline_objective_value=_get_float(values, "BASELINE_OBJECTIVE_VALUE", 0.54),
        source_path=str(config_path),
    )


def load_phase_vii_parameter_sensitivity_analysis_config(
    path: str | Path | None = None,
) -> PhaseVIIBParameterSensitivityConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_vii_parameter_sensitivity.env"
    values = read_env_file(config_path)
    return PhaseVIIBParameterSensitivityConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_vii_parameter_sensitivity"),
        evaluation_mode=_get_str(values, "EVALUATION_MODE", "governance_tradeoff_analysis"),
        workload_name=_get_str(values, "WORKLOAD_NAME", "phase_vi_relation_recovery_mvp"),
        objective_name=_get_str(values, "OBJECTIVE_NAME", "governed_reconstruction"),
        evidence_backend=_get_str(values, "EVIDENCE_BACKEND", "relation_closure"),
        recovery_strategy=_get_str(values, "RECOVERY_STRATEGY", "relation_closure"),
        baseline_activation_threshold=_get_float(values, "BASELINE_ACTIVATION_THRESHOLD", 0.9),
        baseline_recovery_min_evidence=int(_get_float(values, "BASELINE_RECOVERY_MIN_EVIDENCE", 1)),
        baseline_preserve_evidence=_get_bool(values, "BASELINE_PRESERVE_EVIDENCE", False),
        baseline_archive_relations=_get_bool(values, "BASELINE_ARCHIVE_RELATIONS", False),
        baseline_relation_depth=int(_get_float(values, "BASELINE_RELATION_DEPTH", 1)),
        archive_relations_values=_csv_bools(values.get("ARCHIVE_RELATIONS_VALUES"))
        or PhaseVIIBParameterSensitivityConfig.archive_relations_values,
        preserve_evidence_values=_csv_bools(values.get("PRESERVE_EVIDENCE_VALUES"))
        or PhaseVIIBParameterSensitivityConfig.preserve_evidence_values,
        relation_depth_values=_csv_ints(values.get("RELATION_DEPTH_VALUES"))
        or PhaseVIIBParameterSensitivityConfig.relation_depth_values,
        activation_threshold_values=_csv_floats(values.get("ACTIVATION_THRESHOLD_VALUES"))
        or PhaseVIIBParameterSensitivityConfig.activation_threshold_values,
        source_path=str(config_path),
    )


def load_phase_viii_cross_domain_validation_config(
    path: str | Path | None = None,
) -> PhaseVIIICrossDomainValidationConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_viii_cross_domain.env"
    values = read_env_file(config_path)
    return PhaseVIIICrossDomainValidationConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_viii_cross_domain"),
        evaluation_mode=_get_str(values, "EVALUATION_MODE", "cross_domain_validation"),
        domain_names=_csv_values(values.get("DOMAIN_NAMES")) or PhaseVIIICrossDomainValidationConfig.domain_names,
        recovery_modes=_csv_values(values.get("RECOVERY_MODES")) or PhaseVIIICrossDomainValidationConfig.recovery_modes,
        top_k=int(_get_float(values, "TOP_K", 2)),
        relation_depth=int(_get_float(values, "RELATION_DEPTH", 1)),
        closure_validation=_get_bool(values, "CLOSURE_VALIDATION", True),
        evidence_budget=_get_float(values, "EVIDENCE_BUDGET", 1.0),
        source_path=str(config_path),
    )


def load_phase_viii_representation_invariance_config(
    path: str | Path | None = None,
) -> PhaseVIIIRepresentationInvarianceConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_viii_representation_invariance.env"
    values = read_env_file(config_path)
    return PhaseVIIIRepresentationInvarianceConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_viii_representation_invariance"),
        evaluation_mode=_get_str(values, "EVALUATION_MODE", "representation_invariance"),
        encoder_names=_csv_values(values.get("ENCODER_NAMES")) or PhaseVIIIRepresentationInvarianceConfig.encoder_names,
        parser_names=_csv_values(values.get("PARSER_NAMES")) or PhaseVIIIRepresentationInvarianceConfig.parser_names,
        recovery_modes=_csv_values(values.get("RECOVERY_MODES")) or PhaseVIIIRepresentationInvarianceConfig.recovery_modes,
        top_k=int(_get_float(values, "TOP_K", 2)),
        relation_depth=int(_get_float(values, "RELATION_DEPTH", 1)),
        closure_validation=_get_bool(values, "CLOSURE_VALIDATION", True),
        evidence_budget=_get_float(values, "EVIDENCE_BUDGET", 1.0),
        source_path=str(config_path),
    )


def load_phase_viii_implementation_independence_config(
    path: str | Path | None = None,
) -> PhaseVIIIImplementationIndependenceConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "phase_viii_implementation_independence.env"
    values = read_env_file(config_path)
    return PhaseVIIIImplementationIndependenceConfig(
        phase=_get_str(values, "SRP_PHASE", "phase_viii_implementation_independence"),
        evaluation_mode=_get_str(values, "EVALUATION_MODE", "implementation_independence"),
        backend_names=_csv_values(values.get("BACKEND_NAMES")) or PhaseVIIIImplementationIndependenceConfig.backend_names,
        recovery_modes=_csv_values(values.get("RECOVERY_MODES")) or PhaseVIIIImplementationIndependenceConfig.recovery_modes,
        top_k=int(_get_float(values, "TOP_K", 2)),
        relation_depth=int(_get_float(values, "RELATION_DEPTH", 1)),
        closure_validation=_get_bool(values, "CLOSURE_VALIDATION", True),
        evidence_budget=_get_float(values, "EVIDENCE_BUDGET", 1.0),
        source_path=str(config_path),
    )


def load_external_validation_config(path: str | Path | None = None) -> ExternalValidationConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "external_validation.env"
    values = read_env_file(config_path)
    return ExternalValidationConfig(
        phase=_get_str(values, "SRP_PHASE", "external_validation"),
        benchmark_names=_csv_values(values.get("BENCHMARK_NAMES")) or ExternalValidationConfig.benchmark_names,
        baseline_names=_csv_values(values.get("BASELINE_NAMES")) or ExternalValidationConfig.baseline_names,
        seeds=_csv_ints(values.get("SEEDS")) or ExternalValidationConfig.seeds,
        benchmark_sample_limit=int(_get_float(values, "BENCHMARK_SAMPLE_LIMIT", 0)),
        data_root=_get_str(values, "DATA_ROOT", ""),
        output_dir=_get_str(values, "OUTPUT_DIR", "experiments/results/external_validation"),
        source_path=str(config_path),
    )


def load_external_validation_manual_sanity_config(path: str | Path | None = None) -> ExternalValidationManualSanityConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "external_validation_locomo_manual_sanity.env"
    values = read_env_file(config_path)
    return ExternalValidationManualSanityConfig(
        phase=_get_str(values, "SRP_PHASE", "external_validation_manual_sanity"),
        benchmark_name=_get_str(values, "BENCHMARK_NAME", "locomo"),
        baseline_names=_csv_values(values.get("BASELINE_NAMES"))
        or ExternalValidationManualSanityConfig.baseline_names,
        case_limit=int(_get_float(values, "CASE_LIMIT", 12)),
        seed=int(_get_float(values, "SEED", 11)),
        benchmark_sample_limit=int(_get_float(values, "BENCHMARK_SAMPLE_LIMIT", 0)),
        data_root=_get_str(values, "DATA_ROOT", "data/locomo"),
        output_dir=_get_str(values, "OUTPUT_DIR", "experiments/results/external_validation_locomo_sanity"),
        source_path=str(config_path),
    )


def load_external_validation_calibration_aware_config(
    path: str | Path | None = None,
) -> ExternalValidationCalibrationAwareConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "external_validation_locomo_mvp_calibration_aware.env"
    values = read_env_file(config_path)
    return ExternalValidationCalibrationAwareConfig(
        phase=_get_str(values, "SRP_PHASE", "external_validation_calibration_aware"),
        benchmark_names=_csv_values(values.get("BENCHMARK_NAMES"))
        or ExternalValidationCalibrationAwareConfig.benchmark_names,
        baseline_names=_csv_values(values.get("BASELINE_NAMES"))
        or ExternalValidationCalibrationAwareConfig.baseline_names,
        seeds=_csv_ints(values.get("SEEDS")) or ExternalValidationCalibrationAwareConfig.seeds,
        benchmark_sample_limit=int(_get_float(values, "BENCHMARK_SAMPLE_LIMIT", 2)),
        data_root=_get_str(values, "DATA_ROOT", "data/locomo"),
        source_output_dir=_get_str(
            values,
            "SOURCE_OUTPUT_DIR",
            "experiments/results/external_validation_locomo_mvp",
        ),
        output_dir=_get_str(
            values,
            "OUTPUT_DIR",
            "experiments/results/external_validation_locomo_calibration_aware",
        ),
        source_path=str(config_path),
    )


def load_external_validation_longmemeval_adapter_validation_config(
    path: str | Path | None = None,
) -> ExternalValidationLongMemEvalAdapterValidationConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "external_validation_longmemeval_adapter_validation.env"
    values = read_env_file(config_path)
    return ExternalValidationLongMemEvalAdapterValidationConfig(
        phase=_get_str(values, "SRP_PHASE", "external_validation_longmemeval_adapter_validation"),
        benchmark_name=_get_str(values, "BENCHMARK_NAME", "longmemeval"),
        baseline_names=_csv_values(values.get("BASELINE_NAMES"))
        or ExternalValidationLongMemEvalAdapterValidationConfig.baseline_names,
        seeds=_csv_ints(values.get("SEEDS")) or ExternalValidationLongMemEvalAdapterValidationConfig.seeds,
        benchmark_sample_limit=int(_get_float(values, "BENCHMARK_SAMPLE_LIMIT", 2)),
        data_root=_get_str(values, "DATA_ROOT", "data/longmemeval"),
        source_output_dir=_get_str(
            values,
            "SOURCE_OUTPUT_DIR",
            "experiments/results/external_validation_longmemeval_mvp",
        ),
        output_dir=_get_str(
            values,
            "OUTPUT_DIR",
            "experiments/results/external_validation_longmemeval_calibration_aware",
        ),
        source_path=str(config_path),
    )


def load_external_validation_longmemeval_evidence_config(
    path: str | Path | None = None,
) -> ExternalValidationLongMemEvalEvidenceConfig:
    config_path = Path(path) if path is not None else DEFAULT_CONFIG_DIR / "external_validation_longmemeval_evidence.env"
    values = read_env_file(config_path)
    return ExternalValidationLongMemEvalEvidenceConfig(
        phase=_get_str(values, "SRP_PHASE", "external_validation_longmemeval_evidence"),
        benchmark_name=_get_str(values, "BENCHMARK_NAME", "longmemeval"),
        baseline_names=_csv_values(values.get("BASELINE_NAMES"))
        or ExternalValidationLongMemEvalEvidenceConfig.baseline_names,
        seeds=_csv_ints(values.get("SEEDS")) or ExternalValidationLongMemEvalEvidenceConfig.seeds,
        benchmark_sample_limit=int(_get_float(values, "BENCHMARK_SAMPLE_LIMIT", 0)),
        data_root=_get_str(values, "DATA_ROOT", "data/longmemeval"),
        output_dir=_get_str(values, "OUTPUT_DIR", "experiments/results/external_validation_longmemeval_evidence"),
        model_provider=_get_str(values, "MODEL_PROVIDER", "local_vllm"),
        model_backend=_get_str(values, "MODEL_BACKEND", "vllm"),
        model_endpoint=_get_str(values, "MODEL_ENDPOINT", "http://172.25.253.78:8000"),
        model_name=_get_str(values, "MODEL_NAME", "Qwen/Qwen3-4B-AWQ"),
        model_tokenizer=_get_str(values, "MODEL_TOKENIZER", "Qwen/Qwen3-4B-AWQ"),
        prompt_template_id=_get_str(values, "PROMPT_TEMPLATE_ID", "longmemeval_shared_generation_prompt_v1"),
        temperature=_get_float(values, "TEMPERATURE", 0.0),
        max_output_tokens=int(_get_float(values, "MAX_OUTPUT_TOKENS", 96)),
        model_timeout_seconds=int(_get_float(values, "MODEL_TIMEOUT_SECONDS", 500)),
        same_endpoint_across_baselines=_get_bool(values, "SAME_ENDPOINT_ACROSS_BASELINES", True),
        source_path=str(config_path),
    )


def load_experiment_config(phase: str, config_dir: str | Path | None = None) -> Any:
    base_dir = Path(config_dir) if config_dir is not None else DEFAULT_CONFIG_DIR
    normalized = phase.strip().lower()
    if normalized in {"phase_ii_validation", "phase-ii-validation", "validation"}:
        return load_phase_ii_validation_config(base_dir / "phase_ii_validation.env")
    if normalized in {"phase_iii_a", "phase-iii-a", "optimization"}:
        return load_phase_iii_a_config(base_dir / "phase_iii_a.env")
    if normalized in {"evaluation_study", "semantic_backend_comparison", "backend_comparison"}:
        return load_semantic_backend_comparison_config(base_dir / "semantic_backend_comparison.env")
    if normalized in {"phase_v_retention", "phase-v-retention", "retention", "drift"}:
        return load_phase_v_retention_config(base_dir / "phase_v_retention.env")
    if normalized in {"phase_vi_relation_recovery", "phase-vi-relation-recovery", "relation_recovery"}:
        return load_phase_vi_relation_recovery_config(base_dir / "phase_vi_relation_recovery.env")
    if normalized in {"phase_vii_parameter_stability", "phase-vii-parameter-stability", "parameter_stability"}:
        return load_phase_vii_parameter_sensitivity_config(base_dir / "phase_vii_parameter_stability.env")
    if normalized in {"phase_vii_parameter_sensitivity", "phase-vii-parameter-sensitivity", "parameter_sensitivity", "phase_vii_b"}:
        return load_phase_vii_parameter_sensitivity_analysis_config(base_dir / "phase_vii_parameter_sensitivity.env")
    if normalized in {"phase_viii_cross_domain", "phase-viii-cross-domain", "cross_domain", "cross_domain_validation"}:
        return load_phase_viii_cross_domain_validation_config(base_dir / "phase_viii_cross_domain.env")
    if normalized in {"phase_viii_representation_invariance", "phase-viii-representation-invariance", "representation_invariance", "phase_viii_b"}:
        return load_phase_viii_representation_invariance_config(base_dir / "phase_viii_representation_invariance.env")
    if normalized in {"phase_viii_implementation_independence", "phase-viii-implementation-independence", "implementation_independence", "phase_viii_c"}:
        return load_phase_viii_implementation_independence_config(base_dir / "phase_viii_implementation_independence.env")
    if normalized in {"external_validation", "external-validity", "external_validation_stage"}:
        return load_external_validation_config(base_dir / "external_validation.env")
    if normalized in {"external_validation_calibration_aware", "external-validation-calibration-aware", "locomo_calibration_aware"}:
        return load_external_validation_calibration_aware_config(base_dir / "external_validation_locomo_mvp_calibration_aware.env")
    if normalized in {"external_validation_longmemeval_adapter_validation", "external-validation-longmemeval-adapter-validation", "longmemeval_adapter_validation"}:
        return load_external_validation_longmemeval_adapter_validation_config(base_dir / "external_validation_longmemeval_adapter_validation.env")
    if normalized in {"external_validation_longmemeval_evidence", "external-validation-longmemeval-evidence", "longmemeval_evidence"}:
        return load_external_validation_longmemeval_evidence_config(base_dir / "external_validation_longmemeval_evidence.env")
    if normalized in {"external_validation_manual_sanity", "external-validation-manual-sanity", "locomo_manual_sanity"}:
        return load_external_validation_manual_sanity_config(base_dir / "external_validation_locomo_manual_sanity.env")
    raise ValueError(f"Unknown experiment phase: {phase}")
