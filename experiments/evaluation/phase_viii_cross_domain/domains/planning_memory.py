from __future__ import annotations

from .common import build_graph, make_case


def build_planning_memory_cases():
    return [
        make_case(
            case_id="planning_case_1_goal_constraint_chain",
            category="goal_constraint_chain",
            query="goal constraint action resource",
            source_graph=build_graph(
                [
                    ("goal_1", "Goal: deploy safely"),
                    ("action_1", "Action: run tests"),
                    ("constraint_1", "Constraint: no downtime"),
                    ("state_1", "State: staging ready"),
                    ("resource_1", "Resource: CI minutes"),
                ],
                [
                    ("action_1", "resource_1", "requires", 0.94),
                    ("action_1", "constraint_1", "blocked_by", 0.91),
                    ("state_1", "goal_1", "satisfies", 0.87),
                    ("goal_1", "action_1", "guides", 0.72),
                ],
            ),
            reference_node_ids=("goal_1", "action_1", "constraint_1"),
            neighborhood_node_ids=("goal_1", "action_1", "constraint_1", "state_1"),
            reference_edge_keys=(
                ("action_1", "requires", "resource_1"),
                ("action_1", "blocked_by", "constraint_1"),
            ),
            required_paths=(("goal_1", "action_1", "constraint_1"),),
            evidence_cost=1.1,
            notes="Planning memory with a direct constraint dependency.",
        ),
        make_case(
            case_id="planning_case_2_long_dependency",
            category="long_dependency_chain",
            query="goal dependency chain state",
            source_graph=build_graph(
                [
                    ("goal_2", "Goal: ship release"),
                    ("action_2", "Action: merge patch"),
                    ("action_3", "Action: deploy release"),
                    ("constraint_2", "Constraint: freeze window"),
                    ("state_2", "State: release candidate"),
                    ("resource_2", "Resource: release manager"),
                ],
                [
                    ("goal_2", "action_2", "requires", 0.93),
                    ("action_2", "constraint_2", "blocked_by", 0.90),
                    ("action_2", "action_3", "enables", 0.88),
                    ("action_3", "state_2", "produces", 0.84),
                    ("action_3", "resource_2", "requires", 0.86),
                ],
            ),
            reference_node_ids=("goal_2", "action_2", "action_3"),
            neighborhood_node_ids=("goal_2", "action_2", "action_3", "constraint_2", "state_2"),
            reference_edge_keys=(
                ("goal_2", "requires", "action_2"),
                ("action_2", "enables", "action_3"),
                ("action_3", "produces", "state_2"),
            ),
            required_paths=(("goal_2", "action_2", "action_3"), ("goal_2", "action_2", "action_3", "state_2")),
            evidence_cost=1.3,
            notes="Planning chain with changing constraints.",
        ),
    ]
