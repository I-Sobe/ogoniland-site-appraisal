"""Structural tests for the repository scaffold (standard library only)."""
import importlib
import re
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# README.md is deliberately excluded (Amendment 1).
REQUIRED_FILES = [
    ".gitignore",
    "CLAUDE.md",
    "pyproject.toml",
    "data/raw/.gitkeep",
    "data/interim/.gitkeep",
    "data/processed/.gitkeep",
    "docs/DECISIONS.md",
    "docs/CHANGELOG.md",
    "docs/SOURCES.md",
    "notebooks/.gitkeep",
    "src/ogoniland_appraisal/__init__.py",
    "src/ogoniland_appraisal/extract/__init__.py",
    "src/ogoniland_appraisal/screen/__init__.py",
    "src/ogoniland_appraisal/csm/__init__.py",
    "src/ogoniland_appraisal/diagnose/__init__.py",
    "tests/__init__.py",
    "tests/test_structure.py",
]
REQUIRED_DIRS = ["data/raw", "data/interim", "data/processed", "docs",
                 "notebooks", "src/ogoniland_appraisal", "tests"]
SUBPACKAGES = ["extract", "screen", "csm", "diagnose"]
HEADINGS = [
    "## Scope discipline", "## What you do not decide", "## Provenance",
    "## Stop rule", "## Data handling", "## Deliverable formats",
    "## Environment", "## Record keeping", "## Session close",
]


def lines(rel):
    return (ROOT / rel).read_text(encoding="utf-8").splitlines()


class TestStructure(unittest.TestCase):
    def test_1_paths_exist(self):
        for d in REQUIRED_DIRS:
            self.assertTrue((ROOT / d).is_dir(), d)
        for f in REQUIRED_FILES:
            self.assertTrue((ROOT / f).is_file(), f)

    def test_2_imports(self):
        pkg = importlib.import_module("ogoniland_appraisal")
        self.assertEqual(pkg.__version__, "0.1.0")
        for sub in SUBPACKAGES:
            importlib.import_module(f"ogoniland_appraisal.{sub}")

    def test_3_no_pandas_numpy_in_src(self):
        for p in SRC.rglob("*.py"):
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("import pandas", text, str(p))
            self.assertNotIn("import numpy", text, str(p))

    def test_4_gitignore(self):
        ls = lines(".gitignore")
        for required in ["data/raw/*", "!data/raw/.gitkeep",
                         "data/interim/*", "!data/interim/.gitkeep"]:
            self.assertIn(required, ls)
        self.assertFalse([l for l in ls if "data/processed" in l])

    def test_5_claude_md_headings(self):
        ls = lines("CLAUDE.md")
        for h in HEADINGS:
            self.assertIn(h, ls)

    def test_7_changelog_has_entries(self):
        # Originally "exactly one entry" (Session 1); the changelog now grows by
        # one entry per session, so assert at least one.
        self.assertGreaterEqual(
            len([l for l in lines("docs/CHANGELOG.md") if l.startswith("## [")]), 1)

    def test_8_pyproject_dependencies(self):
        with open(ROOT / "pyproject.toml", "rb") as fh:
            data = tomllib.load(fh)
        deps = data["project"]["dependencies"]
        names = [re.split(r"[<>=!~ ]", d, maxsplit=1)[0] for d in deps]
        self.assertEqual(sorted(names), ["beautifulsoup4", "numpy", "pandas", "requests"])
        for d in deps:
            self.assertIn(">=", d)
            self.assertNotIn("==", d)

    def test_11_gitignore_no_duplicates(self):
        ls = [l for l in lines(".gitignore") if l.strip()]
        self.assertEqual(len(ls), len(set(ls)))


if __name__ == "__main__":
    unittest.main()
