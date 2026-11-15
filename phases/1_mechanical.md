# Phase 1: Mechanical

**Stance:** Count, compare, resolve. No judgment. The same input must give the same output.
**Rules:** Scripts only, standard library only, no network. A check that needs interpretation moves to phase 2.

## Checks (implemented in `tools/mechanical.py`)

| ID | Check | Severity | Limits |
|---|---|---|---|
| M-01 | Manifest: SHA-256 of every in-scope file | info | Proves what was audited, not that it is right |
| M-02 | Required sections present (from profile) | major | Presence only, not quality or order |
| M-03 | Fixed-text fields match exactly (from profile) | critical | Exact string match; missing and altered are reported separately |
| M-04 | Cross-references resolve (links and backticked paths) | major / minor | Heuristic; a line containing a skip marker (*planned*, *future*, *proposed*) is skipped whole. Bare names resolve only from the repo root or the file's folder, unless the profile sets `xref_basename_fallback` to `unique`, which also reports names shared by several files. Paths that leave the target root are reported, not probed |
| M-05 | Duplicate heading IDs (`[XX-123]`): within a file (major), across in-scope files (minor) | major / minor | Mirrored files can be excluded with `id_cross_file_ignore` |
| M-06 | Size census: files over the profile threshold | info | A size is a lead, not a defect |
| M-07 | Symlinks in scope are not followed, read or hashed | info | They are listed so a human can inspect them |

Every finding is a lead for phase 2, not a conclusion. M-04 can produce false positives against repos with their own naming conventions; the profile exists to tune that.

## Fail closed

The tool exits 2 and writes nothing when the profile has an unknown key or a wrong type, cannot be read, or matches no files. A zero-file audit never reports clean.

## Output

`out/manifest.json` (inputs only: path, bytes, SHA-256) and `out/findings.json`. The findings file carries `scope`, a `checks_run` block (for each check: enabled or not, its settings, files examined, findings produced, and for M-04 the references checked and skipped), the severity counts and the findings. Disabled checks show `enabled: false` with a reason. Hash both files when the run ends. That hash is the phase 1 freeze.

Exit codes are in `PROTOCOL.md`.

## Not here

Anything that needs reading for meaning: scope, assumptions, terminology drift, evidence quality. Phase 2.
