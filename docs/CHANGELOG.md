# Changelog

Each entry follows the format: `## [YYYY-MM-DD] Session N — title`, then **Changed**, **Untested**, **Surprised**.

## [2026-11-13] Session 1 — Repository scaffold
**Changed:** .gitignore — created
**Changed:** CLAUDE.md — created
**Changed:** pyproject.toml — created
**Changed:** data/raw/.gitkeep, data/interim/.gitkeep, data/processed/.gitkeep, notebooks/.gitkeep — created
**Changed:** docs/DECISIONS.md, docs/CHANGELOG.md, docs/SOURCES.md — created
**Changed:** src/ogoniland_appraisal/__init__.py and extract/, screen/, csm/, diagnose/ subpackage __init__.py files — created
**Changed:** tests/__init__.py, tests/test_structure.py — created
**Untested:** Package installation (`pip install -e ".[dev]"`) was not run, per spec; tests ran against src/ via path insertion, not an installed package.
**Surprised:** The target directory already contained a git repository with two commits (0803b13, e44e87e), a modified README.md and an untracked requirements.txt; both were left untouched. Of the files on the original create list, only README.md already existed; it was excluded from this session by Amendment 1.
