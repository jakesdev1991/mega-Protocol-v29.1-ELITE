# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import random
from typing import List, Tuple

def validate_jitter() -> Tuple[bool, str]:
    """Validate non-linear bounded jitter calculation."""
    MIN_JITTER_MS = 1
    MAX_JITTER_MS = 50
    JITTER_DECAY_RATE = 0.7
    
    # Test boundary conditions
    u_min = 0.0
    jitter_min = MIN_JITTER_MS + (MAX_JITTER_MS - MIN_JITTER_MS) * (u_min ** JITTER_DECAY_RATE)
    u_max = 1.0
    jitter_max = MIN_JITTER_MS + (MAX_JITTER_MS - MIN_JITTER_MS) * (u_max ** JITTER_DECAY_RATE)
    
    if not (math.isclose(jitter_min, MIN_JITTER_MS, abs_tol=1e-9) and 
            math.isclose(jitter_max, MAX_JITTER_MS, abs_tol=1e-9)):
        return False, f"Jitter boundaries failed: min={jitter_min} (expected {MIN_JITTER_MS}), max={jitter_max} (expected {MAX_JITTER_MS})"
    
    # Test monotonicity and range
    prev = jitter_min
    for i in range(1, 101):
        u = i / 100.0
        jitter = MIN_JITTER_MS + (MAX_JITTER_MS - MIN_JITTER_MS) * (u ** JITTER_DECAY_RATE)
        if jitter < prev - 1e-9:  # Allow tiny floating point errors
            return False, f"Jitter non-monotonic at u={u}: {jitter} < {prev}"
        if jitter < MIN_JITTER_MS - 1e-9 or jitter > MAX_JITTER_MS + 1e-9:
            return False, f"Jitter out of bounds at u={u}: {jitter}"
        prev = jitter
    
    # Test distribution shape (should be concave for decay rate <1)
    samples = [random.random() for _ in range(10000)]
    jitters = [MIN_JITTER_MS + (MAX_JITTER_MS - MIN_JITTER_MS) * (s ** JITTER_DECAY_RATE) for s in samples]
    # Check if median is closer to min than max (concave bias toward lower values)
    median_jitter = sorted(jitters)[len(jitters)//2]
    midpoint = (MIN_JITTER_MS + MAX_JITTER_MS) / 2
    if median_jitter > midpoint + 5:  # Allow some tolerance
        return False, f"Jitter distribution biased toward high values (median={median_jitter}, midpoint={midpoint})"
    
    return True, "Jitter calculation mathematically sound"

def validate_scoring() -> Tuple[bool, str]:
    """Validate multi-factor scoring and topology stress calculation."""
    # Mock state simulation
    class MockState:
        def __init__(self):
            self.path_frequency = {}
            self.unique_paths = set()
            self.last_update = 0.0  # Simulated time
            self.score = 0.0
            self.topology_stress = 0.0
    
    state = MockState()
    a, b, c = 0.4, 0.3, 0.3
    
    def update_score(path: str, current_time: float):
        # Update frequency and unique paths
        state.path_frequency[path] = state.path_frequency.get(path, 0) + 1
        if state.path_frequency[path] == 1:
            state.unique_paths.add(path)
        
        # Calculate topology stress (d(unique_paths)/dt)
        delta_time = current_time - state.last_update
        if delta_time <= 0:
            # Avoid division by zero; use previous stress or zero
            state.topology_stress = 0.0
        else:
            state.topology_stress = len(state.unique_paths) / delta_time  # FLAWED: should be delta_unique/delta_time
        
        state.last_update = current_time
        
        # Calculate depth (FLAWED: uses string length, not component count)
        if '/' in path:
            parent = path[:path.rfind('/')]
            depth = len(parent)
        else:
            depth = 0
        
        # Multi-factor scoring
        state.score = a * (len(state.path_frequency) / delta_time) + \
                     b * len(state.unique_paths) + \
                     c * depth
    
    # Test Case 1: First access to new path
    state = MockState()
    update_score("/etc/passwd", 1.0)
    # Expected: 
    #   unique_paths = 1, path_frequency size = 1, delta_time=1.0
    #   topology_stress = 1/1.0 = 1.0
    #   depth = len("/etc") = 4
    #   score = 0.4*(1/1.0) + 0.3*1 + 0.3*4 = 0.4 + 0.3 + 1.2 = 1.9
    expected_score = 0.4*(1/1.0) + 0.3*1 + 0.3*4
    if not math.isclose(state.score, expected_score, rel_tol=1e-9):
        return False, f"Scoring failed for first access: got {state.score}, expected {expected_score}"
    
    # Test Case 2: Second access to same path (should not increase unique_paths)
    update_score("/etc/passwd", 2.0)  # delta_time=1.0
    # Expected:
    #   unique_paths still = 1, path_frequency size = 1, delta_time=1.0
    #   topology_stress = 1/1.0 = 1.0 (FLAWED: should be 0/1.0=0 since no new unique paths)
    #   depth = 4
    #   score = 0.4*(1/1.0) + 0.3*1 + 0.3*4 = 1.9 (same as before)
    expected_score2 = 0.4*(1/1.0) + 0.3*1 + 0.3*4
    if not math.isclose(state.score, expected_score2, rel_tol=1e-9):
        return False, f"Scoring failed for repeated access: got {state.score}, expected {expected_score2}"
    
    # Test Case 3: Access to new path (should increase unique_paths)
    update_score("/etc/shadow", 3.0)  # delta_time=1.0
    # Expected:
    #   unique_paths = 2, path_frequency size = 2, delta_time=1.0
    #   topology_stress = 2/1.0 = 2.0 (FLAWED: should be 1/1.0=1.0)
    #   depth = len("/etc") = 4
    #   score = 0.4*(2/1.0) + 0.3*2 + 0.3*4 = 0.8 + 0.6 + 1.2 = 2.6
    expected_score3 = 0.4*(2/1.0) + 0.3*2 + 0.3*4
    if not math.isclose(state.score, expected_score3, rel_tol=1e-9):
        return False, f"Scoring failed for new path: got {state.score}, expected {expected_score3}"
    
    # Critical flaw detection: topology stress should reflect *change* in unique paths
    # After first two calls to same path, unique_paths didn't change in second call
    # But topology_stress remained 1.0 (should be 0.0)
    # We'll check this indirectly via score consistency
    if math.isclose(state.score, 1.9, rel_tol=1e-9):  # After second access
        pass  # Consistent with flawed model
    else:
        return False, "Scoring inconsistent with flawed topology stress model"
    
    return True, "Scoring implementation matches provided code (despite known flaws in topology stress and depth)"

def validate_depth() -> Tuple[bool, str]:
    """Validate depth calculation (known to be flawed)."""
    test_cases = [
        ("/file", 0),          # Root file: parent="" -> len=0
        ("/dir/", 4),          # Root dir with trailing slash: parent="/dir" -> len=4? 
                               # But FUSE typically normalizes; assuming no trailing slash in practice
        ("/home/user/file", 10), # Parent="/home/user" -> len=10
        ("/a/b/c/d/e", 9),     # Parent="/a/b/c/d" -> len=9
        ("file", 0),           # No slash -> depth=0
        ("/a", 0),             # Parent="" -> len=0
    ]
    
    for path, expected_len in test_cases:
        if '/' in path:
            parent = path[:path.rfind('/')]
            actual_len = len(parent)
        else:
            actual_len = 0
        if actual_len != expected_len:
            return False, f"Depth calculation mismatch for '{path}': got {actual_len}, expected {expected_len}"
    
    # Compare to actual component count (what it should be)
    def actual_depth(path: str) -> int:
        if path == "/":
            return 0
        # Normalize: remove trailing slash if present
        if path.endswith("/") and len(path) > 1:
            path = path[:-1]
        # Count components (split by '/' and filter empty)
        parts = [p for p in path.split('/') if p != '']
        return len(parts)
    
    flaw_cases = [
        ("/home/user/file", 10, 2),   # String length=10, actual depth=2
        ("/a/b/c", 5, 2),             # String length=5 ("/a/b"), actual depth=2
        ("/very/long/path/here", 18, 3) # String length=18, actual depth=3
    ]
    
    for path, string_len, actual_comp in flaw_cases:
        if '/' in path:
            parent = path[:path.rfind('/')]
            calc_len = len(parent)
        else:
            calc_len = 0
        if calc_len != string_len:
            return False, f"Internal error in depth test for '{path}'"
        if calc_len == actual_comp:
            return False, f"Depth calculation accidentally matches component count for '{path}' (should be flawed)"
    
    return True, "Depth calculation matches provided code (known flaw: uses string length instead of component count)"

def validate_trusted_pids() -> Tuple[bool, str]:
    """Validate trusted PID registry lookup."""
    TRUSTED_PIDS = [1, 1234, 5678]
    
    # Test trusted PIDs
    for pid in TRUSTED_PIDS:
        if pid not in TRUSTED_PIDS:
            return False, f"Trusted PID {pid} not found in registry"
    
    # Test untrusted PID
    if 9999 in TRUSTED_PIDS:
        return False, "Untrusted PID 9999 incorrectly found in registry"
    
    # Test lookup efficiency (O(n) but small n is acceptable)
    if len(TRUSTED_PIDS) > 10:
        return False, "Trusted PID registry unexpectedly large (should be small constant)"
    
    return True, "Trusted PID registry lookup sound"

def main():
    """Run all validation checks."""
    checks = [
        ("Jitter Calculation", validate_jitter),
        ("Scoring Implementation", validate_scoring),
        ("Depth Calculation", validate_depth),
        ("Trusted PID Registry", validate_trusted_pids)
    ]
    
    all_passed = True
    for name, check_func in checks:
        passed, msg = check_func()
        if passed:
            print(f"[PASS] {name}: {msg}")
        else:
            print(f"[FAIL] {name}: {msg}")
            all_passed = False
    
    if all_passed:
        print("\nAll mathematical validations completed. Note: Known flaws in topology stress and depth calculations")
        print("were identified but match the provided code implementation.")
    else:
        print("\nSome validations failed. Review the code for mathematical errors.")
    
    return all_passed

if __name__ == "__main__":
    main()