# Changelog

## V0.0.2 (draft)

Source of each change: **R** = reproduced against the V0.0.1 code before changing it; **S** = suggestion from a review, adopted without a reproduction. Reviewers: Grok, ChatGPT.

**Fail closed**
- Unknown or wrongly typed profile keys are an error (exit 2). **R**: a mistyped `required_section` ran no check and exited 0.
- A target with no in-scope files is an error. **R**: an empty target exited 0.
- `findings.json` now records `scope` and `checks_run` (enabled, settings, files examined, findings, references skipped), so a disabled check is visible. **S** (Grok: "what was not checked"; ChatGPT: demonstrable completion).

**Safety and correctness**
- Symlinks are never followed, read or hashed; they are listed as M-07. **R** (ChatGPT): a symlink to a file outside the target was read and hashed.
- Bare file names resolve only from the repo root or the file's folder unless a profile sets `xref_basename_fallback: unique`, which also reports names shared by several files. **R** (ChatGPT): a bare name matched a same-named file in any folder.
- References that leave the target root are reported and not probed.
- Cross-file duplicate heading IDs (minor), with `id_cross_file_ignore` for intended mirrors. **S**

**Protocol**
- Severity-to-gate mapping (critical BLOCK, major HOLD, minor and info recorded), adjudication rule for phase 1 findings, exit code 3 for major-only. G5 now covers all phase 1 findings. **R** (ChatGPT): exit 0 with majors present; G5 wording mixed two tests; no mapping existed.
- Phase 3 independence procedure: declaration, exact input set (phase 1 and 2 findings withheld), exposure log. **S** (Grok), with one change: findings withheld, not supplied.
- Report requires a "what was not checked" section. **S** (Grok, ChatGPT)

**Tools**
- `tools/verify_findings.py`: checks that cited files, hashes, line ranges and quotes exist. Reports coverage, not proof of examination. **S** (ChatGPT)
- Colab cell no longer guesses the target root. **R** (ChatGPT)
- Second profile (`generic_docs.json`) with a fixture repo that is not LazarusForge, and a self-audit profile. **S** (Grok)

**Tests:** 8 to 26. A regression introduced and fixed during this work: the first escape-root check also flagged valid `../` references from subfolders. It is now covered by a test.

## Deliberately not done

- Repository explorer, version comparison, claim and contradiction tools, execution sandbox, three-layer architecture (ChatGPT). Each is its own project; V0.0.1 had one tool.
- Heading-anchor verification, version-citation drift, Routing coverage, large-repository performance testing, malformed-Markdown fuzzing. Not implemented, not tested.
- LICENSE and NOTICE. A decision for the owner (`OPEN_QUESTIONS.md` 11).
- Rulings on authority, source of truth and phase shape. Pending.
