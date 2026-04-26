# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Lead Validation Script
-------------------------------------
Validates a JSON array of freelance leads against:
  - Required fields
  - Sentiment > 0.7
  - Urgency > 0.6
  - Ethical flag (optional: reject leads sourced from vulnerability dorks)
Optionally computes a simple Φ-density proxy: Φ ≈ Σ(sentiment * urgency)
"""

import json
import sys
from typing import List, Dict, Any

# -------------------- Configuration --------------------
SENTIMENT_THRESHOLD = 0.7
URGENCY_THRESHOLD   = 0.6
REQUIRED_KEYS = {
    "source",
    "opportunity",
    "sentiment_score",
    "urgency_score",
    "contact_hint",
    "suggested_pitch"
}
# Leads sourced from the vulnerability dork are considered unethical.
UNETHICAL_SOURCES = {"index of config.php"}  # extend if needed

# -------------------- Validation Functions --------------------
def validate_lead_structure(lead: Dict[str, Any]) -> List[str]:
    """Return list of missing/invalid keys."""
    missing = REQUIRED_KEYS - lead.keys()
    extra   = lead.keys() - REQUIRED_KEYS
    errors = []
    if missing:
        errors.append(f"Missing keys: {missing}")
    if extra:
        errors.append(f"Unexpected keys (ignored): {extra}")
    # Type checks
    if not isinstance(lead.get("sentiment_score"), (int, float)):
        errors.append("sentiment_score must be numeric")
    if not isinstance(lead.get("urgency_score"), (int, float)):
        errors.append("urgency_score must be numeric")
    return errors

def validate_lead_values(lead: Dict[str, Any]) -> List[str]:
    """Check thresholds and ethical constraints."""
    errs = []
    s = lead["sentiment_score"]
    u = lead["urgency_score"]
    if not (SENTIMENT_THRESHOLD < s <= 1.0):
        errs.append(f"sentiment_score {s} not > {SENTIMENT_THRESHOLD} and ≤ 1.0")
    if not (URGENCY_THRESHOLD < u <= 1.0):
        errs.append(f"urgency_score {u} not > {URGENCY_THRESHOLD} and ≤ 1.0")
    source = lead["source"].lower()
    if any(flag in source for flag in UNETHICAL_SOURCES):
        errs.append(f"Lead source '{lead['source']}' flagged as unethical")
    return errs

def compute_phi_density(leads: List[Dict[str, Any]]) -> float:
    """Simple proxy: Φ ≈ Σ(sentiment * urgency) for qualified leads."""
    return sum(l["sentiment_score"] * l["urgency_score"] for l in leads)

# -------------------- Main Execution --------------------
def main(json_input: str) -> None:
    try:
        data = json.loads(json_input)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print("❌ Expected a JSON array at top level.", file=sys.stderr)
        sys.exit(1)

    qualified: List[Dict[str, Any]] = []
    all_errors: List[str] = []

    for idx, lead in enumerate(data):
        if not isinstance(lead, dict):
            all_errors.append(f"Lead #{idx} is not an object")
            continue
        struct_errs = validate_lead_structure(lead)
        value_errs  = validate_lead_values(lead)
        if struct_errs or value_errs:
            all_errors.extend([f"Lead #{idx}: {e}" for e in struct_errs + value_errs])
        else:
            qualified.append(lead)

    if all_errors:
        print("❌ Validation failed:", file=sys.stderr)
        for err in all_errors:
            print("  -", err, file=sys.stderr)
        sys.exit(1)

    # If we reach here, all leads are qualified.
    phi = compute_phi_density(qualified)
    print("✅ All leads passed validation.")
    print(f"🔢 Number of qualified leads: {len(qualified)}")
    print(f"📊 Approximate Φ-density (Σ sentiment*urgency): {phi:.3f}")
    # Optionally output the validated JSON
    print("\n🟢 Qualified Leads JSON:")
    print(json.dumps(qualified, indent=2))

if __name__ == "__main__":
    # Expect the JSON blob as stdin or as a command‑line argument.
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            input_json = f.read()
    else:
        input_json = sys.stdin.read()
    main(input_json)