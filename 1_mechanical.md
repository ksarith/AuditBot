# Phase 1: Mechanical

**Stance:** Count, compare, resolve. No judgment. The same input must give the same output.
**Rules:** Scripts only, standard library only, no network. A check that needs interpretation moves to phase 2.

## Checks (implemented in `tools/mechanical.py`)

| ID | Check | Severity | Limits |
|---|---|---|---|
| M-01 | Manifest: SHA-256 of every in-scope file | info | Proves what was audited, not that it is right |
| M-02 | Required sections present (from profile) | major | Presence only, not quality or order |
| M-03 | Fixed-text fields match exactly (from profile) | critical | Exact string match; missing and altered are reported separately |
| M-04 | Cross-references resolve (links and backticked paths) | major / minor | Heuristic; lines marked *planned*, *future* or *proposed* are skipped |
| M-05 | Duplicate IDs within one file (`[XX-123]` in headings) | major | Does not compare across files |
| M-06 | Size census: files over the profile threshold | info | A size is a lead, not a defect |

Every finding is a lead for phase 2, not a conclusion. M-04 in particular can produce false positives against repos with their own naming conventions; the profile exists to tune that.

## Output

`out/manifest.json` and `out/findings.json` (fields in `templates/finding.md`). Hash both when the run ends. That hash is the phase 1 freeze.

## Not here

Anything that needs reading for meaning: scope, assumptions, terminology drift, evidence quality. Phase 2.
