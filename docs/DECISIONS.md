# Decisions

Entries are written from chat; Claude Code must not add to this file.

2026-11-13 — Week 1 environment gate: passed, with a caveat

Decision: local VS Code is the execution runtime for Build 1. Colab remains the documented fallback, not the default.

Reasoning: the gate first failed with "An Application Control policy has blocked this file" on pandas._libs and on cryptography._rust. The cause was conda's base environment being active alongside the venv; conda deactivate cleared it and all imports then succeeded. Mechanism not fully established — most likely conda's DLL search path resolving a blocked dependency — but the behaviour is reproducible.

Mitigation: conda auto-activation disabled. If (base) appears in a prompt, treat it as the first suspect for any import failure.

Open: the Application Control policy is still active on this machine. Whether it blocks the unsigned executables FloPy downloads for MODFLOW 6 is untested. This remains a Build 2 gate and is not resolved.

[2026-11-13] Package layout deviates from Part 3

Decision: Code lives in src/ogoniland_appraisal/{extract,screen,csm,diagnose}/ as an installable package, not in the bare src/extract/ form given in Part 3 of the setup pack. Installed with pip install -e ".[dev]". Reasoning: Builds 2 and 3 import Build 1's modules, and Colab is a live fallback runtime. A bare src/ requires a sys.path shim in every notebook and breaks on a clean clone; an installed package gives one import path that behaves identically locally and in Colab. Rejected: literal Part 3 layout with a path shim; flat package at repo root. Both work today and cost a repo-wide rename once modules exist.

[2026-11-13] data/raw and data/interim are untracked

Decision: git ignores the contents of data/raw/ and data/interim/; data/processed/ is tracked. Reproducibility from a clean clone rests on docs/SOURCES.md carrying URL and sha256 per source document. Reasoning: UNEP PDFs are large and not ours to redistribute, and interim extraction output is pre-QA by definition — tracking it invites citing an unvalidated table. The manifest is a week 1 deliverable regardless. Rejected: committing raw PDFs (size, redistribution); ignoring all of data/ (makes the validated dataset, the primary public output, invisible in the repo).

[2026-11-13] pyproject.toml is the only environment file, and is unpinned

Decision: Session 1 declares dependencies in pyproject.toml only — no requirements.txt, no environment.yml — and declares pandas and numpy without version specifiers. Pins are added once an environment is proven to build. Reasoning: The Application Control policy already blocks the compiled pandas DLL in the FE miniconda env, so any pin written now is a guess at an environment that has not been shown to exist. Two dependency files would mean two sources of truth before either is proven. PDF-extraction and groundwater libraries are deliberately absent: they are tooling decisions not yet made. Rejected: pinning now against the blocked env; generating environment.yml for miniconda alongside pyproject.

[2026-11-13] Scaffold into the existing repository; README deferred

Decision: Session 1 scaffolds into the pre-existing ogoniland-csm repo as a third commit rather than initialising a fresh one. README.md is removed from Code's remit and written in chat at ship. Reasoning: The existing repo is the artifact that ships publicly in week 8; re-running the scaffold elsewhere would orphan it and force a manual reconciliation. The README is a hiring document, which is prose judgement, not implementation — and it already carries hand-written edits that Code has no basis to merge. Rejected: fresh directory (clean, but discards deliberate history and any remote); having Code merge into the existing README (delegates prose judgement to Code, which the workflow forbids).

[2026-11-13] Lower bounds in pyproject, exact pins in a lock file

Decision: pyproject.toml declares pandas>=3.1, numpy>=2.5. The freeze is renamed requirements-lock.txt, committed, and headed with a statement that it locks a known-working environment on Python 3.14.6 on this machine and is not a declaration. The lower bound on pandas is a deliberate target of pandas 3 semantics — copy-on-write and the string dtype default — not a transcription of the installed version. Reasoning: Colab remains the documented fallback and runs a different Python; exact pins in pyproject.toml would make pip install -e . fail there on a missing wheel. Code written against pandas 3 defaults would fail subtly rather than loudly on 2.x, and a silent dtype change in a provenance-carrying dataset is the worst available failure, so the floor stays at 3.1. Supersedes: the 2026-11-13 entry "requirements.txt is evidence, not a declaration", which resolved to deletion once pins were promoted. The file is retained and renamed instead. Consequence: the Colab bootstrap notebook will require a pandas upgrade cell and a runtime restart before the editable install.

[2026-11-13] .gitattributes added, for tracked outputs

Decision: .gitattributes is added in Session 2, with * text=auto eol=lf as its operative line. Reasoning: Corrects the rationale offered when this was raised. data/raw/ is gitignored, so git cannot normalise the hashed PDFs and their checksums are not at risk. The exposure is data/processed/ — tracked CSVs rewritten to CRLF on a Windows clone, breaking any hash recorded against them. That bites in week 4, but the file must exist before the first tracked data file does. Rejected: treating it as a binary-file problem, which would have produced a *.pdf binary rule that addresses nothing.

[2026-11-13] Session order: acquisition before extraction instrument

Decision: Session 2 is docs/SOURCES.md — download script, sha256 manifest, UNEP main report and fact sheets into data/raw/. The pdfplumber-versus-PyMuPDF decision follows it, boxed to one session against one real fact sheet. Reasoning: The extraction instrument cannot be trialled before the PDFs exist. Camelot requires Ghostscript and tabula requires Java — both compiled, both plausibly blocked by the live Application Control policy — so the realistic field is pdfplumber or PyMuPDF, and it is decided on evidence from a real document rather than by which package was installed first. Rejected: deciding the instrument first (no document to test against); screening values as Session 2 (not a Code task — see below).

[2026-11-13] Screening values are authored, not generated

Decision: data/processed/screening_values.csv is populated by hand from EGASPIN Part VIII-B. Claude Code may scaffold the empty file with its schema and citation columns and must never write a row. Reasoning: Every screening value is a regulatory interpretation carrying a document and page. Delegating population to Code would mean either invented values or scraped ones with no verified provenance, and the standing rule is that a model built on invented values is worse than no model.

[2026-11-13] New sources subpackage

Decision: Acquisition and provenance logic lives in src/ogoniland_appraisal/sources/, a fifth subpackage alongside extract, screen, csm and diagnose. Reasoning: Acquisition is not parsing, so it does not belong in extract, and it is reusable — Builds 2 and 3 acquire their own sources. A loose scripts/ directory would put it outside the importable, testable package. Rejected: folding it into extract/; a top-level scripts/ directory.

## [2026-11-14] Source acquisition splits into discovery and download
**Decision:** Session 2 discovers source URLs into `docs/sources_seed.yml` and
downloads nothing; Session 3 downloads from that reviewed list and writes the
sha256 manifest and `docs/SOURCES.md`.
**Reasoning:** The 67 fact sheets are individual records in UNEP's document
repository with non-derivable handles, so the URL list must be extracted from
pages rather than constructed. Splitting discovery from acquisition puts a human
review between link extraction and anything entering `data/raw/`, and a failed
discovery session costs nothing because it writes no data.
**Supersedes:** the 2026-11-13 entry "Session order: acquisition before
extraction instrument" in its session numbering only. The ordering principle —
acquisition before the extraction-instrument decision — stands.
**Rejected:** Claude enumerating the 67 URLs by hand (its fetch tool returns page
text with links stripped, so it cannot read the one field required); scraping PDF
links directly off the listing page (the listing links to record pages, not PDFs).

## [2026-11-14] requests and beautifulsoup4 added as acquisition dependencies
**Decision:** `pyproject.toml` gains `requests>=2.32` and `beautifulsoup4>=4.13`.
**Reasoning:** Discovery requires real HTML parsing. Both are already present in
the proven environment, so neither risks the Application Control policy, and a
regex over HTML would be the kind of silent failure this project cannot afford in
a provenance chain.
**Rejected:** `html.parser` from the standard library (workable but brittle
against DSpace markup); adding a YAML dependency, which the tests avoid by
reading the seed file with a minimal parser.

## [2026-11-14] Discovery routes through the DSpace collection, not a listing page
**Decision:** Fact-sheet URLs are discovered by resolving a known item through
the repository's REST API, following `owningCollection`, and enumerating that
collection. Seed entries carry `item_uuid` and `bitstream_uuid` alongside the
download URL, and `local_filename` comes from bitstream metadata rather than the
URL.
**Reasoning:** wedocs.unep.org has migrated to DSpace 7. Handle URLs now redirect
to `/items/<uuid>` and files are served from `/bitstreams/<uuid>/download`, so
the URL carries no filename and the 2011 page structure no longer exists. The
page previously specified as a listing is a single record whose related-materials
sidebar is demonstrably incomplete — it omits records known to exist. UUIDs are
the stable identifiers on this platform and will survive a further migration that
the download URLs may not.
**Supersedes:** the starting points and URL contracts in the 2026-11-14 Session 2
spec. The discovery-before-acquisition split is unaffected.
**Rejected:** scraping the related-materials sidebar (incomplete by observation);
constructing bitstream URLs from thumbnail paths (guesswork, and forbidden by the
no-invented-URLs rule).

## [2026-11-14] Repository search permitted; external search engines not
**Decision:** Code may use wedocs.unep.org's own discovery and browse endpoints.
The prohibition applies to Google, Bing and other external search engines.
**Reasoning:** The original wording was imprecise and ruled out the repository's
own index, which is the authoritative enumeration of its holdings. The concern
behind the rule was provenance — URLs arriving from a ranked third-party index
rather than from the publisher — and that concern does not apply here.

## [2026-11-14] Fact-sheet record count is not the site count
**Decision:** No stop rule, acceptance criterion or schema assertion may fix the
number of fact sheets, records or sites until week 2 extraction reads the main
report's tables.
**Reasoning:** Some fact-sheet records cover site ranges rather than single
sites, so records, fact sheets and site rows are three distinct populations.
UNEP states 67 fact sheets; the setup pack states 69 sites; the discovered
record count will match neither. Asserting any of them now would encode a guess
into a test.

## [2026-11-14] Four sites hold two fact-sheet records each
**Decision:** The seed list keeps all 69 records. Duplicate site codes — 008-010,
005-002, 010-009 and 008-003 — are resolved in week 2 by comparing the
downloaded files, not by choosing now.
**Reasoning:** 69 records cover 65 distinct site codes. Each duplicated pair has
distinct item and bitstream UUIDs, and in every pair one record's filename omits
"factsheet" and its title drops the standard prefix, suggesting a second upload
batch. If the two files in a pair share a sha256 the Session 3 manifest settles
it mechanically; if they differ, that difference is itself a provenance finding
and belongs in the QA report.
**Supersedes:** the 2026-11-14 entry "Fact-sheet record count is not the site
count" by making it concrete — the count mismatch is now measured, not
anticipated.
**Rejected:** dropping one of each pair at seed time (discards evidence before
anyone has looked at it); treating the 69 record count as confirmation of the
setup pack's 69 sites (coincidence — the distinct-site count is 65).

## [2026-11-14] Discovery filter widened before any download
**Decision:** Discovery re-runs with a filter matching "factsheet" as one word as
well as "fact sheet", before Session 3 downloads anything.
**Reasoning:** 65 distinct sites is two short of UNEP's stated 67 fact sheets,
and the original filter required a space that UNEP's own headings do not always
use. A missed record is unrecoverable once extraction starts and costs nothing to
check now.
**Rejected:** proceeding to download on the existing 69 (risks a silently
under-covered dataset); treating UNEP's 67 as authoritative over our count
(neither figure is verified, and the main report's tables arbitrate in week 2).

## [2026-11-14] Two Session 1 acceptance criteria withdrawn
**Decision:** The test asserting `docs/DECISIONS.md` contains no entries is
deleted outright. The test asserting exactly two unpinned dependencies is
rewritten to the current contract. `docs/CHANGELOG.md` becomes a standing
exception to every task spec's file list.
**Reasoning:** The DECISIONS test used file contents as a proxy for authorship
and cannot distinguish a human entry from a Code entry, so it fails precisely
when the file is being used correctly; the constraint is enforced by each spec's
file list instead. The CHANGELOG omission set a spec against a standing rule in
CLAUDE.md, and the standing rule should win.

## [2026-11-15: 00:05:00] Discovery closed at 69 seed records
**Decision:** Discovery is complete. The seed file stands at 69 fact-sheet and 10
report records and is the input to Session 3. UNEP's stated figure of 67 is read
as a count of repository records, not sites.
**Reasoning:** The widened filter matches exactly 67 records in the owning
collection, equal to UNEP's published figure; the seed's two additional fact
sheets reach it via the main report record's related list. Distinct site codes
number 65, so none of the three figures — 67, 69, 65 — is a site count until the
main report's tables arbitrate in week 2.
**Rejected:** trimming the seed to the collection's 67 (discards two records that
resolve and may be unique sites); treating 67 as a target to reach (it is a
record count, now explained).

## [2026-11-15: 00:05:00] Site-code regex requires digit boundaries
**Decision:** The widened discovery filter uses `\d{3}-\d{3}` with digit
boundaries. The unanchored form is withdrawn.
**Reasoning:** Unanchored, it matches inside longer digit runs, so year ranges
such as "2024-2029" read as site codes. The first widened run appended eight
unrelated Ecosystem-based Adaptation project fact sheets on that basis. Code
discarded them, restored the seed and anchored the pattern.
**Supersedes:** the filter given in the 2026-11-14 Session 2b spec.
**Rejected:** post-filtering by title keyword (treats the symptom and leaves the
pattern wrong for the next caller).

## [2026-11-15: 00:05:00] Session 1 acceptance criteria tested state, not contract
**Decision:** Three Session 1 tests are withdrawn or relaxed: no entries in
DECISIONS (deleted), exactly two unpinned dependencies (rewritten), exactly one
CHANGELOG entry (relaxed to at least one). No future spec asserts a count that
normal use of the repository will change.
**Reasoning:** Each encoded the state of the repository at the close of Session 1
rather than an invariant. All three failed as the repository was used correctly,
which trains the wrong reflex — relaxing tests to make a suite green.
**Rejected:** keeping them and amending per session (makes every future spec
carry test maintenance for a constraint better enforced by its file list).

## [2026-11-15: 00:20:00] The manifest is a dated snapshot, not a stable truth
**Decision:** `docs/SOURCES.md` and the JSON manifest both carry a generation
timestamp and a statement that the UNEP repository is a live system. Each
document records its own `retrieved_utc`.
**Reasoning:** The owning collection reported 9,277 items on one run and 9,273
less than an hour later. Items are being added and removed while we work, so a
manifest without a retrieval date claims more permanence than the source
supports. Reproduction from a clean clone depends on the sha256, not on the URL
continuing to resolve.
**Rejected:** recording only a single generation timestamp for the whole
manifest (loses per-document retrieval dates if acquisition spans sessions).

## [2026-11-15: 00:35:00] Duplicate fact-sheet records are byte-identical
**Decision:** All four duplicated site codes — 008-010, 005-002, 010-009,
008-003 — resolve to byte-identical PDFs. Both records of each pair stay in the
seed and the manifest; extraction deduplicates by sha256 and treats the pair as
one site.
**Reasoning:** Identical hashes prove a cataloguing artefact rather than two
documents, so no judgement is needed about which record wins. Keeping both is a
true record of what the repository publishes; dropping one would make the
manifest disagree with its source.
**Supersedes:** the 2026-11-14 entry "Four sites hold two fact-sheet records
each" in its open question only. The record counts in that entry stand.

## [2026-11-15: 00:35:00] Discovery is closed
**Decision:** The owning collection holds 72 Ogoniland-titled items; 68 are in
the seed and the four outside it are a geology paper, a newsletter, a poster and
a project document. Discovery is complete and is not revisited.
**Reasoning:** The title-only sweep is strictly broader than every filter used
previously, so nothing a narrower run could find remains unfound. Final figures:
67 records in the collection, matching UNEP's published figure; 69 fact sheets in
the seed, the extra two reached via the main report record; 4 exact duplicates;
65 distinct site codes.
**Open:** whether 65 is the site count the main report's tables use. Resolved in
week 2, not before.

## [2026-11-15: 00:35:00] Tests must pass on a clean clone
**Decision:** Any test depending on gitignored content skips when that content is
absent and asserts when it is present. Applied first to the manifest's
file-existence check.
**Reasoning:** The repository is the week 8 public deliverable and its suite is
the first thing a reviewer runs. A suite that fails on a fresh clone reads as a
broken project, and training the habit of relaxing tests to make a suite green is
worse than the failing test itself.

## [2026-11-15: 10:20:00] Regulatory sources registered with graded provenance
**Decision:** EGASPIN 2002, EGASPIN 2018 and the NUPRC Upstream Petroleum
Environmental Remediation Regulations 2024 enter the manifest as
`kind: "regulation"` with `retrieval_method: "manual"`, each carrying its source
URL, retrieval date and a provenance note stating the strength of its source.
**Reasoning:** Every screening value cites one of these, so the regulatory end of
the provenance chain cannot rest on unrecorded files. The three differ sharply in
authority — NUPRC's own server, a law-firm mirror, and a document-sharing upload
— and a manifest that recorded them identically would misrepresent what the
dataset rests on. A request for an official copy has been sent to NUPRC; if it
arrives it supersedes the mirror.
**Rejected:** excluding the 2018 copy for weak provenance (leaves the comparison
instrument missing with no better copy available); recording all three without
distinguishing their sources.

## [2026-11-15: 10:20:00] EGASPIN 2002 is the primary screening instrument
**Decision:** `screening_values.csv` is populated first from EGASPIN 2002 Part
VIII-F. EGASPIN 2018 is added as a second `instrument` for comparison. The
delineation diagnostic runs against 2002.
**Reasoning:** UNEP sampled in 2009-2011 and assessed against the 2002 edition,
so screening against 2002 reproduces their published findings and makes the
dataset checkable against its source. Screening primarily against 2018 would
produce exceedance counts that diverge from UNEP's with no stated reason.
Divergence between the two editions is a reportable finding, not a defect.
**Rejected:** 2018 as primary (breaks reconciliation with UNEP); 2002 alone
(ignores the edition in force today, which a partner-facing appraisal must
address).

## [2026-11-15: 11:20:00] Seed schema changes carry their test with them
**Decision:** `tests/test_seed.py` is on the file list of every session that
changes what a seed entry may contain. Registering `kind: "regulation"` entries
splits its key, uuid-format and uuid-uniqueness checks by kind rather than
relaxing them.
**Reasoning:** That file encodes the seed's data contract, so a session changing
the contract and omitting the test leaves Code to choose between a red suite and
an unspecified edit — neither of which is its decision to make. Splitting by kind
keeps every original assertion intact for the 79 fetched documents while
admitting regulations, which legitimately have no repository UUIDs.
**Rejected:** relaxing the checks for all entries (would let a malformed fetched
entry through); committing with three failing tests (a red suite in the public
deliverable); holding the commit (discards the session's verification work).

## [2026-11-15: 11:30:00] Regulation URLs are provenance records, not fetch targets
**Decision:** Entries with `kind: "regulation"` are exempt from the seed's
URL-shape check and need only be https. The recorded URL is the page the
document was retrieved from, even where that is a landing page rather than a
direct PDF link.
**Reasoning:** The shape check guards discovery output, where a malformed
bitstream URL is a defect. A manual retrieval URL records where a human actually
got the file; rewriting it into a direct link that was never used would make the
record less true, not more.

## [2026-11-15: 11:30:00] UPER 2024 is a funding instrument, not a screening one
**Decision:** The Upstream Petroleum Environmental Remediation Fund Regulations
2024 are registered and retained, but contribute no screening values. Screening
instruments remain EGASPIN 2002 (primary) and EGASPIN 2018 (comparison).
**Reasoning:** Verification of the file shows a 13-page gazetted regulation
establishing the Environmental Remediation Fund, with contribution rates as its
only table and no target or intervention values. It is the only official
NUPRC-hosted source in the manifest and bears directly on Build 3's cost basis,
which is flagged as the ramp's largest open risk.

## [2026-11-15: 11:30:00] No official EGASPIN is published by NUPRC
**Decision:** The mirror copies stand as the registered sources. If the NUPRC
email yields an official copy it supersedes them and the manifest is updated.
**Reasoning:** NUPRC's site is a client-rendered app whose laws routes were
enumerated from its own script bundle; no route, link text or filename contains
"egaspin", and none contains both "environmental" and "guidelines". Four
guideline pages served no links and are inconclusive. The UPER regulation was
found on the gazetted-regulations route, confirming the search method works
where documents exist.

## [2026-11-15: 12:40:00] Screening thresholds sourced to Table VIII-F1
**Decision:** The delineation diagnostic screens against the mineral oil row of
Table VIII-F1, EGASPIN 2002: soil/sediment intervention 5,000 mg/kg, target
50 mg/kg; groundwater intervention 600 µg/l, target 50 µg/l. Closure is
assessed against the intervention value, per Part VIII F section 6.6.
**Reasoning:** The 5,000 mg/kg figure cited throughout the literature is the
intervention value for mineral oil in section E of the table, not a separate
closure provision. Section 6.6 requires intervention values to be demonstrated
at the point of compliance, which is the regulatory basis for treating an
unbounded site as uncloseable.
**Supersedes:** the 2026-11-15 entry "The diagnostic keys off the intervention
value" in its account of where the two figures come from. Both are the same row
of the same table; they are not contradictory provisions. The decision to screen
against the intervention value stands, now for a sourced reason.

## [2026-11-15: 12:40:00] UNEP's TPH is mapped to EGASPIN's mineral oil
**Decision:** UNEP's reported TPH values are screened against EGASPIN's mineral
oil criteria. The mapping is recorded as a labelled assumption in the screening
module, not as an equivalence.
**Reasoning:** EGASPIN specifies mineral oil, conventionally a defined GC-FID
carbon range; UNEP reports TPH, whose definition varies by analytical method.
No other EGASPIN determinand corresponds to UNEP's primary measurement, so the
mapping is necessary, but it is an interpretation and the standing rule requires
assumptions to be labelled in code.
**Rejected:** treating the two as identical without comment; declining to screen
TPH at all, which would remove the project's primary determinand.

## [2026-11-15: 12:40:00] Table VIII-F1 row alignment is shifted
**Decision:** Transcription of Table VIII-F1 reads substance labels as sitting
one row below their values. Every transcribed row is checked against the Dutch
intervention values it derives from before entering screening_values.csv.
**Reasoning:** In the printed table the category header line carries the first
substance's values and Zinc has none, so an unshifted reading assigns every
metal the wrong value while still looking plausible. The shifted reading returns
chemically correct values throughout. Section E does not shift, having a single
substance.

## [2026-11-15: 19:15:00] screening_values.csv gains three columns
**Decision:** The schema becomes determinand, printed_determinand, medium,
target_value, intervention_value, unit, qualifier, basis, instrument, citation.
One row per determinand per medium; a medium with no published value gets no
row, and a missing value is empty rather than zero.
**Reasoning:** EGASPIN's `(dt)` marks a value as a detection threshold rather
than a concentration, which changes how it is compared and would otherwise be
lost. The printed names carry typographic errors that must be preserved for a
reader checking the page while code joins on a normalised name. Every soil value
is normalised to a standard soil of 10% organic matter and 25% clay, and the
screening module must know that to decide whether the soil-type correction
applies.
**Supersedes:** the `screening_values` schema in Part 3 of the setup pack.
**Rejected:** encoding the qualifier inside the value as text (breaks numeric
comparison); recording zero for an unspecified value (asserts a limit the
regulation does not set).
## [2026-11-15: 22:45:00] Table VIII-F1 section D shifts two rows, not one
**Decision:** In the PAH block, values sit two rows above their substance label,
not one. PAH (Total of 10) carries the soil pair 1 and 40 mg/kg and no
groundwater values; the five named PAHs carry groundwater values only.
**Reasoning:** The groundwater pairs 0.1/70, 0.02/5, 0.02/5, 0.005/1 and
0.002/0.5 match the Dutch values for naphthalene, anthracene, phenanthrene,
fluoranthene and benzo(a)anthracene exactly. A one-row shift would assign the
PAH-total soil values to naphthalene and leave the last named PAH unvalued.
**Supersedes:** the 2026-11-15 entry "Table VIII-F1 row alignment is shifted",
which stated a uniform one-row shift. Sections A, B and C shift by one; section
D shifts by two; section E does not shift.
**Rejected:** applying a uniform shift across all sections (misassigns the PAH
soil values and loses the PAH-total row).

## [2026-11-15: 22:45:00] Determinand keys are normalised; printed names preserved
**Decision:** `determinand` carries the correct chemical name; the printed form,
including EGASPIN's typographic errors, is preserved in `printed_determinand`.
A medium with no published value gets no row rather than a row with a dash.
**Reasoning:** The key is what sample data joins against, so carrying "pnenol"
or "napthalene" into it would propagate a typesetting error through the
screening module. The printed form is what a reader checking the page sees, so
both are needed. A dash in a numeric column is a string, which is the failure
the empty-not-zero rule exists to prevent.