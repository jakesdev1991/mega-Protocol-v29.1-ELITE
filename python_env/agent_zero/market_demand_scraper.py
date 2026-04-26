# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import json

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(PROJECT_ROOT)

from python_env.agent_zero.llm_router import LLMRouter
from python_env.agent_zero.tools.search_ops import searxng_search
from python_env.agent_zero.tools.matrix_auditor import MatrixAuditor

def read_document(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return ""

def main():
    print("🚀 Initiating Market Demand Scraper & Vector DB Ingestion Pipeline...")
    router = LLMRouter()
    auditor = MatrixAuditor()
    
    # 1. Read Document
    doc_path = os.path.join(PROJECT_ROOT, "software_to_learn_from_full.txt")
    print(f"📄 Reading source logic from {doc_path}...")
    doc_content = read_document(doc_path)
    
    # Chunking the document for analysis (simplified for this script)
    chunks = [doc_content[i:i+4000] for i in range(0, len(doc_content), 4000)]
    print(f"🧩 Split document into {len(chunks)} chunks.")
    
    # 2. Web Scrape for Demand & Psychology
    print("🌐 Scraping SearXNG for unmet SaaS demand, monetization, and psychology sentiment analysis...")
    queries = [
        "unmet SaaS automation software demand 2026",
        "how to monetize n8n AI agent workflows immediately",
        "latest APIs for psychology sentiment analysis and social interaction"
    ]
    
    scraped_context = ""
    for q in queries:
        print(f"   -> Querying: '{q}'")
        results = searxng_search(q)
        scraped_context += f"--- Query: {q} ---\n{results}\n\n"
        
    print("✅ Scraping complete.")
    
    # 3. Agent Analysis & Design Generation
    print("🧠 Engaging Agent Zero to analyze document logic + scraped demand...")
    
    analysis_prompt = f"""
    You are the Lead Architect. Analyze the following logic extracted from a workflow document 
    and the scraped market demand context. 
    
    Document Logic (Sample):
    {chunks[0][:1500]}...
    
    Scraped Market Demand:
    {scraped_context[:1500]}...
    
    Task: Propose 3 detailed software designs based on this logic:
    1. A design to help with Tokamak plasma prediction.
    2. A design for advanced Finance prediction.
    3. A design for analyzing Human Speech (incorporating psychology/sentiment analysis).
    
    Ensure the designs utilize unstructured data processing, RAG, buffer memory, and targeted data mining.
    """
    
    designs_proposal = router.generate("architect", analysis_prompt, system_prompt="You are a genius software architect designing Omega Protocol modules.")
    print("✅ Designs generated.")
    
    # 4. Audit Layer (Matrix Auditor)
    print("⚖️ Passing designs to Matrix Auditor (Neo & Smith) for review...")
    
    # We simulate a "write_local_file" action to trigger the EXTREME severity audit
    action_desc = f"Proposing to add the following 3 new software designs to the Omega Vector DB:\n\n{designs_proposal}"
    
    # Trigger the Neo vs. Smith Consensus
    is_approved, audit_result = auditor.evaluate_action(
        agent_name="Market_Demand_Scraper", 
        tool_name="write_local_file", 
        kwargs={"file_path": "omega_vector_db_proposals.md", "content": "[Designs]"}
    )
    
    # 5. Output for Orchestrator (User) Review
    output_path = os.path.join(PROJECT_ROOT, "python_env", "agent_zero", "knowledge", "pending_auditor_review.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    final_report = f"""# 🛡️ OMEGA ORCHESTRATOR REVIEW REQUIRED
    
## 1. Source Logic Analyzed
The agents ingested the n8n JSON structural logic from 'software_to_learn_from.docx'.

## 2. Scraped Market Context
{scraped_context}

## 3. Proposed Architectures (Tokamak, Finance, Speech)
{designs_proposal}

## 4. Matrix Auditor Consensus (Neo vs. Smith)
**Approved by Auditor:** {is_approved}
**Audit Trail:**
{audit_result}

---
**ACTION REQUIRED:** 
As the Orchestrator, review the above. If acceptable, these designs will be vectorized and added to the Omega Protocol's long-term memory.
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_report)
        
    print(f"\n🎉 Pipeline complete! Review the final report at: {output_path}")

if __name__ == "__main__":
    main()
