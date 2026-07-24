#!/usr/bin/env python3
"""Prueft, ob das erzeugte CV-PDF die Kern-Barrierefreiheitsmerkmale traegt.

Faellt mit Exit-Code 1, wenn Tags, Strukturbaum oder Sprache fehlen — so
kann kein untagged PDF versehentlich veroeffentlicht werden.
"""

import sys

from pypdf import PdfReader

path = sys.argv[1] if len(sys.argv) > 1 else "cv.pdf"
root = PdfReader(path).trailer["/Root"]

checks = {
    "getaggt (/MarkInfo /Marked)": bool((root.get("/MarkInfo") or {}).get("/Marked")),
    "Strukturbaum (/StructTreeRoot)": "/StructTreeRoot" in root,
    "Dokumentsprache (/Lang)": bool(root.get("/Lang")),
    "Titelanzeige (DisplayDocTitle)": bool((root.get("/ViewerPreferences") or {}).get("/DisplayDocTitle")),
}

ok = all(checks.values())
for name, passed in checks.items():
    print(f"  [{'OK' if passed else 'FEHLT'}] {name}")

if not ok:
    print("PDF ist NICHT barrierefrei — Build abgebrochen.")
    sys.exit(1)
print("PDF-Barrierefreiheit bestaetigt.")
