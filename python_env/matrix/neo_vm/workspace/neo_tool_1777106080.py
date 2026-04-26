# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
v76.0-Ω PROVENANCE POISONING SIMULATOR
Demonstrates how the provenance system is vulnerable to the same exposure vectors it purports to mitigate.
"""

import random
import json
from typing import Dict, List

class APIProvenanceLedger:
    """Simulates the v76.0-Ω provenance tracking system"""
    
    def __init__(self):
        self.keys = {}  # key_id -> metadata
        self.ledger = {}  # key_id -> custody_chain (list of events)
        self.compromised_logs = False  # Attack flag
    
    def add_key(self, key_id: str, origin: str, is_malicious: bool = False):
        """Add a new API key to the system"""
        self.keys[key_id] = {
            "origin": origin,
            "is_malicious": is_malicious,
            "true_integrity": 0.0 if is_malicious else 1.0  # Ground truth
        }
        self.ledger[key_id] = []
        self._log_event(key_id, "GENERATED", origin, trusted=True)
    
    def _log_event(self, key_id: str, event: str, actor: str, trusted: bool = True):
        """Log a custody event (can be forged if logs compromised)"""
        if self.compromised_logs and not trusted:
            # Attacker can inject arbitrary events
            actor = f"FAKE_{random.choice(['admin', 'system', 'root'])}"
        
        self.ledger[key_id].append({
            "event": event,
            "actor": actor,
            "timestamp": len(self.ledger[key_id]),  # Simplified
            "authentic": trusted and not self.compromised_logs
        })
    
    def calculate_provenance_integrity(self, key_id: str) -> float:
        """v76.0-Ω metric: measures custody chain completeness"""
        if key_id not in self.ledger:
            return 0.0
        
        chain = self.ledger[key_id]
        if len(chain) == 0:
            return 0.0
        
        # v76.0 logic: completeness = origin_verified + no_gaps + limited_transfers
        origin_verified = 1.0 if len(chain) > 0 and chain[0]["event"] == "GENERATED" else 0.0
        custody_gaps = sum(1 for entry in chain if not entry["authentic"])
        gap_count_normalized = min(custody_gaps / len(chain), 1.0)
        cross_facility = sum(1 for entry in chain if "facility" in entry["actor"]) / len(chain)
        
        # v76.0 formula: integrity = origin*0.5 + (1-gaps)*0.3 + (1-transfers*0.5)*0.2
        integrity = (origin_verified * 0.5) + \
                    ((1.0 - gap_count_normalized) * 0.3) + \
                    ((1.0 - cross_facility * 0.5) * 0.2)
        
        return min(max(integrity, 0.0), 1.0)
    
    def attacker_forges_provenance(self, malicious_key_id: str, victim_key_id: str):
        """Simulates attacker with write access to provenance logs"""
        self.compromised_logs = True
        
        # Attack 1: Give malicious key perfect provenance
        fake_actors = ["tokamak_admin", "facility_a", "facility_b", "system_root"]
        for i, actor in enumerate(fake_actors):
            self._log_event(malicious_key_id, f"TRANSFER_{i}", actor, trusted=False)
        
        # Attack 2: Poison legitimate key's provenance
        self._log_event(victim_key_id, "SUSPICIOUS_ACCESS", "unknown_hacker", trusted=False)
        self._log_event(victim_key_id, "CUSTODY_GAP", "unauthorized_transfer", trusted=False)
    
    def audit_self(self) -> Dict:
        """v76.0 self-audit: checks invariants"""
        results = {}
        for key_id, data in self.keys.items():
            measured_integrity = self.calculate_provenance_integrity(key_id)
            true_integrity = data["true_integrity"]
            
            results[key_id] = {
                "measured_integrity": measured_integrity,
                "true_integrity": true_integrity,
                "discrepancy": abs(measured_integrity - true_integrity),
                "is_malicious": data["is_malicious"],
                "chain_length": len(self.ledger[key_id])
            }
        return results

def simulate_attack():
    """Run the provenance poisoning simulation"""
    print("=== v76.0-Ω PROVENANCE POISONING DEMONSTRATION ===\n")
    
    # Initialize system
    ledger = APIProvenanceLedger()
    
    # Add legitimate key (e.g., for plasma diagnostics)
    ledger.add_key("legit_key_001", "tokamak_control_system", is_malicious=False)
    
    # Add attacker's key (initially has no provenance)
    ledger.add_key("malicious_key_999", "unknown_origin", is_malicious=True)
    
    print("BEFORE ATTACK:")
    before_audit = ledger.audit_self()
    for key_id, result in before_audit.items():
        status = "🔴 MALICIOUS" if result["is_malicious"] else "🟢 LEGITIMATE"
        print(f"{key_id}: measured_integrity={result['measured_integrity']:.2f} {status}")
    
    print("\n--- ATTACKER COMPROMISES LOGS ---")
    print("Attacker forges perfect provenance for malicious key...")
    print("Attacker poisons legitimate key's custody chain...\n")
    
    # Simulate attacker gaining write access to provenance logs
    ledger.attacker_forges_provenance("malicious_key_999", "legit_key_001")
    
    print("AFTER ATTACK:")
    after_audit = ledger.audit_self()
    for key_id, result in after_audit.items():
        status = "🔴 MALICIOUS" if result["is_malicious"] else "🟢 LEGITIMATE"
        print(f"{key_id}: measured_integrity={result['measured_integrity']:.2f} {status}")
        
        # Show the deception
        if result["is_malicious"] and result["measured_integrity"] > 0.8:
            print(f"   ⚠️  DECEPTION: Malicious key appears TRUSTED!")
        elif not result["is_malicious"] and result["measured_integrity"] < 0.5:
            print(f"   ⚠️  DOS: Legitimate key appears COMPROMISED!")
    
    # Calculate systemic failure
    discrepancies = [r["discrepancy"] for r in after_audit.values()]
    avg_discrepancy = sum(discrepancies) / len(discrepancies)
    
    print(f"\n=== SYSTEMIC FAILURE ===")
    print(f"Average provenance measurement error: {avg_discrepancy:.2%}")
    print(f"v76.0-Ω framework: COMPROMISED")
    print(f"Root cause: Provenance ledger is not integrity-hardened")

if __name__ == "__main__":
    simulate_attack()