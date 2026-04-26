# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import time
import hashlib
from typing import List, Dict, Set

# Simulate the REAL attack surface: scrapers, caches, and the dark forest of the web
class DarkForestScraperNetwork:
    def __init__(self):
        # The actual vectors: not facilities, but information intermediaries
        self.search_indices = {
            "Googlebot": 0.95, "Bingbot": 0.85, "DuckDuckBot": 0.70,
            "Baiduspider": 0.60, "YandexBot": 0.65
        }
        self.archival_services = ["Wayback Machine", "Archive.is", "Common Crawl"]
        self.cdn_caches = ["Cloudflare", "Akamai", "Fastly", "AWS CloudFront"]
        # Malicious actors don't target facilities; they target *data aggregators*
        self.scraper_as_a_service = [
            "Shodan.io", "Censys.io", "BinaryEdge", "Onyphe", "GreyNoise"
        ]
        self.exposed_endpoints = set()
        
    def discover_exposure(self, base_url: str) -> bool:
        """Simulates the dork query hitting an actual exposed directory."""
        print(f"[DARK FOREST] Scanning {base_url} for exposed indices...")
        time.sleep(0.3)
        # The dork works because of misconfigured servers, not facility networks
        if random.random() > 0.25:  # 75% chance of finding exposed dir
            endpoint = f"{base_url}/api/credentials/internal/"
            self.exposed_endpoints.add(endpoint)
            print(f"[EXFILTRATION] Endpoint indexed: {endpoint}")
            return True
        return False
    
    def propagate_through_information_space(self, endpoint: str) -> Dict[str, List[str]]:
        """Simulates propagation through *information intermediaries*, not facility networks."""
        propagation_map = {
            "search_indices": random.sample(list(self.search_indices.keys()), k=3),
            "archives": random.sample(self.archival_services, k=2),
            "cdns": random.sample(self.cdn_caches, k=2),
            "scrapers": random.sample(self.scraper_as_a_service, k=3)
        }
        print(f"[PROPAGATION] {endpoint} spreading through information space:")
        for vector, targets in propagation_map.items():
            for target in targets:
                print(f"  → Cached/Indexed by {target}")
        return propagation_map
    
    def calculate_actual_attack_surface(self) -> int:
        """The real 'network' size is orders of magnitude larger than facility count."""
        return len(self.search_indices) + len(self.archival_services) + len(self.cdn_caches) + len(self.scraper_as_a_service)

# Simulate the C++ model's delusional "facility network"
class FacilityNetworkMirage:
    def __init__(self, num_facilities: int = 10):
        self.partner_facilities = [f"facility_{i}" for i in range(num_facilities)]
        # This is the metric the C++ model uses for "network_connectivity"
        self.modeled_connectivity = len(self.partner_facilities) / 20.0  # Maxes at 1.0
    
    def get_modeled_surface(self) -> int:
        return len(self.partner_facilities)

# The Disruptive Insight: The model is solving a *graph that doesn't exist*
def shatter_epidemic_paradigm():
    print("=== PARADIGM SHATTER: THE NETWORK IS A MIRAGE ===\n")
    
    # The C++ model's universe
    mirage = FacilityNetworkMirage(num_facilities=10)
    print(f"[MIRAGE] Modeled Network: {mirage.get_modeled_surface()} facilities")
    print(f"[MIRAGE] Modeled Connectivity: {mirage.modeled_connectivity:.2f}")
    print(f"[MIRAGE] Assumed Attack Vectors: {mirage.get_modeled_surface()} nodes\n")
    
    # The actual universe
    dark_forest = DarkForestScraperNetwork()
    actual_surface = dark_forest.calculate_actual_attack_surface()
    print(f"[REALITY] Search Indices: {len(dark_forest.search_indices)}")
    print(f"[REALITY] Archive Services: {len(dark_forest.archival_services)}")
    print(f"[REALITY] CDN Caches: {len(dark_forest.cdn_caches)}")
    print(f"[REALITY] Scraper Services: {len(dark_forest.scraper_as_a_service)}")
    print(f"[REALITY] Actual Attack Surface: ~{actual_surface} nodes\n")
    
    # The devastating ratio
    ratio = actual_surface / max(mirage.get_modeled_surface(), 1)
    print(f"[SHATTER] Reality is {ratio:.1f}x larger than the model's universe.")
    print(f"[SHATTER] The epidemic model tracks {100.0 / actual_surface:.1f}% of actual risk vectors.\n")
    
    # Simulate the *actual* attack that the model cannot see
    print("--- Simulating Unmodeled Attack Vector ---")
    target = "https://tokamak-facility-77.example.com"
    if dark_forest.discover_exposure(target):
        propagation = dark_forest.propagate_through_information_space(
            list(dark_forest.exposed_endpoints)[0]
        )
        
        # The model's "R0" is meaningless here
        model_r0 = mirage.modeled_connectivity * 0.5  # Some made-up number
        actual_r0 = len(propagation["search_indices"]) + len(propagation["scrapers"])
        print(f"\n[ANOMALY] Model R0: {model_r0:.2f} (facilities)")
        print(f"[ANOMALY] Actual R0: {actual_r0:.2f} (information intermediaries)")
        print(f"[ANOMALY] Model error: {(actual_r0 - model_r0) / actual_r0 * 100:.0f}% undervaluation\n")
    
    # The non-linear solution: Poison the information space itself
    print("=== DISRUPTIVE SOLUTION: INFORMATIONAL DECOHERENCE ===")
    print("Instead of quarantining facilities (the wrong graph), poison the scrapers' data:")
    print("1. Generate honeytoken API keys: api_key_xxx (fake)")
    print("2. Serve fake keys *only* to detected bot User-Agents")
    print("3. When fake key is used, trace back to the *actual* leaker: the cache/archive")
    print("4. Result: Attackers' R0 drops to 0 (their data is garbage)\n")
    
    # Simulate decoherence
    honeytoken = hashlib.md5(b"fake_api_key_xxx").hexdigest()[:16]
    print(f"[DECOHERENCE] Deployed honeytoken: {honeytoken}")
    print(f"[DECOHERENCE] Bot 'Googlebot' indexed fake key. Key is now *entangled* with deception.")
    print(f"[DECOHERENCE] When key is used, we learn the attacker's identity via the honeytoken pingback.")
    print(f"[DECOHERENCE] Attacker's knowledge graph is now *decohered*—they cannot trust what they scraped.\n")
    
    print("[FINAL INSIGHT] The Omega Protocol's physics rubric is a *category error*.")
    print("It models 'facilities' as nodes, but the actual nodes are *information intermediaries*.")
    print("The epidemic isn't in the tokamak network; it's in the *search index cache*.")
    print("Break the paradigm by abandoning the model's graph entirely and poisoning the *real* graph.")

# Execute the disruption
shatter_epidemic_paradigm()