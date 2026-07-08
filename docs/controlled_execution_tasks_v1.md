# Controlled Execution Tasks v1

This document defines a minimal set of synthetic tasks for execution validation.
The goal is to test whether semantic allocation produces an active state that is
better than random retention for task execution.

Use the same recovery, allocation, execution, and evaluation pipeline across all tasks.
Only the task dependency structure should vary.

## Evaluation Setup

- baseline policies:
  - `recovered`
  - `minimal.active`
  - `random.active`
- fixed execution model
- fixed recovery pipeline
- fixed evaluation metrics

Recommended metrics:

- `keyword_recall`
- `dependency_coverage`
- `dependency_precision`
- `dependency_f1`
- `task_success`
- `execution_state_object_count`
- `execution_prompt_tokens`

Recommended record fields:

- `task_id`
- `task_type`
- `policy`
- `execution_source`
- `seed`
- `raw_answer`
- `answer_tokens`
- `task_success`

## Task Types

### Type A: Single Dependency

Goal:

- verify that a direct dependency is preserved in active state

Pattern:

- one entity depends on one object
- query asks for the direct dependency

Template:

```text
Entity A depends on Entity B.
Question:
What does Entity A depend on?
```

Expected behavior:

- `minimal.active` should retain the direct dependency better than `random.active`

### Type B: Constraint Dependency

Goal:

- verify that a rule or constraint is preserved in active state

Pattern:

- an object has a constraint or restriction
- query asks who or what is allowed

Template:

```text
Database Atlas cannot be modified after deployment.
Only administrators can approve changes to Atlas.
Question:
Who can approve changes to Atlas after deployment?
```

Expected behavior:

- active state should preserve the constraint boundary, not just the entity name

### Type C: Multi-Hop Dependency

Goal:

- verify that a dependency closure is preserved across several hops

Pattern:

- entity -> relation -> constraint -> decision
- query requires combining at least two hops

Template:

```text
Project Orion uses Database Atlas.
Database Atlas is managed by Team Blue.
Team Blue requires administrator approval for changes.
Question:
Who can approve changes to Project Orion?
```

Expected behavior:

- `minimal.active` should outperform `random.active` when the chain must be preserved

### Type D: Distractor Heavy

Goal:

- test whether allocation keeps useful objects while dropping irrelevant noise

Pattern:

- one dependency chain
- many unrelated facts

Template:

```text
Project Orion depends on Database Atlas.
Database Atlas cannot be modified after deployment.
Alice can approve changes to Atlas before version 2.0.
The cafeteria is on the third floor.
The backup server is in Prague.
Bob likes coffee.
Question:
Who can approve changes to Atlas after version 2.0?
```

Expected behavior:

- `minimal.active` should preserve the relevant dependency objects better than `random.active`

## Minimal Task Set

The first release should contain 10 tasks total:

- 3 tasks of Type A
- 2 tasks of Type B
- 3 tasks of Type C
- 2 tasks of Type D

This gives a small but balanced set for the first execution validation matrix.

## Suggested Task Fields

Each task should include:

- `id`
- `task_type`
- `source`
- `initial_state.memory`
- `queries`
- `query_expectations`
- `expected_output`
- `expected_keywords`
- `metadata.required_dependency_labels`
- `metadata.notes`

## Dependency Label Guidance

Use human-readable dependency labels in `metadata.required_dependency_labels`.

Examples:

- `Project Orion depends on Database Atlas`
- `Database Atlas cannot be modified after deployment`
- `Only administrators can approve changes to Atlas after version 2.0`

Do not encode the dependency oracle as runtime object IDs in the task file.
The runtime object resolver should map labels to runtime object IDs during evaluation.

## Success Criteria

The task set is useful if it can distinguish:

- `minimal.active` vs `random.active`
- `minimal.active` vs `recovered`

Desired signal:

- `minimal.active` achieves higher dependency preservation than `random.active`
- `minimal.active` retains sufficient task performance while using fewer execution tokens

