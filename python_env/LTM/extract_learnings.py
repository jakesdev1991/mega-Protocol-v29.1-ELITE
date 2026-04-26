# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sqlite3
import os

DB_PATH = 'C:/Users/Jakesdev1991/Downloads/training/LTM/memories.db'

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: DB not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Pull all learnings and recent technical insights
        cursor.execute("SELECT content FROM local_memories WHERE content LIKE 'LEARNING%'")
        learnings = cursor.fetchall()
        
        for r in learnings:
            print("--- ENTRY START ---")
            print(r[0])
            print("--- ENTRY END ---")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
