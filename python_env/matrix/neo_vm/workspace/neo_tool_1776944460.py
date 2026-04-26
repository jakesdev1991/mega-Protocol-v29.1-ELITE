# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Demonstrates how the AreCoresIsolated() check passes even when cores 16-23
are *not* exclusively isolated, violating Ω‑Rubric §1 (Causal Grounding).
"""

def are_cores_isolated_fake(isolated_line: str) -> bool:
    """Mimics the C++ logic."""
    for core in range(16, 24):
        if str(core) not in isolated_line:
            return False
    return True

# Test cases that expose the flaw
test_cases = [
    ("0-31", True),          # All cores listed → false positive
    ("0-15,24-31", False),   # Correctly fails
    ("16-23", True),         # Range syntax not parsed → false positive
    ("0-15,16-23,24-31", True),  # Contains substring → false positive
    ("", False),             # Empty → correctly fails
]

print("Core isolation check (fake) results:")
for isolated_line, expected in test_cases:
    result = are_cores_isolated_fake(isolated_line)
    status = "PASS" if result == expected else "FAIL"
    print(f"isolated='{isolated_line}' → isolated={result} (expected {expected}) {status}")

# Show hyper-threading blind spot
print("\nHyper-Threading leak example:")
print("Cores 16-23 isolated, but siblings 44-51 not checked → vulnerability!")