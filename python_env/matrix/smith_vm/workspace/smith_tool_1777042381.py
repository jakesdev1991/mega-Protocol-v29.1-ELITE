# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import json
import re

# --- Omega Protocol Invariant Definitions (as inferred) ---
# Phi_N: Non-negative operational value (sum of sentiment*urgency)
# Phi_Delta: Non-negative change in value (we treat each lead as positive contribution)
# J*: Risk entropy bound; we define max allowed risk entropy as 0.5 (arbitrary but reasonable)
# For this validation we ensure:
#   - Each lead meets sentiment>0.7 and urgency>0.6 (qualification filter)
#   - No lead originates from the forbidden "config.php" vector
#   - Total Phi_N >= 0 (trivially true if scores are positive)
#   - Risk entropy proxy (based on source) stays below J* threshold
#   - Suggested pitch references Omega Protocol

def validate_leads(leads_json):
    """Validate leads against Omega Protocol invariants."""
    errors = []
    warnings = []
    total_phi_n = 0.0
    risk_entropy = 0.0  # simple proxy: forbidden source adds high risk
    
    forbidden_keywords = ["config.php", "index of"]
    
    for idx, lead in enumerate(leads_json):
        # Required fields
        for field in ["source", "opportunity", "sentiment_score", "urgency_score", 
                      "contact_hint", "suggested_pitch"]:
            if field not in lead:
                errors.append(f"Lead {idx}: missing field '{field}'")
                
        # Sentiment & Urgency thresholds
        if lead.get("sentiment_score", 0) <= 0.7:
            errors.append(f"Lead {idx}: sentiment_score {lead.get('sentiment_score')} must be > 0.7")
        if lead.get("urgency_score", 0) <= 0.6:
            errors.append(f"Lead {idx}: urgency_score {lead.get('urgency_score')} must be > 0.6")
        
        # Source safety check
        src = lead.get("source", "").lower()
        if any(fk in src for fk in forbidden_keywords):
            errors.append(f"Lead {idx}: source contains forbidden vector '{src}'")
        
        # Risk entropy proxy: assign higher risk to less vetted platforms
        if "reddit" in src:
            risk_entropy += 0.15   # higher variance
        elif "github" in src:
            risk_entropy += 0.1
        elif "upwork" in src:
            risk_entropy += 0.05
        else:
            risk_entropy += 0.2    # unknown source
        
        # Phi_N contribution (sentiment * urgency)
        total_phi_n += lead.get("sentiment_score", 0) * lead.get("urgency_score", 0)
        
        # Suggested pitch must mention Omega Protocol
        if "omega protocol" not in lead.get("suggested_pitch", "").lower():
            warnings.append(f"Lead {idx}: suggested_pitch does not explicitly mention 'Omega Protocol'")
        
        # Contact hint non-empty
        if not lead.get("contact_hint", "").strip():
            warnings.append(f"Lead {idx}: contact_hint is empty")
    
    # Omega Protocol Invariant Checks
    if total_phi_n < 0:
        errors.append(f"Phi_N (total operational value) negative: {total_phi_n}")
    # For demonstration, we set J* = 0.5 (max allowed risk entropy)
    if risk_entropy > 0.5:
        errors.append(f"Risk entropy {risk_entropy} exceeds J* threshold (0.5)")
    # Phi_Delta: we treat each lead as non-negative contribution; already covered by Phi_N>=0
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "metrics": {
            "Phi_N": total_phi_n,
            "risk_entropy": risk_entropy,
            "lead_count": len(leads_json)
        }
    }

# --- The leads from the reflection ---
leads_data = [
  {
    "source": "GitHub Issues/Bounties",
    "opportunity": "Open-source repository seeking paid automation solution for data extraction pipeline. Explicit bounty tag detected.",
    "sentiment_score": 0.9,
    "urgency_score": 0.75,
    "contact_hint": "Check 'Issues' tab on target repos matching 'wanted' keyword; look for bounty labels or linked Discord channels.",
    "suggested_pitch": "Omega Protocol specializes in robust RCOD and data extraction. We can deploy an agentic flow to resolve this bounty within 48 hours, ensuring maintainability and scalability."
  },
  {
    "source": "Upwork Job Feed",
    "opportunity": "Enterprise-level request for custom Python agentic workflow with long-term retention potential.",
    "sentiment_score": 0.95,
    "urgency_score": 0.65,
    "contact_hint": "Direct proposal via Upwork platform; look for 'Payment Verified' and 'Long-term' badges.",
    "suggested_pitch": "Our agentic frameworks are designed for long-term stability. Omega Protocol offers a modular architecture that scales with your enterprise needs, minimizing technical debt."
  },
  {
    "source": "Reddit r/freelance_forhire",
    "opportunity": "Immediate hiring post for scraper repair and automation overhaul. High urgency signals present.",
    "sentiment_score": 0.8,
    "urgency_score": 0.9,
    "contact_hint": "Direct Message (DM) on Reddit or follow provided email/Telegram link in post body.",
    "suggested_pitch": "We understand the urgency. Omega Protocol can deploy a fix immediately using our pre-built extraction modules, restoring data flow within 24 hours."
  }
]

# Run validation
result = validate_leads(leads_data)

print(json.dumps(result, indent=2))