# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = r"C:\Users\Jakesdev1991\Downloads\training"
sys.path.append(PROJECT_ROOT)

from business.sales_automation_engine import OmegaSalesEngine

def send_attachment_followups():
    print("🚀 [Commercialization] Executing Attachment Correction Follow-up...")
    
    engine = OmegaSalesEngine()
    
    # Path to the Stealth Datasheet
    datasheet_path = os.path.join(PROJECT_ROOT, "business", "OMEGA_DATASHEET_STEALTH.md")
    
    targets = [
        {"name": "Josh Wolfe", "email": "josh.wolfe@luxcapital.com"},
        {"name": "Scott Nolan", "email": "scott@foundersfund.com"},
        {"name": "Vinod Khosla", "email": "vk@khoslaventures.com"}
    ]
    
    for t in targets:
        print(f"\n📡 Sending follow-up to {t['name']}...")
        
        subject = f"Enclosed: Omega Protocol Technical Datasheet ({t['name']})"
        
        body = f"""
Dear {t['name'].split(' ')[0]},

I realized that the Technical Datasheet mentioned in my previous message was not physically attached to the thread.

Please find the enclosed OMEGA_DATASHEET_STEALTH.md. It details the 90% reduction in associated GPU costs and the linear scaling benchmarks achieved via RCOD curvature gating.

I look forward to discussing how these invariants redefine the competitive moat for your deep-tech portfolio.

Best,

Jacob See
Founder & Creator, Omega Protocol
Phone: 217-799-8720
        """
        
        success = engine.send_email_to_lead(t['email'], subject, body, attachments=[datasheet_path])
        if success:
            print(f"✅ Follow-up sent to {t['email']} with attachment.")
        else:
            print(f"❌ Failed to send follow-up to {t['email']}.")

if __name__ == "__main__":
    send_attachment_followups()
