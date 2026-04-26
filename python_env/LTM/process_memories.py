# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sqlite3
import json
import logging
import requests
import numpy as np
from typing import List, Tuple, Optional, Dict, Any

import os
import sys

# Ensure both python_env and root are in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from configs.config import config
from utils.logger import logger

DB_PATH = config.ltm_dir / 'memories.db'
EMBEDDING_MODEL = config.ltm_embedding
OLLAMA_URL = config.ollama_embed_url

# Initialize requests session for connection pooling
session = requests.Session()

def init_db():
    """Ensure the table exists."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                vector_data TEXT NOT NULL,
                metadata TEXT
            )
        ''')
        conn.commit()

# Call once to ensure table
init_db()

def get_qwen_embedding(text: str) -> Optional[List[float]]:
    """Generates an embedding vector using the local Ollama API."""
    try:
        payload = {
            "model": EMBEDDING_MODEL,
            "prompt": text,
            "options": {
                "num_thread": 12,
                "num_ctx": 32768
            }
        }
        response = session.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("embedding")
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error generating embedding: {e}")
    except Exception as e:
        logger.error(f"Unexpected error generating embedding: {e}")
    return None

def store_memory(content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """Embeds and stores a new memory continuously reusing sqlite connect context."""
    vector = get_qwen_embedding(content)
    if not vector:
        logger.warning("Aborted storing memory due to failed embedding.")
        return False

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO local_memories (content, vector_data, metadata) VALUES (?, ?, ?)",
                (content, json.dumps(vector), json.dumps(metadata) if metadata else None)
            )
            conn.commit()
        logger.info(f"✅ Memory stored successfully: {content[:50]}...")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error while storing memory: {e}")
        return False

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculates cosine similarity between two vectors."""
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm_v1 * norm_v2))

def search_memories(query: str, limit: int = 3) -> str:
    """Performs a semantic search in the local database."""
    query_vector = get_qwen_embedding(query)
    if not query_vector:
        error_msg = "Search failed: Error generating embedding for query."
        logger.error(error_msg)
        return error_msg

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content, vector_data FROM local_memories")
            rows = cursor.fetchall()
            
        if not rows:
            return "No memories found in the database."

        q_vec = np.array(query_vector)
        results = []
        
        for content, vector_str in rows:
            vector = np.array(json.loads(vector_str))
            score = cosine_similarity(q_vec, vector)
            results.append((content, score))

        # Sort by similarity score descending
        results.sort(key=lambda x: x[1], reverse=True)
        top_results = results[:limit]
        
        return "\n---\n".join([f"[Score: {s:.4f}] {c}" for c, s in top_results])

    except sqlite3.Error as e:
        logger.error(f"Database query error: {e}")
        return "Search failed due to internal database error."

if __name__ == "__main__":
    # Test example
    logger.info("Seeding test memory...")
    store_memory("The user prefers Vanilla CSS over TailwindCSS.")
    logger.info("Searching for 'UI styling'...")
    logger.info(f"\n{search_memories('UI styling')}")
