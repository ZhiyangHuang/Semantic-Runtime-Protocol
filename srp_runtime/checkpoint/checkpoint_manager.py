from __future__ import annotations

from dataclasses import dataclass, field

from srp_runtime.commit import SemanticCommit
from .runtime_checkpoint import RuntimeCheckpoint


@dataclass
class CheckpointManager:
    """Milestone 2 checkpoint boundary."""

    checkpoints_by_version: dict[str, RuntimeCheckpoint] = field(default_factory=dict)
    checkpoints_by_id: dict[str, RuntimeCheckpoint] = field(default_factory=dict)

    def create_checkpoint(
        self,
        semantic_commit: SemanticCommit,
        state_ref: str,
        event_position: int,
    ) -> RuntimeCheckpoint:
        if not semantic_commit.new_version_id:
            raise ValueError("CheckpointManager requires a semantic commit with a version id.")

        parent_checkpoint_id = None
        if semantic_commit.parent_version_id:
            parent_checkpoint = self.checkpoints_by_version.get(semantic_commit.parent_version_id)
            if parent_checkpoint is not None:
                parent_checkpoint_id = parent_checkpoint.checkpoint_id

        checkpoint = RuntimeCheckpoint(
            checkpoint_id=f"checkpoint:{semantic_commit.commit_id}",
            version_id=semantic_commit.new_version_id,
            commit_id=semantic_commit.commit_id,
            state_ref=state_ref,
            event_offset=event_position,
            created_round=semantic_commit.semantic_time,
            parent_checkpoint_id=parent_checkpoint_id,
            replay_boundary=f"{semantic_commit.new_version_id}@{event_position}",
            metadata={
                "trace_id": semantic_commit.trace_id,
                "semantic_time": semantic_commit.semantic_time,
                "commit_reason": semantic_commit.commit_reason,
            },
        )
        self.checkpoints_by_version[checkpoint.version_id] = checkpoint
        self.checkpoints_by_id[checkpoint.checkpoint_id] = checkpoint
        return checkpoint

    def find_checkpoint(self, version_id: str) -> RuntimeCheckpoint | None:
        return self.checkpoints_by_version.get(version_id)
