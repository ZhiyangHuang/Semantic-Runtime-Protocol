from __future__ import annotations

from dataclasses import dataclass, field

from .semantic_commit import SemanticCommit
from srp_runtime.version import SemanticVersionGraph, SemanticVersionNode


@dataclass
class CommitManager:
    """Milestone 2 commit boundary.

    This skeleton only freezes the contract for creating semantic commits.
    """

    version_graph: SemanticVersionGraph = field(default_factory=SemanticVersionGraph)
    committed_transition_ids: set[str] = field(default_factory=set)

    def commit_transition(self, transition_result, trace_record, decision_result) -> SemanticCommit:
        if transition_result.transition_id in self.committed_transition_ids:
            raise ValueError("CommitManager cannot commit the same transition twice.")
        if transition_result.event_id != trace_record.event_id or transition_result.event_id != decision_result.event_id:
            raise ValueError("CommitManager requires matching event ids across transition, trace, and decision.")
        if transition_result.transition_id != trace_record.transition_id:
            raise ValueError("CommitManager requires matching transition ids across transition and trace.")
        if transition_result.operator_name != trace_record.operator_name:
            raise ValueError("CommitManager requires matching operator names across transition and trace.")
        if decision_result.selected_operator and decision_result.selected_operator != transition_result.operator_name:
            raise ValueError("CommitManager requires the selected operator to match the executed transition.")

        parent_version_id = decision_result.version_id or transition_result.before_state_ref or None
        new_version_id = transition_result.after_state_ref
        commit_id = f"commit:{transition_result.transition_id}"
        state_ref = transition_result.after_state_ref
        semantic_time = max(transition_result.timestamp_round, decision_result.semantic_time)

        commit = SemanticCommit(
            commit_id=commit_id,
            parent_version_id=parent_version_id,
            new_version_id=new_version_id,
            event_id=transition_result.event_id,
            decision_id=decision_result.decision_id,
            transition_id=transition_result.transition_id,
            trace_id=trace_record.trace_id,
            state_ref=state_ref,
            version_ref=new_version_id,
            semantic_time=semantic_time,
            commit_reason=transition_result.mutation_summary.get("operation", transition_result.operator_name),
            author_context=decision_result.explanation or None,
        )

        if parent_version_id and not self.version_graph.has_version(parent_version_id):
            self.version_graph.add_version(
                SemanticVersionNode(
                    version_id=parent_version_id,
                    parent_versions=[],
                    commit_id="",
                    state_ref=transition_result.before_state_ref,
                    created_round=semantic_time,
                )
            )

        self.version_graph.upsert_version(
            SemanticVersionNode(
                version_id=new_version_id,
                parent_versions=[parent_version_id] if parent_version_id else [],
                commit_id=commit_id,
                state_ref=state_ref,
                created_round=semantic_time,
            )
        )
        self.committed_transition_ids.add(transition_result.transition_id)

        return commit
