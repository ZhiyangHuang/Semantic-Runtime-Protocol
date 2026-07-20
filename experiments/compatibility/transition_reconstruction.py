from __future__ import annotations

from .reconstruction_policy_harness import (
    ReconstructionPolicySuite,
    available_suite_names,
    build_reconstruction_policy_suites,
    render_reconstruction_policy_summary_markdown,
    run_reconstruction_policy_comparison as _run_base_comparison,
    select_reconstruction_policy_suites,
    summarize_reconstruction_policy_comparison as _summarize_base_comparison,
    write_reconstruction_policy_outputs,
)

run_transition_reconstruction_comparison = _run_base_comparison
summarize_transition_reconstruction_comparison = _summarize_base_comparison
render_transition_reconstruction_summary_markdown = render_reconstruction_policy_summary_markdown
write_transition_reconstruction_outputs = write_reconstruction_policy_outputs
build_transition_reconstruction_suites = build_reconstruction_policy_suites
select_transition_reconstruction_suites = select_reconstruction_policy_suites

__all__ = [
    "ReconstructionPolicySuite",
    "available_suite_names",
    "build_reconstruction_policy_suites",
    "render_reconstruction_policy_summary_markdown",
    "select_reconstruction_policy_suites",
    "write_reconstruction_policy_outputs",
    "run_transition_reconstruction_comparison",
    "summarize_transition_reconstruction_comparison",
    "render_transition_reconstruction_summary_markdown",
    "write_transition_reconstruction_outputs",
    "build_transition_reconstruction_suites",
    "select_transition_reconstruction_suites",
]
