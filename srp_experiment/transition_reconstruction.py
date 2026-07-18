from __future__ import annotations

from experiments.srp_runtime_legacy.transition_reconstruction import (
    ReconstructionPolicySuite,
    available_suite_names,
    build_reconstruction_policy_suites,
    render_reconstruction_policy_summary_markdown,
    run_reconstruction_policy_comparison,
    select_reconstruction_policy_suites,
    summarize_reconstruction_policy_comparison,
    write_reconstruction_policy_outputs,
    build_transition_reconstruction_suites,
    render_transition_reconstruction_summary_markdown,
    run_transition_reconstruction_comparison,
    select_transition_reconstruction_suites,
    summarize_transition_reconstruction_comparison,
    write_transition_reconstruction_outputs,
)

run_recovery_comparison = run_transition_reconstruction_comparison
summarize_recovery_comparison = summarize_transition_reconstruction_comparison
render_recovery_summary_markdown = render_transition_reconstruction_summary_markdown
write_recovery_outputs = write_transition_reconstruction_outputs

__all__ = [
    "ReconstructionPolicySuite",
    "available_suite_names",
    "build_reconstruction_policy_suites",
    "render_reconstruction_policy_summary_markdown",
    "run_reconstruction_policy_comparison",
    "select_reconstruction_policy_suites",
    "summarize_reconstruction_policy_comparison",
    "write_reconstruction_policy_outputs",
    "build_transition_reconstruction_suites",
    "render_transition_reconstruction_summary_markdown",
    "run_transition_reconstruction_comparison",
    "select_transition_reconstruction_suites",
    "summarize_transition_reconstruction_comparison",
    "write_transition_reconstruction_outputs",
    "run_recovery_comparison",
    "summarize_recovery_comparison",
    "render_recovery_summary_markdown",
    "write_recovery_outputs",
]
