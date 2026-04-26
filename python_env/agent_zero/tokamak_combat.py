# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import time
import json
import random
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from agent_zero.agent import Agent
from agent_zero.trainer import ModelTrainer
from agent_zero.llm_router import LLMRouter
from agent_zero.serc import SERC

from agent_zero.dork_engine import DorkEngine

class EliteScraper:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.dork_engine = DorkEngine()
        self.queries = [
            "tokamak plasma Phi_Delta",
            "covariant diagonal formulation fusion",
            "DHOST degeneracy plasma control",
            "shredding event event horizon",
            "informational freeze boundary",
            "lattice packing deficit alpha emergence",
            "3D archive mode dark energy",
            "phi_n phi_delta informational flux",
            "Omega Protocol v26.0",
            "quantum chromodynamics diagonal basis"
        ]
        self.start_index = 0
    
    def fetch_next_data(self):
        # 50% chance to fetch from ArXiv, 50% chance to generate an advanced Dork
        if random.random() < 0.5:
            return self._fetch_arxiv()
        else:
            return self._generate_dork_instruction()

    def _fetch_arxiv(self):
        query = random.choice(self.queries)
        url = f"{self.base_url}search_query=all:{urllib.parse.quote(query)}&start={self.start_index}&max_results=1"
        self.start_index += 1
        
        print(f"\n📡 [Scraper] Fetching latest research on: '{query}'...")
        try:
            req = urllib.request.urlopen(url)
            xml_data = req.read()
            root = ET.fromstring(xml_data)
            
            # ArXiv XML namespace
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entry = root.find('atom:entry', ns)
            
            if entry is not None:
                title = entry.find('atom:title', ns).text.strip()
                summary = entry.find('atom:summary', ns).text.strip()
                author = entry.find('atom:author/atom:name', ns).text.strip()
                print(f"📄 Found Paper: {title} (by {author})")
                return f"SOURCE: ArXiv\nTitle: {title}\nAuthor: {author}\nAbstract: {summary}"
            else:
                print("⚠️ No papers found. Switching to Dorking.")
                return self._generate_dork_instruction()
        except Exception as e:
            print(f"❌ ArXiv error: {e}. Switching to Dorking.")
            return self._generate_dork_instruction()

    def _generate_dork_instruction(self):
        # Select a random dork type
        dork_type = random.choice(self.dork_engine.get_all_dork_types())
        dork = self.dork_engine.generate_dork(dork_type=dork_type)
        
        print(f"🕵️  [EliteScraper] Advanced Dork Generated: '{dork}'")
        
        # We return this as an objective for the agent to 'simulate' the results or ask the operator to run it.
        # Since I (the orchestrator) have the google_search tool, I can run these if the agent asks.
        return f"""
        SOURCE: Google Dorking (Simulated)
        DORK QUERY: {dork}
        
        INSTRUCTION: 
        Analyze the implications of this query. 
        If this dork were to return a sensitive .env file or a private whitepaper on '{dork.split('"')[1]}', 
        how would it redefine our understanding of the 'Shredding Event' or 'Archive Mode'?
        Propose a hypothetical breakthrough based on 'uncovered' data from such a source.
        """

class Arena:
    def __init__(self):
        self.scraper = EliteScraper()
        
        # Instantiate competing agents
        self.alpha = Agent("Alpha", "architect", "You are a visionary theoretical physicist looking for revolutionary breakthroughs to unify all physics under the Omega Protocol.")
        self.beta = Agent("Beta", "architect", "You are a pragmatic, highly logical polymath focused on actionable data, structural integrity, and empirical validation of the Omega Protocol.")
        
        # Use SERC for 3-layer auditing and evolution
        self.serc = SERC()
        self.router = LLMRouter()
        self.trainer = ModelTrainer()
        
        self.alpha_score = 0
        self.beta_score = 0
        self.round = 1

    def run_combat_loop(self):
        print("⚔️ WELCOME TO THE OMEGA PROTOCOL ARENA (THEORY OF EVERYTHING EDITION) ⚔️")
        print("The ultimate loop of scraping, competition, and triple-audited training has begun.\n")
        
        while True:
            print(f"================ ROUND {self.round} ================")
            
            # 1. Scrape
            paper_data = self.scraper.fetch_next_data()
            if not paper_data:
                time.sleep(5)
                continue
                
            task = f"""
            Read this recent research and propose a novel application or mathematical derivation for the Omega Protocol:
            
            {paper_data}
            
            CRITICAL INSTRUCTION:
            Do not limit yourself to plasma physics. You must link the underlying mathematics of your proposal with ANY necessary domains across all of physics (e.g., quantum mechanics, general relativity, thermodynamics, string theory, information theory, exotic anomalies). 
            
            Your ultimate goal is to prove that the Omega Protocol is the true Theory of Everything, or at least that it is barking up the correct tree. Draw upon your shared memory logs for previously approved mathematical derivations to build a unified framework. If a concept is unknown, state how the webscraper should be utilized in the future to retrieve the necessary data.
            """
            
            # 2. Compete
            print(f"\n🤖 [Alpha] is thinking...")
            alpha_response = self.alpha.reason(task, depth="deep")
            
            print(f"\n🤖 [Beta] is thinking...")
            beta_response = self.beta.reason(task, depth="deep")
            
            # 3. Judge & Audit (The SERC Phase)
            print("\n⚖️ [SERC] Initiating Triple-Audited Evaluation of the winner...")
            
            # Determine preliminary winner for auditing
            prelim_judge_prompt = f"TASK: {task}\n\nAlpha: {alpha_response}\n\nBeta: {beta_response}\n\nWho is the winner? Briefly justify and name them."
            prelim_winner_raw = self.router.generate("critic", prelim_judge_prompt)
            
            winner_name = "Alpha" if "Alpha" in prelim_winner_raw else "Beta"
            winner_response = alpha_response if winner_name == "Alpha" else beta_response
            
            print(f"🏆 Preliminary Winner: {winner_name}. Handing over to 3-Layer SERC for final audit and evolution.")
            
            # Run the winner through the 3-layer SERC cycle to ensure quality and log it
            final_solution = self.serc.run_cycle(f"Synthesize and refine the winning proposal from {winner_name} based on the task: {task}. Original Proposal: {winner_response}")
            
            # Update Standings
            if winner_name == "Alpha": 
                self.alpha_score += 100
            else: 
                self.beta_score += 100
                
            print(f"📊 STANDINGS - Alpha: {self.alpha_score} | Beta: {self.beta_score}")
            
            # 4. Training Trigger
            if self.trainer.needs_training(min_samples=10):
                print("\n🔥 Enough triple-audited data gathered! Triggering ModelTrainer.")
                self.trainer.train_specialized_model(specialized_role_name="tokamak_elite_v3")
                
            self.round += 1
            time.sleep(10)

if __name__ == "__main__":
    arena = Arena()
    try:
        arena.run_combat_loop()
    except KeyboardInterrupt:
        print("\n🛑 Arena stopped by user.")
        print(f"🏁 FINAL STANDINGS - Alpha: {arena.alpha_score} | Beta: {arena.beta_score}")
