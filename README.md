# AuditBot (draft V0.0.2)

Audit logic extracted from LazarusForge and isolated. Nothing here designs, builds or governs anything except audits.

**Status:** draft for multi-agent review. Not yet a repository. Nothing here is ratified; LazarusForge's text governs until the human owner ratifies a transfer (see `MIGRATION.md`). Open rulings are in `OPEN_QUESTIONS.md`; what changed since V0.0.1 is in `CHANGELOG.md`.

## Three phases, strict sequence

| Phase | Method | Question |
|---|---|---|
| 1. Mechanical | Deterministic scripts, no judgment | "Does it check out structurally?" |
| 2. Logical | Judgment, one claim at a time | "What does it claim, assume and rest on?" |
| 3. Adversarial | Independent instance, hostile posture | "How does it fail?" |

Between phase 3 and the report, `tools/verify_findings.py` checks that every cited quote exists where the finding says it does. The report then integrates the findings. It does not reconcile them, and it must say what was not checked (`PROTOCOL.md`).

## Quick start

- **Phase 1:** `python tools/mechanical.py <target_repo> --profile profiles/generic_docs.json --out out/`
  Exit codes: 0 clean, 1 critical, 2 error (bad profile or nothing in scope), 3 major findings.
- **Colab (mobile):** paste `tools/colab_cell.py` into a cell, set `TARGET_ROOT`, run.
- **Phases 2 and 3:** paste the prompt at the bottom of `phases/2_logical.md` or `phases/3_adversarial.md` into a fresh agent session. Phase 3 gets the target files and `manifest.json` only (`PROTOCOL.md`, independence procedure).
- **Citations:** `python tools/verify_findings.py <target_repo> --manifest out/manifest.json --findings p2_findings.json --out out/verification.json`
- **Tests:** `python -m unittest discover -s tests -v`
- **Self-audit:** `python tools/mechanical.py . --profile profiles/auditbot_self.json --out out/`

## Layout

```
CHARTER.md          the ideology, condensed (9 rules, each tagged with its LazarusForge source)
PROTOCOL.md         entry conditions, phase order, severity-to-gate mapping, independence procedure, report rules
phases/             one file per phase: checks, stance, output, agent prompt
templates/          finding, report and exposure-log formats
tools/              mechanical.py (phase 1), verify_findings.py (citations), colab_cell.py
profiles/           lazarusforge.json, generic_docs.json, auditbot_self.json
tests/              unit tests and a small non-LazarusForge fixture repo
CHANGELOG.md        changes by version, with their source
MIGRATION.md        what moved from LazarusForge, what stayed, what is untriaged
OPEN_QUESTIONS.md   decisions needed before creation
```

## What this is not

Not a doctrine repository, not a governance system, not a place for specifications. If something is not about how to audit, it belongs elsewhere.
