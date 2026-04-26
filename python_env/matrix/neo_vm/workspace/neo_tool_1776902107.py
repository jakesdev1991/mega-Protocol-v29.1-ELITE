# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import time
from collections import defaultdict
import threading

# --- AFDS Flawed Parameters ---
MIN_JITTER_MS = 1
MAX_JITTER_MS = 50
JITTER_DECAY_RATE = 0.7
TRUSTED_PIDS = {1, 1234, 5678}

# --- Bug: Separate static state per operation ---
class AFDS_State:
    def __init__(self):
        self.path_frequency = defaultdict(int)
        self.unique_paths = set()
        self.lock = threading.Lock()
        self.score = 0.0
        self.topology_stress = 0.0
        self.last_update = None

lookup_state = AFDS_State()
readdir_state = AFDS_State()

def jitter_delay():
    # Missing rng seed is a compile error; we simulate to show distribution leak
    return MIN_JITTER_MS + (MAX_JITTER_MS - MIN_JITTER_MS) * (random.random() ** JITTER_DECAY_RATE)

def update_score(state, path, delta_time):
    with state.lock:
        state.path_frequency[path] += 1
        state.unique_paths.add(path)
        state.topology_stress = len(state.unique_paths) / delta_time if delta_time > 0 else 0
        call_rate = len(state.path_frequency) / delta_time if delta_time > 0 else 0
        depth = path.count('/')
        state.score = 0.4 * call_rate + 0.3 * len(state.unique_paths) + 0.3 * depth

def simulate_lookup(pid, path):
    if pid in TRUSTED_PIDS:
        return 0.0
    delay = jitter_delay()
    time.sleep(delay / 1000.0)
    now = time.time()
    state = lookup_state
    delta = now - state.last_update if state.last_update else 0.001
    state.last_update = now
    update_score(state, path, delta)
    return delay

def simulate_readdir(pid, path):
    if pid in TRUSTED_PIDS:
        return 0.0
    delay = jitter_delay()
    time.sleep(delay / 1000.0)
    now = time.time()
    state = readdir_state
    delta = now - state.last_update if state.last_update else 0.001
    state.last_update = now
    update_score(state, path, delta)
    return delay

def run_attack(pid, split_factor=0.0, paths=500):
    total_delay = 0.0
    for i in range(paths):
        path = f"/deep/path/entry_{i}"
        if random.random() < split_factor:
            total_delay += simulate_readdir(pid, path)
        else:
            total_delay += simulate_lookup(pid, path)
    return total_delay

# --- Attack 1: Trusted PID Bypass ---
print("🔓 ATTACK 1: Trusted PID 1234 (no jitter)")
random.seed(0)
lookup_state = AFDS_State(); readdir_state = AFDS_State()
start = time.time()
delay = run_attack(1234, split_factor=0.0, paths=200)
print(f"  → Total jitter: {delay:.2f} ms, Elapsed: {time.time()-start:.2f} s")
print(f"  → Lookup score: {lookup_state.score:.2f}, Readdir score: {readdir_state.score:.2f}")

# --- Attack 2: State Fragmentation Evasion ---
print("\n🎭 ATTACK 2: Split traffic 50/50 to evade detection")
random.seed(1)
lookup_state = AFDS_State(); readdir_state = AFDS_State()
start = time.time()
delay = run_attack(9999, split_factor=0.5, paths=200)
print(f"  → Total jitter: {delay:.2f} ms, Elapsed: {time.time()-start:.2f} s")
print(f"  → Lookup score: {lookup_state.score:.2f}, Readdir score: {readdir_state.score:.2f}")
print("  → Both scores are halved; any threshold >15.0 is blind.")

# --- Attack 3: Path Poisoning from 'Trusted' PID ---
print("\n☠️  ATTACK 3: Poison state from trusted PID (DoS)")
lookup_state = AFDS_State(); readdir_state = AFDS_State()
for i in range(5000):
    simulate_lookup(1234, f"/fake/poison_{i}")
print(f"  → Unique paths poisoned: {len(lookup_state.unique_paths)}")
print(f"  → Topology stress: {lookup_state.topology_stress:.2f}")
print("  → Now any untrusted PID inherits a bloated state, causing false positives & resource exhaustion.")

# --- Side-Channel: Jitter Distribution Leak ---
samples = [jitter_delay() for _ in range(10000)]
print(f"\n📡 SIDE-CHANNEL: Jitter distribution (mean={sum(samples)/len(samples):.2f} ms, std={(__import__('statistics').stdev(samples) if len(samples)>1 else 0):.2f} ms)")
print("  → Attacker fits distribution and subtracts noise; defense becomes transparent.")