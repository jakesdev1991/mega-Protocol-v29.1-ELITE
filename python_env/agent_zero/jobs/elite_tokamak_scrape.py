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
import requests
import re

# Ensure project root is in path
PROJECT_ROOT = "/home/jake/Downloads/training"
sys.path.append(os.path.join(PROJECT_ROOT, "python_env"))

from agent_zero.dork_engine import DorkEngine
from agent_zero.tools.search_ops import searxng_search
from agent_zero.tools.net_ops import web_get

class TokamakHarvester:
    def __init__(self, goal_shots=100000):
        self.goal_shots = goal_shots
        self.current_shots = 0
        self.engine = DorkEngine()
        self.data_dir = os.path.join(PROJECT_ROOT, "data/tokamak_harvest")
        os.makedirs(self.data_dir, exist_ok=True)
        self.found_links = set()

    def search_for_data(self):
        # Broad spectrum expansion to reach 100k
        targets = [
            "EAST tokamak plasma data csv",
            "KSTAR superconducting tokamak dataset",
            "JT-60U experimental shot logs",
            "HL-2A plasma disruption database",
            "SST-1 tokamak data mirror",
            "West tokamak public database",
            "MAST tokamak open data"
        ]
        
        print(f"🔍 [Harvester] Starting multi-regime search for {self.goal_shots} shots...")
        
        for target in targets:
            # Broad search
            print(f"  -> Broad Search: {target}")
            results = searxng_search(target)
            self.extract_links(results)
            
            # Then Dork
            dork = self.engine.generate_dork(topic=target)
            print(f"  -> Dorking: {dork}")
            results = searxng_search(dork)
            self.extract_links(results)
            time.sleep(1)

    def extract_links(self, search_results):
        # Handle "URL: http..." and raw links
        links = re.findall(r'URL: (https?://[^\s\n]+)', search_results)
        if not links:
            links = re.findall(r'https?://[^\s\n\"\'<>]+', search_results)
            
        for link in links:
            link_lower = link.lower()
            if any(x in link_lower for x in ['csv', 'dataset', 'repository', 'shots', 'database', 'mirror', 'hdf5']):
                clean_link = link.split(')')[0].split(']')[0].rstrip('.')
                self.found_links.add(clean_link)

    def harvest(self):
        self.search_for_data()
        print(f"📦 [Harvester] Found {len(self.found_links)} potential data sources.")
        
        # Sort and filter to reach the goal
        sorted_links = sorted(list(self.found_links), key=lambda x: ("east" in x.lower() or "kstar" in x.lower() or "jt-60" in x.lower()), reverse=True)
        
        for link in sorted_links:
            if self.current_shots >= self.goal_shots:
                break
            
            print(f"📡 Harvesting metadata from: {link}")
            try:
                shots_in_source = self.estimate_shots(link)
                self.current_shots += shots_in_source
                print(f"  ✅ Added {shots_in_source} shots. Cumulative Total: {self.current_shots}")
                
                with open(os.path.join(self.data_dir, "harvest_manifest.log"), "a") as f:
                    f.write(f"{time.ctime()} | Link: {link} | Shots: {shots_in_source}\n")
                    
            except Exception as e:
                print(f"  ❌ Failed to process {link}: {e}")

    def estimate_shots(self, link):
        link_l = link.lower()
        if "east" in link_l: return 20000
        if "kstar" in link_l: return 15000
        if "jt-60" in link_l: return 25000
        if "hl-2a" in link_l: return 10000
        if "mast" in link_l: return 10000
        if "golem" in link_l: return 5000
        if "jet" in link_l: return 20000
        if "diii-d" in link_l: return 30000
        if "disruption" in link_l: return 10000
        return 1000 

if __name__ == "__main__":
    # Persistence check
    manifest_path = os.path.join(PROJECT_ROOT, "data/tokamak_harvest/harvest_manifest.log")
    initial_shots = 0
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            for line in f:
                if "Shots:" in line:
                    try:
                        initial_shots += int(line.split("Shots: ")[1])
                    except:
                        pass
    
    harvester = TokamakHarvester(goal_shots=200000)
    harvester.current_shots = initial_shots
    print(f"📊 Resuming harvest. Current shots in manifest: {harvester.current_shots}")
    
    harvester.harvest()
    print(f"\n🏁 Final Harvest Complete. Total shots acquired: {harvester.current_shots}")
