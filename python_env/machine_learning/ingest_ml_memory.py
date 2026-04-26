# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import glob

# Ensure project root and python_env are in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "python_env"))

from python_env.LTM.qdrant_memory import QdrantMemorySystem

def ingest_ml_docs():
    """
    Reads all markdown files in the machine_learning directory and ingests them
    into the Qdrant working memory system.
    """
    qms = QdrantMemorySystem()
    ml_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Find all markdown files in the directory and subdirectories
    md_files = glob.glob(os.path.join(ml_dir, "**", "*.md"), recursive=True)
    
    print(f"Found {len(md_files)} Machine Learning documentation files.")
    
    for file_path in md_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Use the relative path as the document name for metadata
        rel_path = os.path.relpath(file_path, ml_dir)
        category = os.path.dirname(rel_path)
        if not category:
            category = "general"
            
        metadata = {
            "branch": "machine_learning",
            "category": category,
            "file_name": os.path.basename(file_path),
            "type": "theory_and_workflow"
        }
        
        print(f"Ingesting: {rel_path} into Working Memory...")
        success = qms.add_memory(content, metadata)
        
        if success:
            print(f"✅ Successfully added {rel_path} to Qdrant.")
        else:
            print(f"❌ Failed to add {rel_path} to Qdrant.")

if __name__ == "__main__":
    print("--- OMEGA PROTOCOL: ML Memory Ingestion ---")
    ingest_ml_docs()
    print("--- Ingestion Complete ---")
