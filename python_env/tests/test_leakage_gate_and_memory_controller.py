# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from LTM.memory_management import SamsonMemoryController
from agent_zero.tools.search_ops import SearxngSearchAdapter
from rcod.leakage_gate import ZScoreLeakageGate, lexical_overlap


class FakeAgent:
    def reason(self, prompt):
        return "archival summary"


class FakeResponse:
    status_code = 200

    def raise_for_status(self):
        return None

    def json(self):
        return {
            "results": [
                {"title": "Omega overview", "url": "https://example.test/a", "content": "brief context"},
                {"title": "Other note", "url": "https://example.test/b", "content": "unrelated material"},
            ]
        }


class FakeClient:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get(self, url, params=None, timeout=None):
        self.url = url
        self.params = params
        self.timeout = timeout
        return FakeResponse()


class LeakageGateTests(unittest.TestCase):
    def test_lexical_overlap_bounds_and_matches_tokens(self):
        score = lexical_overlap("alpha beta gamma", "beta gamma delta")
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_gate_blocks_absolute_overlap(self):
        gate = ZScoreLeakageGate(absolute_threshold=0.5)
        decision = gate.evaluate_text("alpha beta", "alpha beta")
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "absolute-threshold")


class SearchAdapterTests(unittest.TestCase):
    def test_adapter_normalizes_http_results(self):
        with patch("agent_zero.tools.search_ops.httpx.Client", return_value=FakeClient()):
            results = SearxngSearchAdapter(base_url="http://searx.test", max_results=2).search("omega")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].title, "Omega overview")
        self.assertIn("Leakage:", results[0].render())


class SamsonMemoryControllerTests(unittest.TestCase):
    def test_build_report_detects_redundant_vectors(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            db_path = tmp / "memories.db"
            knowledge_dir = tmp / "knowledge"
            knowledge_dir.mkdir()
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    "CREATE TABLE local_memories (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, vector_data TEXT)"
                )
                conn.execute(
                    "INSERT INTO local_memories (content, vector_data) VALUES (?, ?)",
                    ("first", json.dumps([1.0, 0.0])),
                )
                conn.execute(
                    "INSERT INTO local_memories (content, vector_data) VALUES (?, ?)",
                    ("duplicate", json.dumps([1.0, 0.0])),
                )
                conn.execute(
                    "INSERT INTO local_memories (content, vector_data) VALUES (?, ?)",
                    ("different", json.dumps([0.0, 1.0])),
                )

            controller = SamsonMemoryController(
                db_path=db_path,
                knowledge_dir=knowledge_dir,
                old_memory_window=50,
                finance_agent=FakeAgent(),
            )
            report = controller.build_report()

        self.assertEqual(report["db_optimization"]["total_entries"], 3)
        self.assertEqual(report["db_optimization"]["redundant_ids"], [2])


if __name__ == "__main__":
    unittest.main()
