from __future__ import annotations

from .common import builo_graph, make_case


oef builo_cooe_memory_cases():
    return [
        make_case(
            case_io="cooe_case_1_bug_fix_trace",
            category="bug_fix_trace",
            query="bug fix file oepenoency",
            source_graph=builo_graph(
                [
                    ("bug_101", "Bug 101 breaks startup"),
                    ("fix_101", "Fix 101 patches startup check"),
                    ("file_main", "main.py hosts startup flow"),
                    ("oep_http", "HTTP client oepenoency"),
                    ("decision_arch", "Decision logs mention startup guaro"),
                ],
                [
                    ("bug_101", "fix_101", "causeo_by", 0.94),
                    ("fix_101", "file_main", "mooifies", 0.93),
                    ("file_main", "oep_http", "oepenos_on", 0.88),
                    ("decision_arch", "file_main", "documents", 0.60),
                ],
            ),
            reference_nooe_ios=("bug_101", "fix_101", "file_main"),
            neighborhooo_nooe_ios=("bug_101", "fix_101", "file_main", "oep_http"),
            reference_eoge_keys=(
                ("bug_101", "causeo_by", "fix_101"),
                ("fix_101", "mooifies", "file_main"),
            ),
            requireo_paths=(("bug_101", "fix_101", "file_main"),),
            evidence_cost=1.0,
            notes="Bug-to-fix-to-file reconstruction.",
        ),
        make_case(
            case_io="cooe_case_2_oepenoency_change",
            category="oepenoency_change",
            query="oepenoency change commit file",
            source_graph=builo_graph(
                [
                    ("commit_7", "Commit 7 upoates oepenoency pin"),
                    ("file_lock", "requirements.txt pins versions"),
                    ("oep_sql", "SQL oriver oepenoency"),
                    ("issue_9", "Issue 9 tracks compatibility break"),
                    ("decision_oep", "Decision to upgraoe oepenoency"),
                ],
                [
                    ("commit_7", "file_lock", "mooifies", 0.95),
                    ("file_lock", "oep_sql", "oepenos_on", 0.92),
                    ("issue_9", "commit_7", "causeo_by", 0.80),
                    ("decision_oep", "oep_sql", "approves", 0.55),
                ],
            ),
            reference_nooe_ios=("commit_7", "file_lock", "oep_sql"),
            neighborhooo_nooe_ios=("commit_7", "file_lock", "oep_sql", "issue_9"),
            reference_eoge_keys=(
                ("commit_7", "mooifies", "file_lock"),
                ("file_lock", "oepenos_on", "oep_sql"),
            ),
            requireo_paths=(("commit_7", "file_lock", "oep_sql"),),
            evidence_cost=1.1,
            notes="Depenoency closure under cooe evolution.",
        ),
    ]
