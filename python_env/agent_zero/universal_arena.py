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

class UniversalScraper:
    def __init__(self):
        self.base_url = "http://export.arxiv.org/api/query?"
        self.dork_engine = DorkEngine()
        self.branches = {
            "tokamak": [
                "tokamak plasma Phi_Delta",
                "covariant diagonal formulation fusion",
                "DHOST degeneracy plasma control"
            ],
            "omega_physics": [
                "shredding event event horizon",
                "informational freeze boundary",
                "lattice packing deficit alpha emergence",
                "phi_n phi_delta informational flux"
            ],
            "business": [
                "GPU cost reduction enterprise data",
                "B2B AI sales automation trends 2026",
                "decentralized compute market growth",
                "KTH Live-in Lab PV-BESS optimization",
                "multi-market energy trading strategies"
            ],
            "finance": [
                "HFT causal inference market regime",
                "algorithmic trading topological data analysis",
                "crypto market liquidity anomalies",
                "real-time electricity pricing RTP arbitrage",
                "Levelized Cost of Storage LCOS trends 2026"
            ],
            "biology": [
                "synthetic biology universal metabolism",
                "topological invariants protein folding",
                "bio-topology gene regulatory networks"
            ],
            "psychology": [
                "Q-Systemic Self informational geometry",
                "trauma-induced cognitive architecture phase transition",
                "Asperger's syndrome superior abstract reasoning synthesis",
                "quantum subconscious MWI interpretations",
                "Jungian shadow self systemic integration"
            ]
        }
        self.start_indexes = {k: 0 for k in self.branches.keys()}
    
    def fetch_next_data(self):
        branch = random.choice(list(self.branches.keys()))
        # 50% chance to fetch from ArXiv, 50% chance to generate an advanced Dork
        if random.random() < 0.5:
            return self._fetch_arxiv(branch), branch
        else:
            return self._generate_dork_instruction(branch), branch

    def _fetch_arxiv(self, branch):
        query = random.choice(self.branches[branch])
        url = f"{self.base_url}search_query=all:{urllib.parse.quote(query)}&start={self.start_indexes[branch]}&max_results=1"
        self.start_indexes[branch] += 1
        
        print(f"\n📡 [Scraper] [{branch.upper()}] Fetching research on: '{query}'...")
        try:
            req = urllib.request.urlopen(url)
            xml_data = req.read()
            root = ET.fromstring(xml_data)
            
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entry = root.find('atom:entry', ns)
            
            if entry is not None:
                title = entry.find('atom:title', ns).text.strip()
                summary = entry.find('atom:summary', ns).text.strip()
                author = entry.find('atom:author/atom:name', ns).text.strip()
                return f"SOURCE: ArXiv\nBranch: {branch}\nTitle: {title}\nAuthor: {author}\nAbstract: {summary}"
            else:
                return self._generate_dork_instruction(branch)
        except Exception:
            return self._generate_dork_instruction(branch)

    def _generate_dork_instruction(self, branch):
        dork_type = random.choice(self.dork_engine.get_all_dork_types())
        # Use the first keyword of the branch for the dork query
        keyword = self.branches[branch][0].split()[0]
        dork = self.dork_engine.generate_dork(dork_type=dork_type)
        
        print(f"🕵️  [UniversalScraper] [{branch.upper()}] Dork Generated: '{dork}'")
        return f"""
        SOURCE: Google Dorking (Simulated)
        Branch: {branch}
        DORK QUERY: {dork}
        
        INSTRUCTION: 
        Analyze the implications of this query in the context of {branch}. 
        Propose a breakthrough or insight based on hypothetical data from such a source.
        """

class UniversalArena:
    def __init__(self):
        self.scraper = UniversalScraper()
        self.alpha = Agent("Alpha", "architect", "Visionary specialist.")
        self.beta = Agent("Beta", "architect", "Pragmatic logic specialist.")
        self.neo = Agent("Neo", "architect", "The Anomaly. You propose disruptive, non-linear integrations that shatter conventional paradigms.")
        self.smith = Agent("Smith", "critic", "The Matrix Guardian (Anti-Agency). You ruthlessly audit proposals for weakness, eliminate flaws, and select the ultimate survivor.")
        self.serc = SERC()
        self.router = LLMRouter()
        self.trainer = ModelTrainer()
        self.scores = {"Alpha": 0, "Beta": 0, "Neo": 0}
        self.round = 1

    def run_universal_loop(self):
        print("⚔️ UNIVERSAL OMEGA ARENA: ALL BRANCHES ACTIVE ⚔️\n")
        
        while True:
            print(f"================ ROUND {self.round} ================")
            
            # 1. Scrape
            data, branch = self.scraper.fetch_next_data()
            task = f"BRANCH: {branch}\nDATA: {data}\n\nPropose a novel integration with the Omega Protocol."
            
            # 2. Compete
            a_res = self.alpha.reason(task, depth="deep")
            b_res = self.beta.reason(task, depth="deep")
            n_res = self.neo.reason(task, depth="deep")
            
            # 3. Judge (Agent Smith)
            judge_prompt = f"TASK: {task}\n\nAlpha: {a_res}\n\nBeta: {b_res}\n\nNeo: {n_res}\n\nAs Agent Smith, who survives this round? Select ONLY 'Alpha', 'Beta', or 'Neo' as the winner, and state your ruthless logic."
            judge_out = self.smith.reason(judge_prompt)
            
            if "Neo" in judge_out:
                winner = "Neo"
                winner_res = n_res
            elif "Alpha" in judge_out:
                winner = "Alpha"
                winner_res = a_res
            else:
                winner = "Beta"
                winner_res = b_res
                
            self.scores[winner] += 1
            
            print(f"🏆 Round Winner (Decided by Smith): {winner} ({branch}) | Scores: {self.scores}")
            
            # 4. Triple-Audit (SERC)
            final_sol = self.serc.run_cycle(f"Refine {winner}'s {branch} proposal: {winner_res}")
            
            # 5. Training
            if self.trainer.needs_training(min_samples=10):
                self.trainer.train_specialized_model(f"{branch}_specialist_v3")
                
            self.round += 1
            time.sleep(300)

if __name__ == "__main__":
    arena = UniversalArena()
    arena.run_universal_loop()
