# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import csv
from datetime import date

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from business.sales_automation_engine import OmegaSalesEngine

CRM_FILE = os.path.join(PROJECT_ROOT, "official_launch", "business", "crm_tracker.csv")
PITCHES_FILE = os.path.join(PROJECT_ROOT, "official_launch", "docs", "GENERATED_PITCHES.md")

def generate_batch():
    engine = OmegaSalesEngine()
    leads_to_pitch = []
    
    # 1. Read leads that need pitches
    if not os.path.exists(CRM_FILE):
        print("❌ CRM file not found.")
        return

    rows = []
    with open(CRM_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows.append(header)
        for row in reader:
            # Check for "New (Scraped)" or "New" status
            if len(row) >= 4 and ("New (Scraped)" in row[3] or row[3] == "New"):
                leads_to_pitch.append(row)
                # Update status
                row[3] = "Pitch Generated"
                row[4] = "AI Pitch Created"
                row[5] = "Review & Send"
            rows.append(row)

    if not leads_to_pitch:
        print("ℹ️ No new leads found requiring pitches.")
        return

    print(f"🚀 [Pitch Gen] Generating {len(leads_to_pitch)} personalized pitches...")
    
    # 2. Generate Pitches
    pitches_output = f"# Generated Sales Pitches - {date.today()}\n\n"
    
    for lead in leads_to_pitch:
        company = lead[1]
        contact = lead[2]
        
        # Use NVIDIA for high-quality enterprise pitches
        pitch = engine.generate_personalized_pitch(
            company_name=company, 
            contact_person=contact, 
            context="Targeting high-end AI Infrastructure providers to license RCOD for 90% GPU cost reduction.",
            provider="nvidia",
            model="mistral-large"
        )
        
        pitches_output += f"## {company} | {contact}\n"
        pitches_output += f"**Pitch:**\n> {pitch}\n\n---\n\n"
        print(f"✅ Generated pitch for {company}")

    # 3. Save Pitches to File
    os.makedirs(os.path.dirname(PITCHES_FILE), exist_ok=True)
    with open(PITCHES_FILE, 'w', encoding='utf-8') as f:
        f.write(pitches_output)

    # 4. Update CRM file
    with open(CRM_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"\n✨ All pitches generated! Saved to: {PITCHES_FILE}")
    print(pitches_output)

if __name__ == "__main__":
    generate_batch()
