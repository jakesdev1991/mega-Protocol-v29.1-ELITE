# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import requests
import json
import csv
from datetime import date

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from business.sales_automation_engine import OmegaSalesEngine
from utils.nvidia_client import NvidiaClient

class LeadScraperJob:
    """
    Job that harvests leads (Companies + C-Suite/VP contacts) for the Omega Protocol.
    Focused on AI Infrastructure & Cloud providers.
    """
    
    def __init__(self):
        self.sales_engine = OmegaSalesEngine()
        self.nvidia = NvidiaClient()
        self.target_industries = ["Google DeepMind", "Google AI", "OpenAI", "Anthropic", "Meta AI"]
        self.target_roles = ["CTO", "VP Engineering", "Chief AI Officer", "CEO"]

    def _generate_search_queries(self):
        """Builds a list of search queries to find target companies and people."""
        queries = []
        for industry in self.target_industries:
            for role in self.target_roles:
                queries.append(f"{industry} companies {role} LinkedIn")
                queries.append(f"List of {industry} providers 2026")
        return queries

    def harvest_leads(self, max_leads=10):
        print(f"🕵️  [LeadScraper] Starting harvest for {max_leads} leads...")
        
        # In a real-world scenario, we'd use a Google Search API or Scraper.
        # Here we simulate the 'scraping' by using the LLM to 'propose' valid targets based on latest industry knowledge.
        
        prompt = f"""
        Objective: Identify 10 real-world or high-probability 'AI Infrastructure & Cloud' companies 
        likely to have massive GPU clusters (e.g., CoreWeave, Lambda Labs, Crusoe Energy, etc.).
        
        For each company, identify the likely {', '.join(self.target_roles)} and their approximate LinkedIn profile focus.
        
        Return ONLY a JSON array of objects:
        [
          {{"company": "CompanyName", "contact": "Name (Title)", "reason": "Why they need Omega Protocol"}}
        ]
        """
        
        try:
            raw_response = self.nvidia.chat("mistral-large", prompt, "You are a lead generation specialist.")
            
            # Extract JSON from markdown if needed
            if "```json" in raw_response:
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            elif "[" in raw_response:
                raw_response = raw_response[raw_response.find("["):raw_response.rfind("]")+1]
            
            leads = json.loads(raw_response)
            
            count = 0
            for lead in leads:
                if count >= max_leads: break
                
                company = lead.get("company", "Unknown")
                contact = lead.get("contact", "Unknown")
                
                print(f"➕ Found: {company} | {contact}")
                self.sales_engine.add_lead_to_crm(company, contact, status="New (Scraped)")
                count += 1
                
            print(f"✅ Harvest Complete. {count} leads added to CRM.")
            return leads
            
        except Exception as e:
            print(f"❌ Error during lead harvest: {e}")
            return []

if __name__ == "__main__":
    job = LeadScraperJob()
    job.harvest_leads(max_leads=5)
