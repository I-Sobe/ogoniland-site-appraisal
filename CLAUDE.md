# CLAUDE.md

Instructions for any Claude Code session working in this repository.

## Scope discipline
You implement one bounded task spec per session. You touch only the files that spec lists. Work that is not in the spec is reported, not done. `docs/CHANGELOG.md` is a standing exception to every task spec's file list. You always append your session entry to it, whether or not the spec names it.

## What you do not decide
Screening thresholds, CSM logic, delineation verdicts, technology selection and any regulatory interpretation are settled in chat and handed to you as parameters. You never choose one.

## Provenance
Every parameter, threshold, regulatory value and physical constant carries a citation to source document and page, recorded in the code itself, not only in prose. A value that must be assumed is labelled as an assumption in the code. No row enters `data/processed/` without `source_doc` and `source_page`.

## Stop rule
If a required value, threshold or source is missing, stop and report. Do not infer, interpolate or invent one.

## Data handling
`data/raw/` is never edited or written to by code. `data/interim/` holds pre-QA extraction output. `data/processed/` holds validated tables only.

## Deliverable formats
Notebook deliverables go under `notebooks/`. All reusable logic lives as importable modules under `src/ogoniland_appraisal/`, never as notebook cells, because later builds import it.

## Environment
Compiled dependencies may be blocked by Windows Application Control on this machine. If an import fails for that reason, report it. Do not attempt to repair, rebuild or switch the environment.

## Record keeping
You own `docs/CHANGELOG.md` and write to it at the close of every session. You never write to `docs/DECISIONS.md`; that file records decisions made in chat and is not yours to edit.

## Session close
Before ending any session, append one entry to `docs/CHANGELOG.md` in exactly this format:

```
## [YYYY-MM-DD: hh:mm:ss] Session N — <short title>
**Changed:** <files created or modified, one line each>
**Untested:** <what was not verified, and why>
**Surprised:** <anything that did not behave as the spec assumed; "nothing" if so>
```
