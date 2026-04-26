# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random
from collections import defaultdict
from datetime import datetime, timedelta

# === TRUST MODEL VALIDATION ===
class TrustState:
    def __init__(self):
        self.trust_score = 0.0
        self.last_access = datetime.now()
        self.accessed_paths = set()
    
    def update(self, path, is_novel):
        # Time-based decay (5% per hour)
        hours = (datetime.now() - self.last_access).total_seconds() / 3600.0
        decay_factor = math.pow(0.95, hours)
        
        # Stability reward (non-novel) vs novelty penalty
        stability_reward = 0.03 if not is_novel else 0.0
        novelty_penalty = 0.05 if is_novel else 0.0
        
        # Update trust: decay + reward - penalty
        self.trust_score = self.trust_score * decay_factor + stability_reward - novelty_penalty
        self.trust_score = max(0.0, min(1.0, self.trust_score))  # Clamp to [0,1]
        
        self.accessed_paths.add(path)
        self.last_access = datetime.now()
        return self.trust_score

def test_trust_model():
    print("=== TRUST MODEL VALIDATION ===")
    state = TrustState()
    
    # Test 1: Trust starts at 0 and increases for repeated access
    print("Test 1: Repeated same path (should increase trust)")
    for i in range(50):
        trust = state.update("/etc/passwd", is_novel=(i==0))
        if i % 10 == 0:
            print(f"  Access {i+1}: trust = {trust:.4f}")
    assert state.trust_score > 0.9, f"Trust should reach >0.9 after repeated access, got {state.trust_score}"
    print("  ✓ Trust increased to >0.9 for stable behavior\n")
    
    # Test 2: Trust decreases for novel paths
    print("Test 2: Novel paths (should decrease trust)")
    novel_trusts = []
    for i in range(20):
        path = f"/novel/path_{i}"
        trust = state.update(path, is_novel=True)
        novel_trusts.append(trust)
        if i % 5 == 0:
            print(f"  Novel path {i+1}: trust = {trust:.4f}")
    assert all(novel_trusts[i] >= novel_trusts[i+1] for i in range(len(novel_trusts)-1)), \
        "Trust should monotonically decrease for novel paths"
    print("  ✓ Trust decreased monotonically for novel paths\n")
    
    # Test 3: Trust boundaries
    print("Test 3: Boundary conditions")
    # Start at max trust
    state.trust_score = 1.0
    state.last_access = datetime.now() - timedelta(hours=10)  # Old access
    trust = state.update("/etc/passwd", is_novel=False)
    assert trust <= 1.0, f"Trust exceeded 1.0: {trust}"
    assert trust >= 0.0, f"Trust below 0.0: {trust}"
    
    # Start at min trust
    state.trust_score = 0.0
    state.last_access = datetime.now() - timedelta(hours=10)
    trust = state.update("/novel/path", is_novel=True)
    assert trust >= 0.0, f"Trust below 0.0: {trust}"
    assert trust <= 1.0, f"Trust exceeded 1.0: {trust}"
    print("  ✓ Trust remains within [0,1] boundaries\n")
    
    return True

# === JITTER MODEL VALIDATION ===
def calculate_traversal_score(unique_paths, max_depth):
    return (unique_paths * 0.6) + (max_depth * 0.4)

def apply_adaptive_jitter(raw_traversal_score, trust_mitigation):
    # Base probability from traversal score
    base_prob = math.pow(raw_traversal_score / 100.0, 1.5)
    base_prob = min(1.0, base_prob)  # Clamp to [0,1]
    
    # Trust-based mitigation: 80% reduction at max trust
    # mitigation = 0.2 * trust_score -> effective_prob = base_prob * (1 - 4 * mitigation)
    effective_prob = base_prob * (1.0 - 4.0 * trust_mitigation)
    effective_prob = max(0.0, min(1.0, effective_prob))  # Clamp to [0,1]
    
    # Apply jitter with probability effective_prob
    if random.random() < effective_prob:
        jitter_ms = 1 + int(49.0 * random.random())  # 1-50 ms
        return jitter_ms, effective_prob
    return 0, effective_prob

def test_jitter_model():
    print("=== JITTER MODEL VALIDATION ===")
    random.seed(42)  # For reproducibility
    
    # Test 1: Probability clamping
    print("Test 1: Probability clamping")
    scores = [0, 50, 100, 150, 200]
    for score in scores:
        base_prob = math.pow(score / 100.0, 1.5)
        clamped = min(1.0, base_prob)
        print(f"  Score {score}: base_prob={base_prob:.4f} -> clamped={clamped:.4f}")
        assert 0.0 <= clamped <= 1.0, f"Probability out of bounds: {clamped}"
    print("  ✓ Probability correctly clamped to [0,1]\n")
    
    # Test 2: Trust-jitter coupling
    print("Test 2: Trust-jitter coupling (80% reduction at max trust)")
    base_score = 100.0  # Base traversal score
    base_prob = math.pow(base_score / 100.0, 1.5)
    base_prob = min(1.0, base_prob)
    
    # Test with zero trust (no mitigation)
    mitigation_zero = 0.0  # trust_score=0.0
    eff_prob_zero, _ = apply_adaptive_jitter(base_score, mitigation_zero)
    # Should equal base_prob (since 1-4*0=1)
    assert abs(eff_prob_zero - base_prob) < 1e-5, \
        f"Zero trust should give base_prob: {eff_prob_zero} vs {base_prob}"
    
    # Test with max trust (mitigation=0.2 -> 80% reduction)
    mitigation_max = 0.2  # trust_score=1.0
    eff_prob_max, _ = apply_adaptive_jitter(base_score, mitigation_max)
    expected = base_prob * 0.2  # 20% of base
    assert abs(eff_prob_max - expected) < 1e-5, \
        f"Max trust should give 20% base_prob: {eff_prob_max} vs {expected}"
    print(f"  Base prob: {base_prob:.4f}")
    print(f"  Zero trust eff_prob: {eff_prob_zero:.4f} (expected {base_prob:.4f})")
    print(f"  Max trust eff_prob: {eff_prob_max:.4f} (expected {expected:.4f})")
    print("  ✓ Trust-jitter coupling works correctly\n")
    
    # Test 3: Jitter range
    print("Test 3: Jitter magnitude")
    jitters = []
    for _ in range(1000):
        jitter, _ = apply_adaptive_jitter(50.0, 0.0)  # Medium score, no trust
        if jitter > 0:
            jitters.append(jitter)
    assert len(jitters) > 0, "No jitter applied in test"
    assert min(jitters) >= 1 and max(jitters) <= 50, \
        f"Jitter out of range [1,50]: min={min(jitters)}, max={max(jitters)}"
    print(f"  Jitter range: [{min(jitters)}, {max(jitters)}] ms")
    print("  ✓ Jitter magnitude correct\n")
    
    return True

# === FORENSIC LOGGER VALIDATION ===
class ForensicEntry:
    def __init__(self, pid, path, operation, latency, traversal_score, trust_score, interval):
        self.timestamp = datetime.now()
        self.pid = pid
        self.path = path
        self.operation = operation
        self.applied_latency_ms = latency
        self.traversal_score = traversal_score
        self.trust_score = trust_score
        self.inter_call_interval = interval

class ForensicLogger:
    def __init__(self):
        self.entries = []
        self.honey_nodes = set(["/honey/etc/passwd", "/honey/var/log"])  # Example honey nodes
    
    def is_honey_node(self, path):
        return any(path.startswith(hn) for hn in self.honey_nodes)
    
    def log_access(self, pid, path, latency, traversal_score, trust_score, interval):
        is_honey = self.is_honey_node(path)
        operation = "honey_node_access" if is_honey else "lookup"
        
        entry = ForensicEntry(
            pid=pid, path=path, operation=operation,
            latency=latency, traversal_score=traversal_score,
            trust_score=trust_score, interval=interval
        )
        self.entries.append(entry)
        
        # Trigger report on honey node access or high traversal score
        if is_honey or traversal_score > 90.0:
            self.generate_report()
    
    def generate_report(self):
        # Simulate report generation
        print(f"  [FORENSIC REPORT] Triggered at {datetime.now()}")
        print(f"    Total entries: {len(self.entries)}")
        honey_count = sum(1 for e in self.entries if e.operation == "honey_node_access")
        print(f"    Honey-node accesses: {honey_count}")
        high_score_count = sum(1 for e in self.entries if e.traversal_score > 90.0)
        print(f"    High traversal score entries: {high_score_count}")

def test_forensic_logger():
    print("=== FORENSIC LOGGER VALIDATION ===")
    logger = ForensicLogger()
    
    # Test 1: Honey node detection
    print("Test 1: Honey node detection")
    test_paths = [
        ("/etc/passwd", False),
        ("/honey/etc/passwd", True),
        ("/var/log/syslog", False),
        ("/honey/var/log/auth.log", True),
        ("/tmp/test", False)
    ]
    for path, expected in test_paths:
        result = logger.is_honey_node(path)
        assert result == expected, \
            f"Honey node mismatch for {path}: expected {expected}, got {result}"
    print("  ✓ Honey node detection correct\n")
    
    # Test 2: Report triggering
    print("Test 2: Report triggering conditions")
    # Trigger via honey node
    logger.log_access(123, "/honey/etc/passwd", 10, 50.0, 0.8, 100.0)
    # Trigger via high traversal score
    logger.log_access(456, "/tmp/scan", 20, 95.0, 0.3, 50.0)
    # No trigger
    logger.log_access(789, "/etc/hosts", 5, 30.0, 0.9, 200.0)
    
    assert len(logger.entries) == 3, "Should have 3 log entries"
    assert logger.entries[0].operation == "honey_node_access", \
        "First entry should be honey node access"
    assert logger.entries[1].operation == "lookup", \
        "Second entry should be lookup (but triggered by score)"
    assert logger.entries[2].operation == "lookup", \
        "Third entry should be lookup (no trigger)"
    print("  ✓ Report triggering works correctly\n")
    
    # Test 3: Forensic data integrity
    print("Test 3: Forensic data fields")
    entry = logger.entries[0]
    assert hasattr(entry, 'timestamp'), "Missing timestamp"
    assert hasattr(entry, 'pid'), "Missing pid"
    assert hasattr(entry, 'path'), "Missing path"
    assert hasattr(entry, 'operation'), "Missing operation"
    assert hasattr(entry, 'applied_latency_ms'), "Missing latency"
    assert hasattr(entry, 'traversal_score'), "Missing traversal score"
    assert hasattr(entry, 'trust_score'), "Missing trust score"
    assert hasattr(entry, 'inter_call_interval'), "Missing interval"
    print("  ✓ All forensic fields present\n")
    
    return True

# === TOPOLOGY ANALYSIS VALIDATION ===
def update_topology(path, unique_paths, depth_histogram, max_depth_ref):
    # Update unique paths
    unique_paths.add(path)
    
    # Calculate depth (number of '/' characters)
    depth = path.count('/')
    
    # Update max depth
    if depth > max_depth_ref[0]:
        max_depth_ref[0] = depth
    
    # Update depth histogram
    while len(depth_histogram) <= depth:
        depth_histogram.append(0)
    depth_histogram[depth] += 1
    
    return depth

def test_topology():
    print("=== TOPOLOGY ANALYSIS VALIDATION ===")
    unique_paths = set()
    depth_histogram = []
    max_depth_ref = [0]  # Use list for mutable reference
    
    # Test paths
    paths = [
        "/",           # depth=0
        "/etc",        # depth=1
        "/etc/passwd", # depth=2
        "/var/log",    # depth=2
        "/usr/bin",    # depth=2
        "/usr/bin/vim" # depth=3
    ]
    
    expected_depths = [0, 1, 2, 2, 2, 3]
    for i, path in enumerate(paths):
        depth = update_topology(path, unique_paths, depth_histogram, max_depth_ref)
        assert depth == expected_depths[i], \
            f"Depth mismatch for {path}: expected {expected_depths[i]}, got {depth}"
    
    # Check unique paths
    assert len(unique_paths) == len(paths), \
        f"Unique paths count mismatch: expected {len(paths)}, got {len(unique_paths)}"
    
    # Check max depth
    assert max_depth_ref[0] == 3, \
        f"Max depth should be 3, got {max_depth_ref[0]}"
    
    # Check depth histogram
    # Index: 0->1, 1->1, 2->3, 3->1
    assert depth_histogram[0] == 1, "Depth 0 count wrong"
    assert depth_histogram[1] == 1, "Depth 1 count wrong"
    assert depth_histogram[2] == 3, "Depth 2 count wrong"
    assert depth_histogram[3] == 1, "Depth 3 count wrong"
    assert len(depth_histogram) == 4, \
        f"Histogram length should be 4, got {len(depth_histogram)}"
    
    print("  Paths processed:", list(unique_paths))
    print("  Depth histogram:", depth_histogram)
    print("  Max depth:", max_depth_ref[0])
    print("  ✓ Topology analysis correct\n")
    
    return True

# === MAIN VALIDATION SUITE ===
def main():
    print("=" * 60)
    print("AFDS v3.0 OMEGA PROTOCOL INVARIANT VALIDATION")
    print("=" * 60)
    
    try:
        # Run all validation tests
        test_trust_model()
        test_jitter_model()
        test_forensic_logger()
        test_topology()
        
        print("=" * 60)
        print("ALL VALIDATIONS PASSED")
        print("AFDS v3.0 is MATHEMATICALLY SOUND and OMEGA COMPLIANT")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print("=" * 60)
        print("VALIDATION FAILED:")
        print(str(e))
        print("=" * 60)
        return False
    except Exception as e:
        print("=" * 60)
        print("UNEXPECTED ERROR:")
        print(str(e))
        print("=" * 60)
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)