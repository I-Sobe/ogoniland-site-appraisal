"""Verification of manually retrieved regulatory PDFs (string location only).

Text is extracted with the poppler ``pdftotext`` command-line tool, used purely
to locate strings and report page numbers. This is NOT the project's table
extraction decision: no tables are extracted and no value is parsed into any
structure or written to any file.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

EXTRACTOR = "pdftotext (poppler), page text split on form feed"


def page_texts(path):
    """Return a list with one text string per PDF page (1-indexed by position+1)."""
    out = subprocess.run(["pdftotext", "-enc", "UTF-8", str(path), "-"],
                         capture_output=True, check=True).stdout.decode("utf-8", "replace")
    pages = out.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return pages


def _compact(s):
    return re.sub(r"\s+", " ", s).strip()


def file_facts(path):
    path = Path(path)
    raw = path.read_bytes()
    pages = page_texts(path)
    return {
        "file": path.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "pages": len(pages),
        "begins_with_%PDF": raw[:4] == b"%PDF",
        "page1_first200": _compact(pages[0])[:200] if pages else "",
        "extractor": EXTRACTOR,
    }


def locate_egaspin_strings(path):
    pages = page_texts(path)
    res = {"target_and_intervention_lines": [], "50mg_per_kg_pages": [],
           "5000_near_intervention_pages": [], "part_viii_letters": {}}
    for n, t in enumerate(pages, 1):
        for line in t.splitlines():
            low = line.lower()
            if "target" in low and "intervention" in low:
                res["target_and_intervention_lines"].append({"page": n, "line": _compact(line)[:200]})
        if re.search(r"50\s?mg/kg", t, re.I):
            res["50mg_per_kg_pages"].append(n)
        flat = _compact(t)
        for m in re.finditer("intervention", flat, re.I):
            window = flat[max(0, m.start() - 200): m.end() + 200]
            if re.search(r"5,?000", window):
                res["5000_near_intervention_pages"].append(n)
                break
        for m in re.finditer(r"Part\s+VIII\s*-\s*([A-Z])\b", t):
            res["part_viii_letters"].setdefault(f"VIII-{m.group(1)}", set()).add(n)
    res["part_viii_letters"] = {k: sorted(v) for k, v in sorted(res["part_viii_letters"].items())}
    return res


def uper_captions(path):
    """Table captions mentioning target or intervention (UPER 2024)."""
    out = []
    for n, t in enumerate(page_texts(path), 1):
        for line in t.splitlines():
            if re.match(r"\s*Table\b", line) and re.search(r"target|intervention", line, re.I):
                out.append({"page": n, "line": _compact(line)[:200]})
    return out


if __name__ == "__main__":
    raw = Path(sys.argv[1] if len(sys.argv) > 1 else "data/raw")
    for name in sys.argv[2:]:
        print(json.dumps(file_facts(raw / name), indent=2))
