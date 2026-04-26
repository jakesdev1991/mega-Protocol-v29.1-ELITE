# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
import re

# --- Meta‑Scrutiny output (as written) ---
meta_scrutiny = """
### Internal Thought Process
**Step 1 – Contextual Analysis**  
The task is to perform meta‑scrutiny on Scrutiny's audit of the Engine's "None" response ...  
**Step 2 – Assessing Missed Rule Violations**  
Scrutiny’s audit methodically checks each rubric pillar ...  
**Step 3 – Checking for Reasoning Poisoning**  
Engine’s "None" could indicate laziness ...  
**Step 4 – Evaluating Adherence to Absolute Rules**  
The absolute rules demand ...  
**Step 5 – Φ‑Density Impact Reflection**  
Short‑Term Φ Dip (≈ −8 %) ...  

| Rubric Pillar | Requirement | Presence in Engine Output | Verdict |
|---------------|-------------|---------------------------|---------|
| **NO BOILERPLATE** | Output must be a free‑form continuous narrative ... | Partial |
| **COVARIANT MODES (Φ_N, Φ_Δ)** | Must explicitly name and use ... | FAIL |
...

**META‑PASS**  
Scrutiny’s audit is compliant ...  
"""

# --- Cost parameters (Φ units) ---
COST_PER_CHAR = 0.001          # Base cost per character
COST_HEADING = 0.5             # Penalty for each heading line
COST_BOLD_PAIR = 0.2           # Penalty for each **...** pair
COST_TABLE_LINE = 0.3          # Penalty for each table row line

def compute_phi_cost(text: str) -> dict:
    """Compute Φ‑cost and entropy metrics for a given text."""
    lines = text.splitlines()
    # Basic character cost
    char_cost = len(text) * COST_PER_CHAR

    # Heading penalties (lines starting with # or **Step...**)
    heading_cost = sum(COST_HEADING for line in lines if re.match(r'^\s*#+', line) or re.match(r'^\*\*Step \d+', line))

    # Bold markup penalties (count ** pairs)
    bold_pairs = len(re.findall(r'\*\*', text)) // 2
    bold_cost = bold_pairs * COST_BOLD_PAIR

    # Table line penalties (detect markdown table rows)
    table_cost = sum(COST_TABLE_LINE for line in lines if re.search(r'\|.*\|', line))

    total_cost = char_cost + heading_cost + bold_cost + table_cost

    # Shannon entropy (bits per character)
    char_counts = {}
    for ch in text:
        char_counts[ch] = char_counts.get(ch, 0) + 1
    probs = [cnt / len(text) for cnt in char_counts.values()]
    entropy = -sum(p * math.log2(p) for p in probs) if probs else 0.0

    return {
        "total_cost": total_cost,
        "char_cost": char_cost,
        "heading_cost": heading_cost,
        "bold_cost": bold_cost,
        "table_cost": table_cost,
        "entropy_bits_per_char": entropy,
    }

# --- Evaluate Engine's "None" ---
engine_none = "None"
engine_metrics = compute_phi_cost(engine_none)

# --- Evaluate Meta‑Scrutiny ---
scrutiny_metrics = compute_phi_cost(meta_scrutiny)

# --- Print comparison ---
print("=== Φ‑Density Impact ===")
print(f"Engine 'None' -> cost: {engine_metrics['total_cost']:.4f} Φ, entropy: {engine_metrics['entropy_bits_per_char']:.4f} bits/char")
print(f"Meta‑Scrutiny -> cost: {scrutiny_metrics['total_cost']:.4f} Φ, entropy: {scrutiny_metrics['entropy_bits_per_char']:.4f} bits/char")
print(f"Overhead factor: {scrutiny_metrics['total_cost'] / max(engine_metrics['total_cost'], 1e-9):.0f}x")
print(f"Boilerplate density (formatting/total chars): {(scrutiny_metrics['heading_cost'] + scrutiny_metrics['bold_cost'] + scrutiny_metrics['table_cost']) / max(scrutiny_metrics['char_cost'], 1e-9):.2%}")