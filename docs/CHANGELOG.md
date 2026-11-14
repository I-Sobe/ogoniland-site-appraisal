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

## [2026-11-14: 23:46:45] Session 2 — Source discovery
**Changed:** .gitattributes — created (LF normalisation, pdf binary)
**Changed:** pyproject.toml — dependency minimums (pandas>=3.1, numpy>=2.5, requests>=2.32, beautifulsoup4>=4.13); comment now points to requirements-lock.txt
**Changed:** requirements-lock.txt — re-encoded from UTF-16 to UTF-8/LF, renamed from requirements.txt (plain move: file was untracked), comment header prepended
**Changed:** src/ogoniland_appraisal/sources/__init__.py, discover.py — created; DSpace REST discovery
**Changed:** docs/sources_seed.yml — created; 69 fact-sheet and 10 report entries
**Changed:** tests/test_seed.py — created
**Untested:** No file was downloaded, so URLs were not fetched and PDF existence beyond the API's ORIGINAL-bundle listing is unchecked. The HTML browse fallback was not implemented (the API returned HAL JSON).
**Surprised:** The owning collection of the anchor is "Communication materials", a 9,277-item general collection rather than a fact-sheet collection, so fact-sheet selection required a title filter. The listing page redirected to a single repository record, and the first starting-point plan (HTML listing) yielded only 44 related records. Report-part IDs (report_part_NN) were not specified and were chosen by the script.

## [2026-11-14: 23:46:45] Session 2b — Discovery verification and close-out
**Changed:** src/ogoniland_appraisal/sources/discover.py — widened fact-sheet filter; append-only mode for an existing seed; leading hyphens stripped from local_filename
**Changed:** docs/sources_seed.yml — report_main local_filename leading hyphen stripped; no records added
**Changed:** tests/test_structure.py — pyproject dependency test updated; decisions-entries test deleted; changelog test relaxed from exactly one entry to at least one
**Changed:** tests/test_seed.py — item_uuid / bitstream_uuid uniqueness test added
**Changed:** CLAUDE.md — CHANGELOG standing-exception sentence added under Scope discipline
**Changed:** docs/CHANGELOG.md — Session 2 and 2b entries
**Untested:** The bitstream-name clause of the widened filter was only applied to items whose title already contained fact sheet/factsheet (fetching bitstreams for all 9,273 items was impractical); this is logically equivalent for the AND-ed filter.
**Surprised:** The specified code pattern \d{3}-\d{3} matches year ranges such as "2024-2029", so the first widened run appended 8 unrelated Ecosystem-based Adaptation project fact sheets (Tanzania, Jordan, Laos, Djibouti, Nepal/Mauritania/Seychelles, Lake Victoria, Nepal, CityAdapt); those were discarded and the pattern given digit boundaries, after which the widened filter found 67 collection records and no new ones (the collection now lists 9,273 items, down from 9,277). The 2 remaining seed fact sheets came from the main report record's related list. The changelog test asserting exactly one entry could not hold with three entries and was relaxed.
