# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sqlite3
import json
import os
import sys
import numpy as np
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from LTM.process_memories import DB_PATH, cosine_similarity, store_memory
from finance.finance_agent import FinanceAgent

class MemoryManagement:
    """
    RCOD-based Global Manifold Janitor.
    Identifies redundant memories, compresses old info across DB and logs, 
    and keeps the entire Omega repository lean.
    """
    def __init__(self, redundancy_threshold=0.94):
        self.threshold = redundancy_threshold
        self.agent = FinanceAgent("Omega-Janitor")
        self.knowledge_dir = os.path.join(PROJECT_ROOT, "agent_zero", "knowledge")

    def scan_log_redundancy(self):
        """Scans for redundant or oversized .jsonl logs."""
        logs = [f for f in os.listdir(self.knowledge_dir) if f.endswith(".jsonl")]
        redundant_logs = []
        for log in logs:
            path = os.path.join(self.knowledge_dir, log)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            if size_mb > 10.0: # Arbitrary 10MB limit for active logs
                redundant_logs.append({"file": log, "size_mb": round(size_mb, 2), "action": "compress"})
        return redundant_logs

    def run_epoch(self):
        print("🧹 [Memory Management] Performing global manifold sweep...")
        
        # 1. Database Sweep
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content, vector_data FROM local_memories")
                rows = cursor.fetchall()
        except Exception as e:
            print(f"Error accessing DB: {e}")
            rows = []

        db_redundancies = []
        old_memories = []
        
        if len(rows) > 2:
            vectors = [np.array(json.loads(r[2])) for r in rows]
            for i in range(len(rows)):
                if rows[i][0] in [r['id'] for r in db_redundancies]: continue
                
                # Check for age (simulated by row ID)
                if i < len(rows) - 50: # The first memories are 'old'
                    old_memories.append(rows[i][1])
                
                for j in range(i + 1, len(rows)):
                    score = cosine_similarity(vectors[i], vectors[j])
                    if score > self.threshold:
                        db_redundancies.append({"id": rows[j][0], "content": rows[j][1][:50] + "..."})

        # 2. Summarization of Old Manifold State
        summary = ""
        if len(old_memories) > 10:
            print(f"🧠 [Janitor] Summarizing {len(old_memories)} old memories into a single epoch constant...")
            prompt = f"Summarize the following old memories into a single, high-density informational constant for the Omega Protocol. Retain all technical derivations and approved insights but remove conversational noise:\n\n" + "\n".join(old_memories[:20])
            summary = self.agent.reason(prompt)

        # 3. Log Sweep
        log_plan = self.scan_log_redundancy()

        # 4. Final Compression Plan
        report = {
            "scope": "DIRECTORY-WIDE",
            "db_optimization": {
                "total_entries": len(rows),
                "redundant_ids": [r['id'] for r in db_redundancies],
                "old_memories_compressed": len(old_memories[:20]),
                "new_archival_constant": summary[:200] + "..." if summary else "None"
            },
            "log_optimization": log_plan,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        print("--- BEGIN PROPOSED LEARNING ---")
        print(json.dumps(report, indent=2))
        print("--- END PROPOSED LEARNING ---")

if __name__ == "__main__":
    mm = MemoryManagement()
    mm.run_epoch()
