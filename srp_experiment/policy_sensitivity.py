from __future__ import annotations

from srp_experiment.governance_sensitivity import (
    SensitivityAxis,
    build_sensitivity_axes,
    render_governance_sensitivity_markdown,
    run_governance_sensitivity,
    summarize_governance_sensitivity,
    write_governance_sensitivity_outputs,
)

run_policy_sensitivity = run_governance_sensitivity
summarize_policy_sensitivity = summarize_governance_sensitivity
render_policy_sensitivity_markdown = render_governance_sensitivity_markdown
write_policy_sensitivity_outputs = write_governance_sensitivity_outputs

__all__ = [
    "SensitivityAxis",
    "build_sensitivity_axes",
    "render_governance_sensitivity_markdown",
    "run_governance_sensitivity",
    "summarize_governance_sensitivity",
    "write_governance_sensitivity_outputs",
    "render_policy_sensitivity_markdown",
    "run_policy_sensitivity",
    "summarize_policy_sensitivity",
    "write_policy_sensitivity_outputs",
]
