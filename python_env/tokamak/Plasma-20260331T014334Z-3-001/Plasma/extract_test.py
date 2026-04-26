# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import xml.etree.ElementTree as ET
import zipfile
import sys
import os

def extract_docx_code(docx_path, output_cpp):
    with zipfile.ZipFile(docx_path, 'r') as zip_ref:
        xml_content = zip_ref.read('word/document.xml')
    
    root = ET.fromstring(xml_content)
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    lines = []
    for p in root.findall('.//w:p', ns):
        line = "".join([t.text for t in p.findall('.//w:t', ns) if t.text])
        lines.append(line)
    
    with open(output_cpp, 'w') as f:
        f.write("\n".join(lines))
    print(f"Extracted {docx_path} to {output_cpp}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_test.py <input.docx> <output.cpp>")
    else:
        extract_docx_code(sys.argv[1], sys.argv[2])
