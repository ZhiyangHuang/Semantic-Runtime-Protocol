from __future__ import annotations

from .common import build_graph, make_case


def build_code_memory_cases():
    return [
        make_case(
            case_id="code_case_1_bug_fix_trace",
            category="bug_fix_trace",
            query="bug fix file dependency",
            source_graph=build_graph(
                [
                    ("bug_101", "Bug 101 breaks startup"),
                    ("fix_101", "Fix 101 patches startup check"),
                    ("file_main", "main.py hosts startup flow"),
                    ("dep_http", "HTTP client dependency"),
                    ("decision_arch", "Decision logs mention startup guard"),
                ],
                [
                    ("bug_101", "fix_101", "caused_by", 0.94),
                    ("fix_101", "file_main", "modifies", 0.93),
                    ("file_main", "dep_http", "depends_on", 0.88),
                    ("decision_arch", "file_main", "documents", 0.60),
                ],
            ),
            reference_node_ids=("bug_101", "fix_101", "file_main"),
            neighborhood_node_ids=("bug_101", "fix_101", "file_main", "dep_http"),
            reference_edge_keys=(
                ("bug_101", "caused_by", "fix_101"),
                ("fix_101", "modifies", "file_main"),
            ),
            required_paths=(("bug_101", "fix_101", "file_main"),),
            evidence_cost=1.0,
            notes="Bug-to-fix-to-file reconstruction.",
        ),
        make_case(
            case_id="code_case_2_dependency_change",
            category="dependency_change",
            query="dependency change commit file",
            source_graph=build_graph(
                [
                    ("commit_7", "Commit 7 updates dependency pin"),
                    ("file_lock", "requirements.txt pins versions"),
                    ("dep_sql", "SQL driver dependency"),
                    ("issue_9", "Issue 9 tracks compatibility break"),
                    ("decision_dep", "Decision to upgrade dependency"),
                ],
                [
                    ("commit_7", "file_lock", "modifies", 0.95),
                    ("file_lock", "dep_sql", "depends_on", 0.92),
                    ("issue_9", "commit_7", "caused_by", 0.80),
                    ("decision_dep", "dep_sql", "approves", 0.55),
                ],
            ),
            reference_node_ids=("commit_7", "file_lock", "dep_sql"),
            neighborhood_node_ids=("commit_7", "file_lock", "dep_sql", "issue_9"),
            reference_edge_keys=(
                ("commit_7", "modifies", "file_lock"),
                ("file_lock", "depends_on", "dep_sql"),
            ),
            required_paths=(("commit_7", "file_lock", "dep_sql"),),
            evidence_cost=1.1,
            notes="Dependency closure under code evolution.",
        ),
    ]
