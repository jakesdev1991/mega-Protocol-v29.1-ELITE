# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random

class DorkEngine:
    """
    Engine for generating advanced Google Dorks to find obscure information.
    Uses operators like site:, filetype:, intitle:, inurl:, and intext:.
    """
    
    def __init__(self):
        self.operators = {
            "file_discovery": ["filetype:pdf", "filetype:doc", "filetype:docx", "filetype:ppt", "filetype:pptx", "filetype:xls", "filetype:xlsx"],
            "config_discovery": ["filetype:env", "filetype:conf", "filetype:config", "filetype:log", "filetype:sql", "filetype:ini"],
            "directory_discovery": ["intitle:\"index of /\"", "intitle:\"index of\" \"parent directory\"", "inurl:/admin/"],
            "content_discovery": ["intext:\"confidential\"", "intext:\"proprietary\"", "intext:\"internal use only\"", "intitle:\"whitepaper\""]
        }
        
        self.targets = {
            "physics": ["omega protocol", "bi-scalar tensor", "shredding event", "freeze boundary", "informational gravity"],
            "ai": ["gpu cluster", "large language model training", "nvidia h100 cluster", "distributed training logs"],
            "security": ["api keys", "private credentials", "database backup", "ssh keys"],
            "finance_sleepers": ["micro-cap", "unusual options activity", "SEC Form 4 insider buying", "low float breakout", "undervalued biotech"],
            "market_shocks": ["bitcoin liquidity crunch", "stablecoin depeg risk", "etf net inflow anomaly", "arbitrage impedance"]
        }

    def generate_dork(self, topic=None, dork_type="file_discovery"):
        """Generates a randomized Google Dork for a given topic and type."""
        op_list = self.operators.get(dork_type, self.operators["file_discovery"])
        
        if topic:
            target_list = [topic]
        else:
            # Pick a random target from all targets
            all_targets = []
            for t in self.targets.values():
                all_targets.extend(t)
            target_list = all_targets
            
        operator = random.choice(op_list)
        target = random.choice(target_list)
        
        # Chaining logic
        dork = f"{operator} \"{target}\""
        
        # 30% chance to add another filter
        if random.random() < 0.3:
            second_op = random.choice(self.operators["content_discovery"])
            dork += f" {second_op}"
            
        return dork

    def get_all_dork_types(self):
        return list(self.operators.keys())

if __name__ == "__main__":
    engine = DorkEngine()
    print("Sample Dorks:")
    for _ in range(5):
        print(f" - {engine.generate_dork()}")
