# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import zipfile
import xml.etree.ElementTree as ET
import sys

def get_docx_text(path):
    """
    Take the path of a docx file, return the text in html,
    memory efficient way.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
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
        print("Usage: python read_docx.py <path_to_docx>")
        sys.exit(1)
    
    docx_path = sys.argv[1]
    try:
        print(get_docx_text(docx_path))
    except Exception as e:
        print(f"Error: {e}")
