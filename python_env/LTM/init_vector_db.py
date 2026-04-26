# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import sqlite3
import os
import json

# Configuration
DB_DIR = r'C:\Users\Jakesdev1991\Downloads\training\LTM'
DB_PATH = os.path.join(DB_DIR, 'memories.db')

def setup_vector_db():
    """Initializes the SQLite database for storing memories."""
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table for text and the vector
    # We store the vector as a TEXT (JSON string) for simplicity without external extensions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS local_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            vector_data TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at: {DB_PATH}")

if __name__ == "__main__":
    setup_vector_db()
