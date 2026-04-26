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
from tqdm import tqdm

# Ensure project root and python_env are in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from python_env.LTM.qdrant_memory import QdrantMemorySystem
from configs.config import config
from utils.logger import logger

DB_PATH = config.ltm_dir / 'memories.db'

def migrate():
    if not os.path.exists(DB_PATH):
        logger.error(f"SQLite database not found at {DB_PATH}")
        return

    logger.info(f"Starting migration from {DB_PATH} to Qdrant...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT content, metadata FROM local_memories")
        rows = cursor.fetchall()
        
        if not rows:
            logger.info("No memories to migrate.")
            return

        qms = QdrantMemorySystem()
        
        for content, metadata_str in tqdm(rows, desc="Migrating memories"):
            metadata = json.loads(metadata_str) if metadata_str else {}
            qms.add_memory(content, metadata)
            
        logger.info(f"✅ Migration complete. {len(rows)} memories ported to Qdrant.")
        conn.close()
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
