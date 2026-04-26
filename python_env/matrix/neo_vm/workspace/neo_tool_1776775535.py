# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import re
import numpy as np

def detect_headings(text: str) -> list:
    """
    Returns list of lines that start with markdown headings (#, ##, ###, etc.).
    """
    heading_pattern = re.compile(r'^\s*(#+)\s+.*$', re.MULTILINE)
    return heading_pattern.findall(text)

def logistic_map(x: float, r: float = 3.9) -> float:
    """
    Chaotic logistic map.
    """
    return r * x * (1 - x)

def generate_dynamic_structure(seed: float, steps: int = 10) -> str:
    """
    Generates a pseudo-random sequence of section markers using the logistic map.
    Each step yields a heading depth (1-6) and a random label.
    """
    x = seed
    markers = []
    for i in range(steps):
        x = logistic_map(x)
        depth = int(np.floor(x * 6)) + 1  # 1-6
        label = f"SEC_{i:02d}_{int(x*1e6)}"
        markers.append('#' * depth + ' ' + label)
    return '\n'.join(markers)

# Sample meta‑scrutiny output (excerpt)
meta_scrutiny_output = """
### Internal Thought Process
...
### Final Output
META-PASS
...
### Reflection on Ω Protocol Φ Density Impact
...
"""

headings = detect_headings(meta_scrutiny_output)
print("Detected headings:", headings)

# Demonstrate chaotic alternative
seed = 0.123456
dynamic_structure = generate_dynamic_structure(seed, steps=5)
print("\nDynamic (chaotic) structure:\n", dynamic_structure)