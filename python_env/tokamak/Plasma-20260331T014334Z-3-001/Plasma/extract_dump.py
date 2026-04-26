# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import xml.etree.ElementTree as ET
import re
import os

def extract_source_code(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Namespaces
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    all_text = []
    for p in root.findall('.//w:p', ns):
        line = ""
        for t in p.findall('.//w:t', ns):
            if t.text:
                line += t.text
        all_text.append(line)
    
    # Files mapping
    files = {}
    current_file = None
    
    # Patterns for file headers (e.g., "1. Pulse_Phase_Manager.hpp")
    file_header_pattern = re.compile(r'^(\d+)\.\s+([\w\.-]+\.(hpp|cpp|h|c))$')
    
    for line in all_text:
        match = file_header_pattern.match(line.strip())
        if match:
            current_file = match.group(2)
            files[current_file] = []
        elif current_file:
            files[current_file].append(line)
            
    # Write files
    for filename, lines in files.items():
        # Strip potential garbage or empty lines at the end
        content = "\n".join(lines).strip()
        with open(filename, 'w') as f:
            f.write(content)
            print(f"Extracted: {filename}")

if __name__ == "__main__":
    extract_source_code('tmp_dump/word/document.xml')
