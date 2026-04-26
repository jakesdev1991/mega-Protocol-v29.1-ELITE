# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import time
import hashlib
import secrets
import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set

# ============================================
# SIMULATION: LEGACY AFDS (FLAWED)
# ============================================

class LegacyTrustManager:
    def __init__(self):
        self.states = {}
        self.pid_reuse_counter = 0
    
    def assign_pid(self, is_trusted_legacy=False):
        # Simulate PID reuse: cycle through 0-100
        pid = self.pid_reuse_counter % 100
        self.pid_reuse_counter += 1
        if pid not in self.states:
            self.states[pid] = {"trust": 0.0, "paths": set()}
        if is_trusted_legacy:  # Simulate pre-trusted process
            self.states[pid]["trust"] = 0.95
        return pid
    
    def access_path(self, pid, path):
        state = self.states[pid]
        is_novel = path not in state["paths"]
        if not is_novel:
            state["trust"] = min(1.0, state["trust"] + 0.01)  # Gameable!
        state["paths"].add(path)
        return state["trust"]

class LegacyJitter:
    def __init__(self):
        self.rng = random.Random(42)  # Predictable!
    
    def get_latency(self, trust_score):
        # Flawed: uniform distribution leaks trust state
        prob = (trust_score / 100.0) ** 1.5
        if self.rng.random() < prob:
            return self.rng.randint(1, 50)
        return 0

# ============================================
# SIMULATION: ADVERSARIAL TRUST GYMNASIUM
# ============================================

@dataclass
class CapabilityToken:
    token_id: str
    parent_id: str
    binary_hash: str
    trust_level: float
    puzzle_exempt: bool = False

class GymnasiumTrust:
    def __init__(self):
        self.tokens: Dict[str, CapabilityToken] = {}
        self.salt = secrets.token_bytes(32)
        self.puzzle_difficulty = defaultdict(int)
        
    def mint_token(self, parent_id, binary_hash, is_known_good=False):
        token_id = hashlib.sha256(f"{parent_id}{binary_hash}{secrets.token_hex(4)}".encode()).hexdigest()[:16]
        trust = 0.9 if is_known_good else 0.1
        exempt = is_known_good
        token = CapabilityToken(token_id, parent_id, binary_hash, trust, exempt)
        self.tokens[token_id] = token
        return token_id
    
    def challenge(self, token_id, path, request_rate):
        if self.tokens[token_id].puzzle_exempt:
            return 0  # No latency for known-good
        
        # Exponential difficulty scaling
        self.puzzle_difficulty[token_id] = min(10, self.puzzle_difficulty[token_id] + request_rate / 10.0)
        difficulty = int(self.puzzle_difficulty[token_id])
        
        # Simulate puzzle solving time: ~10ms * 2^difficulty
        latency_ms = (2 ** difficulty) * 10
        
        # If honey trap accessed, difficulty → infinity (ban)
        if "honey" in path:
            self.puzzle_difficulty[token_id] = 100
            return 5000
        
        return latency_ms

# ============================================
# ATTACK SIMULATIONS
# ============================================

def simulate_pid_reuse_attack():
    print("=== ATTACK 1: PID Reuse ===")
    legacy = LegacyTrustManager()
    
    # Legitimate admin process runs and builds trust
    admin_pid = legacy.assign_pid(is_trusted_legacy=True)
    for i in range(10):
        legacy.access_path(admin_pid, f"/etc/config{i}.conf")
    print(f"Legacy: Admin PID {admin_pid} trust = {legacy.states[admin_pid]['trust']:.2f}")
    
    # Admin exits, attacker gets same PID
    attacker_pid = legacy.assign_pid()  # Reuses PID 0
    print(f"Legacy: Attacker inherited PID {attacker_pid} with trust = {legacy.states[attacker_pid]['trust']:.2f}!")
    
    # Attacker accesses sensitive path with inherited trust
    mitigation = 0.8 * legacy.states[attacker_pid]["trust"]
    print(f"Legacy: Attacker gets {mitigation*100:.0f}% latency mitigation due to trust inheritance!\n")

def simulate_trust_gaming_attack():
    print("=== ATTACK 2: Trust Gaming ===")
    legacy = LegacyTrustManager()
    jitter = LegacyJitter()
    
    # Attacker learns paths slowly
    attacker_pid = legacy.assign_pid()
    latencies = []
    for day in range(7):  # Week-long slow game
        for path in ["/usr/bin/ls", "/etc/passwd", "/var/log/syslog"]:
            trust = legacy.access_path(attacker_pid, path)  # No novelty penalty
            latencies.append(jitter.get_latency(trust))
    
    print(f"Legacy: Attacker trust after gaming = {trust:.2f}")
    print(f"Legacy: Average latency = {statistics.mean(latencies):.2f}ms (min={min(latencies)}, max={max(latencies)})")
    print("Legacy: Attacker now performs fast scan...")
    
    # Now attacker scans fast
    for i in range(20):
        legacy.access_path(attacker_pid, f"/secret/file{i}.txt")
        lat = jitter.get_latency(trust)  # Still high trust!
        latencies.append(lat)
    print(f"Legacy: Scan latency = {statistics.mean(latencies[-20:]):.2f}ms (ineffective!)\n")

def simulate_statistical_jitter_exploit():
    print("=== ATTACK 3: Statistical Jitter Exploit ===")
    jitter = LegacyJitter()
    
    # Attacker measures latency distribution
    samples = [jitter.get_latency(0.1) for _ in range(1000)]  # Low trust
    samples_high = [jitter.get_latency(0.9) for _ in range(1000)]  # High trust
    
    # Detect trust state via latency variance
    var_low = statistics.variance(samples)
    var_high = statistics.variance(samples_high)
    print(f"Legacy: Low-trust latency variance = {var_low:.2f}")
    print(f"Legacy: High-trust latency variance = {var_high:.2f}")
    print(f"Legacy: Trust state is STATISTICALLY DETECTABLE via variance!\n")

def simulate_gymnasium_defense():
    print("=== GYMNASIUM: Active Defense ===")
    gym = GymnasiumTrust()
    
    # Legitimate process (bash)
    bash_token = gym.mint_token("root", "bash_hash", is_known_good=True)
    latency = gym.challenge(bash_token, "/etc/passwd", request_rate=1)
    print(f"Gymnasium: Bash access latency = {latency}ms (exempt)")
    
    # Unknown scanner process
    scanner_token = gym.mint_token("root", "evil_scanner_hash")
    latencies = []
    for i in range(50):  # Burst scan
        lat = gym.challenge(scanner_token, f"/file{i}.txt", request_rate=50)
        latencies.append(lat)
    
    print(f"Gymnasium: Scanner avg latency = {statistics.mean(latencies):.2f}ms")
    print(f"Gymnasium: Final puzzle difficulty = {gym.puzzle_difficulty[scanner_token]:.2f}")
    print(f"Gymnasium: Slowdown factor = {statistics.mean(latencies) / 0.1:.0f}x\n")

# ============================================
# EXECUTE DISRUPTION
# ============================================

if __name__ == "__main__":
    random.seed(42)
    simulate_pid_reuse_attack()
    simulate_trust_gaming_attack()
    simulate_statistical_jitter_exploit()
    simulate_gymnasium_defense()
    
    print("=== CONCLUSION ===")
    print("Legacy AFDS: Trust is gameable, PID is identity, jitter is detectable.")
    print("Adversarial Gymnasium: Trust is proven, capability is identity, cost is asymmetric.")
    print("DISRUPTION: The paradigm must shift from OBSERVATION to PROVOCATION.")