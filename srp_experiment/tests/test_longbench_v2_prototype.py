import json
import tempfile
import unittest
from pathlib import Path

from srp_experiment.data.longbench_v2.import_longbench_v2 import build_query, tokenize_keywords, transform_row
from srp_experiment.data.longbench_v2 import split_task_groups


class TestLongBenchV2Prototype(unittest.TestCase):
    def test_transform_row_builds_frozen_long_context_task(self):
        row = {
            "_id": "row-001",
            "question": "Which option is correct?",
            "choice_A": "Alpha",
            "choice_B": "Beta",
            "choice_C": "Gamma",
            "choice_D": "Delta",
            "answer": "B",
            "context": "A long benchmark context.",
            "domain": "qa",
            "sub_domain": "mcq",
            "difficulty": "easy",
            "length": 1234,
        }

        task = transform_row(row)

        self.assertEqual(task["id"], "longbench_v2::row-001")
        self.assertEqual(task["task_type"], "long_context_mcq")
        self.assertEqual(task["source"], "LongBench v2")
        self.assertEqual(task["initial_state"]["memory"], "A long benchmark context.")
        self.assertEqual(task["expected_output"]["answer_letter"], "B")
        self.assertEqual(task["expected_output"]["answer_text"], "Beta")
        self.assertIn("preserve benchmark context", task["initial_state"]["constraints"])
        self.assertIn("answer-critical evidence", " ".join(task["initial_state"]["constraints"]))
        self.assertIn("B. Beta", task["queries"][0])
        self.assertEqual(task["query_expectations"], [[["B", "Beta"]]])
        self.assertEqual(task["metadata"]["benchmark"], "LongBench v2")
        self.assertEqual(task["metadata"]["source_id"], "row-001")

    def test_build_query_and_keyword_tokenization_are_stable(self):
        query = build_query(
            "What is the answer?",
            {"A": "Alpha", "B": "Beta", "C": "Gamma", "D": "Delta"},
        )
        keywords = tokenize_keywords("What is the answer?", "Beta option")

        self.assertIn("Options:", query)
        self.assertIn("A. Alpha", query)
        self.assertIn("Answer with the correct option letter", query)
        self.assertEqual(keywords, ["beta"])

    def test_split_task_groups_writes_frozen_subsets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            source_path = tmp_path / "tasks.json"
            source_payload = {
                "benchmark": "LongBench v2",
                "tasks": [
                    {"id": "task-1"},
                    {"id": "task-2"},
                    {"id": "task-3"},
                ],
            }
            source_path.write_text(json.dumps(source_payload, indent=2), encoding="utf-8")

            previous_root = split_task_groups.ROOT
            previous_source = split_task_groups.SOURCE_PATH
            previous_group_size = split_task_groups.GROUP_SIZE
            try:
                split_task_groups.ROOT = tmp_path
                split_task_groups.SOURCE_PATH = source_path
                split_task_groups.GROUP_SIZE = 2
                exit_code = split_task_groups.main()
                self.assertEqual(exit_code, 0)

                group_1 = json.loads((tmp_path / "tasks_group_1.json").read_text(encoding="utf-8"))
                group_2 = json.loads((tmp_path / "tasks_group_2.json").read_text(encoding="utf-8"))
                self.assertEqual(group_1["group_name"], "group_1")
                self.assertEqual(group_2["group_name"], "group_2")
                self.assertEqual(len(group_1["tasks"]), 2)
                self.assertEqual(len(group_2["tasks"]), 1)
            finally:
                split_task_groups.ROOT = previous_root
                split_task_groups.SOURCE_PATH = previous_source
                split_task_groups.GROUP_SIZE = previous_group_size


if __name__ == "__main__":
    unittest.main()
