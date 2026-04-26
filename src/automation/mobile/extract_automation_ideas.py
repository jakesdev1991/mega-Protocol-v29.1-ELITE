# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import docx
import os

def extract_text(file_path):
    doc = docx.Document(file_path)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

base_path = "/home/jake/Downloads/training/data/automation_ideas/automation all devices"
files = ["understanding_automation.docx", "A16_Skeleton_Dump.md.docx"]

output_path = "/home/jake/Downloads/training/data/automation_ideas/extracted_ideas.txt"

with open(output_path, "w") as out:
    for f in files:
        f_path = os.path.join(base_path, f)
        if os.path.exists(f_path):
            out.write(f"--- CONTENT FROM {f} ---\n")
            out.write(extract_text(f_path))
            out.write("\n\n")

print(f"✅ Extracted text to {output_path}")
