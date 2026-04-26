# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import json
import time
from datetime import datetime

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from agent_zero.serc import SERC
from business.sales_automation_engine import OmegaSalesEngine

class FreelanceScoutJob:
    """
    Freelance Scout: Advanced dorking and sentiment analysis for revenue generation.
    Targets custom software builds, data extraction, and automation services.
    """
    def __init__(self):
        self.serc = SERC()
        self.sales_engine = OmegaSalesEngine()
        self.knowledge_dir = os.path.join(PROJECT_ROOT, "python_env", "agent_zero", "knowledge")
        self.leads_path = os.path.join(self.knowledge_dir, "freelance_leads.jsonl")
        os.makedirs(self.knowledge_dir, exist_ok=True)

    def run_scout_cycle(self):
        print(f"💰 [FreelanceScout] Initiating revenue discovery cycle...")
        
        # Advanced Dorking Directives
        dorks = [
            'site:github.com "wanted" "paid" "bounty" (automation OR "data extraction")',
            'site:upwork.com/jobs "custom build" "long-term" (python OR "agentic")',
            'site:reddit.com/r/freelance_forhire "hiring" (scraper OR "automation")',
            'intitle:"index of" "config.php" (implies unprotected infrastructure needing repair)',
            '"looking for a developer" "urgent" "extraction" -job -careers'
        ]
        
        directive = f"""
        FREELANCE SCOUT DIRECTIVE: Identify High-Value Revenue Opportunities.

        PHASE 1: ADVANCED DORKING
        Analyze the following search intents:
        {json.dumps(dorks, indent=2)}

        PHASE 2: SENTIMENT & URGENCY ANALYSIS
        For each potential lead, evaluate:
        1. Urgency Score (0-1.0): Based on keywords like "urgent", "ASAP", "frustrated", "deadline".
        2. Budget Sentiment (0-1.0): Based on "paid", "bounty", "long-term", "enterprise".
        3. Technical Fit: Matches Omega Protocol strengths (RCOD, Data Extraction, Agentic Flows).

        PHASE 3: LEAD QUALIFICATION
        Filter for opportunities where Sentiment > 0.7 and Urgency > 0.6.

        OUTPUT FORMAT:
        Return a JSON array of Qualified Leads:
        [
          {{
            "source": "Platform/URL",
            "opportunity": "Description of the need",
            "sentiment_score": 0.85,
            "urgency_score": 0.9,
            "contact_hint": "How to reach them",
            "suggested_pitch": "Why Omega Protocol is the solution"
          }}
        ]
        """

        try:
            # Execute the reasoning cycle
            print("🧠 [FreelanceScout] Analyzing manifold for opportunities...")
            result = self.serc.run_cycle(directive)
            
            # Extract JSON from the SERC output
            leads = self._extract_leads(result)
            
            for lead in leads:
                print(f"💎 Found Opportunity: {lead['opportunity'][:50]}... (S:{lead['sentiment_score']}|U:{lead['urgency_score']})")
                self.sales_engine.add_lead_to_crm(
                    company=lead.get("source", "Web Lead"),
                    contact=lead.get("contact_hint", "Unknown"),
                    status="Qualified (Scraped)"
                )
                
                # Append to persistent storage
                with open(self.leads_path, "a") as f:
                    f.write(json.dumps(lead) + "\n")

            print(f"✅ [FreelanceScout] Cycle complete. {len(leads)} leads qualified.")
            return leads

        except Exception as e:
            print(f"❌ [FreelanceScout] Error: {e}")
            return []

    def _extract_leads(self, text):
        import re
        # Attempt to find JSON array
        match = re.search(r"\[\s*\{.*\}\s*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        return []

if __name__ == "__main__":
    scout = FreelanceScoutJob()
    scout.run_scout_cycle()
