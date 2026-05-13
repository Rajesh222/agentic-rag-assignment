# Meridian Consulting Policy Corpus

This is the test corpus for the Senior AI Engineer technical assessment (AIE-2026-01).

## Contents

- `metadata.json` — authoritative metadata for every document: category, department, effective date, and supersession relationships. Your agent MUST respect this.
- `eval_questions.json` — 15 test questions covering single-doc, composition, contradiction, supersession, and out-of-scope scenarios.
- `*.md` / `*.pdf` — 42 fictional policy documents for a fictional company called Meridian Consulting.

## Key things your agent must handle

1. **Supersession**: some documents have a newer version. `metadata.json` records this via `superseded_by` / `supersedes` fields. By default your agent should answer from the current (non-superseded) document.

2. **Contradictions**: some documents conflict with each other. Your agent must detect and surface these, not silently pick one.

3. **Composition**: some questions require combining information across multiple documents.

4. **Out-of-scope**: some questions cannot be answered from the corpus. Your agent must refuse rather than guess.

5. **Cross-lingual**: the corpus is English, but questions may be asked in Arabic. Arabic answers with English citations are expected.

## How to run

Place this folder at `./policy_corpus/` in your repository root and point your ingestion pipeline at it.

Good luck.
