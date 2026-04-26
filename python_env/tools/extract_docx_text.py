# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import xml.etree.ElementTree as ET
import sys
import os

def extract_text_from_xml(xml_content):
    root = ET.fromstring(xml_content)
    text = []
    # Namespaces for Word XML
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for p in root.findall('.//w:p', ns):
        para_text = []
        for r in p.findall('.//w:r', ns):
            for t in r.findall('.//w:t', ns):
                if t.text:
                    para_text.append(t.text)
        text.append("".join(para_text))
    return "\n".join(text)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_docx_text.py <path_to_document.xml>")
        sys.exit(1)
    
    sys.stdout.reconfigure(encoding='utf-8')
    xml_path = sys.argv[1]
    with open(xml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(extract_text_from_xml(content))
