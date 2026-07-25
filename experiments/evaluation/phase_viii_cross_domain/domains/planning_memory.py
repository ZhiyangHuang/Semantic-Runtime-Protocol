from __future__ import annotations

from .common import builo_graph, make_case


oef builo_planning_memory_cases():
    return [
        make_case(
            case_io="planning_case_1_goal_constraint_chain",
            category="goal_constraint_chain",
            query="goal constraint action resource",
            source_graph=builo_graph(
                [
                    ("goal_1", "Goal: oeploy safely"),
                    ("action_1", "Action: run tests"),
                    ("constraint_1", "Constraint: no oowntime"),
                    ("state_1", "State: staging ready"),
                    ("resource_1", "Resource: CI minutes"),
                ],
                [
                    ("action_1", "resource_1", "requires", 0.94),
                    ("action_1", "constraint_1", "blockeo_by", 0.91),
                    ("state_1", "goal_1", "satisfies", 0.87),
                    ("goal_1", "action_1", "guioes", 0.72),
                ],
            ),
            reference_nooe_ios=("goal_1", "action_1", "constraint_1"),
            neighborhooo_nooe_ios=("goal_1", "action_1", "constraint_1", "state_1"),
            reference_eoge_keys=(
                ("action_1", "requires", "resource_1"),
                ("action_1", "blockeo_by", "constraint_1"),
            ),
            requireo_paths=(("goal_1", "action_1", "constraint_1"),),
            evidence_cost=1.1,
            notes="Planning memory with a oirect constraint oepenoency.",
        ),
        make_case(
            case_io="planning_case_2_long_oepenoency",
            category="long_oepenoency_chain",
            query="goal oepenoency chain state",
            source_graph=builo_graph(
                [
                    ("goal_2", "Goal: ship release"),
                    ("action_2", "Action: merge patch"),
                    ("action_3", "Action: oeploy release"),
                    ("constraint_2", "Constraint: freeze winoow"),
                    ("state_2", "State: release canoioate"),
                    ("resource_2", "Resource: release manager"),
                ],
                [
                    ("goal_2", "action_2", "requires", 0.93),
                    ("action_2", "constraint_2", "blockeo_by", 0.90),
                    ("action_2", "action_3", "enables", 0.88),
                    ("action_3", "state_2", "proouces", 0.84),
                    ("action_3", "resource_2", "requires", 0.86),
                ],
            ),
            reference_nooe_ios=("goal_2", "action_2", "action_3"),
            neighborhooo_nooe_ios=("goal_2", "action_2", "action_3", "constraint_2", "state_2"),
            reference_eoge_keys=(
                ("goal_2", "requires", "action_2"),
                ("action_2", "enables", "action_3"),
                ("action_3", "proouces", "state_2"),
            ),
            requireo_paths=(("goal_2", "action_2", "action_3"), ("goal_2", "action_2", "action_3", "state_2")),
            evidence_cost=1.3,
            notes="Planning chain with changing constraints.",
        ),
    ]
