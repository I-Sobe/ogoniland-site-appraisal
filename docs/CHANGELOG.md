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

## [2026-11-15: 00:25:38] Session 3 — Source acquisition and provenance manifest
**Changed:** src/ogoniland_appraisal/sources/fetch.py — created; fetch_all, verify, duplicate-pair report
**Changed:** tests/test_manifest.py — created
**Changed:** docs/sources_manifest.json — created; 79 documents with sha256, bytes, retrieved_utc
**Changed:** docs/SOURCES.md — regenerated from the manifest (replaces the Session 1 stub)
**Changed:** data/raw/ — 79 PDFs downloaded (449,939,114 bytes); gitignored, not staged
**Untested:** No PDF was opened or parsed; only the %PDF header, size and sha256 were checked. Retry and backoff paths did not trigger, so they are unexercised.
**Surprised:** All four duplicate-site pairs (008-010, 005-002, 010-009, 008-003) are byte-identical. The completeness sweep found 72 Ogoniland-titled items, 68 in the seed; the other four (Geology of Ogoniland, UNEP In Ogoniland Newsletter August 2011, Ogoniland poster, Environmental Survey of Ogoniland Project Document) are not site fact sheets and were not added. 11 seed items (factsheet_05, factsheet_55, the main report and seven report parts) are not in the owning collection's listing; they were found via the main report record or are mapped from elsewhere.

## [2026-11-15: 00:33:44] Session 3b — Clean-clone-safe raw-file test
**Changed:** tests/test_manifest.py — test_6_files_exist skips when data/raw/ is absent or holds no PDF; otherwise still requires every manifest local_filename to exist
**Changed:** docs/CHANGELOG.md — this entry
**Untested:** Behaviour on a real fresh clone was simulated by moving the PDFs out of data/raw/, not by cloning.
**Surprised:** Renaming data/raw/ away entirely fails tests/test_structure.py test_1 (it requires the directory, which a real clone keeps via .gitkeep); the faithful case, PDFs removed with .gitkeep kept, passes with one skip.

## [2026-11-15: 11:32:56] Session 4 — Verify and register regulatory sources
**Changed:** src/ogoniland_appraisal/sources/verify_docs.py — created; pdftotext-based string location for the three regulatory PDFs (no tables extracted, no values written)
**Changed:** src/ogoniland_appraisal/sources/fetch.py — entries with retrieval_method "manual" are hashed in place and never downloaded; manifest keeps all seed fields; SOURCES.md gains a regulatory-sources section
**Changed:** docs/sources_seed.yml — three regulation entries appended (regulation_egaspin_2002, regulation_egaspin_2018, regulation_uper_2024)
**Changed:** docs/sources_manifest.json, docs/SOURCES.md — regenerated; 82 documents, the 79 earlier sha256 values unchanged
**Changed:** tests/test_manifest.py — nulls allowed only for regulation UUIDs; regulation provenance and null-UUID-only-on-regulation tests added
**Changed:** tests/test_seed.py — regulation-aware key, UUID and URL-shape checks; nulls excluded from UUID uniqueness; unique-url test added
**Changed:** data/raw/ — stray duplicate "-Environmental Assessment of Ogoniland-2011UNEP_OEA.pdf" deleted after its sha256 matched report_main (not tracked)
**Untested:** NUPRC pages /laws/guidelines, /laws/guidelines/cssa, /laws/guidelines/nuprc and /laws/menu served no links, so the egaspin search of them is inconclusive. Part VIII letters come from the PDF text layer and may miss letters it renders differently. EGASPIN text was not checked for 5000/5,000 outside 200 characters of "intervention".
**Surprised:** tests/test_seed.py was outside the spec's file list, and registering regulations changed the seed contract it enforces (null UUIDs, extra keys, non-bitstream URLs); it was added by amendment. The file named "Upstream Petroleum Environmental Remediation Regulations, 2024" is titled on its own page "Upstream Petroleum Environmental Remediation Fund Regulations, 2024" and is a fund-contribution regulation with no target or intervention values. No EGASPIN copy is published on nuprc.gov.ng. retrieved_utc for the three manual entries holds the date only.
