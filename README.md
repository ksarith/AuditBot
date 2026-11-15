# AuditBot (draft V0.0.1)

Audit logic extracted from LazarusForge and isolated. Nothing here designs, builds or governs anything except audits.

**Status:** draft for multi-agent review. Not yet a repository. Nothing here is ratified; LazarusForge's text governs until the human owner ratifies a transfer (see `MIGRATION.md`).

## Three phases, strict sequence

| Phase | Method | Question |
|---|---|---|
| 1. Mechanical | Deterministic scripts, no judgment | "Does it check out structurally?" |
| 2. Logical | Judgment, one claim at a time | "What does it claim, assume and rest on?" |
| 3. Adversarial | Independent instance, hostile posture | "How does it fail?" |

After phase 3 the report integrates the findings. It does not reconcile them (see `PROTOCOL.md`).

## Quick start

- **Phase 1 (offline):** `python tools/mechanical.py <target_repo> --profile profiles/lazarusforge.json --out out/`
- **Colab (mobile):** paste `tools/colab_cell.py` into a cell, upload the target zip, run.
- **Phases 2 and 3:** paste the prompt at the bottom of `phases/2_logical.md` or `phases/3_adversarial.md` into a fresh agent session, with the phase 1 findings and the target files.
- **Tests:** `python -m unittest discover -s tests -v`

## Layout

```
CHARTER.md          the ideology, condensed (9 rules, each tagged with its LazarusForge source)
PROTOCOL.md         entry conditions, phase order, gates, report procedure
phases/             one file per phase: checks, stance, output, agent prompt
templates/          finding and report formats
tools/              mechanical.py (phase 1), colab_cell.py
profiles/           per-target settings (lazarusforge.json)
tests/              unit tests for phase 1
MIGRATION.md        what moved from LazarusForge, what stayed, what is untriaged
OPEN_QUESTIONS.md   decisions needed before creation
```

## What this is not

Not a doctrine repository, not a governance system, not a place for specifications. If something is not about how to audit, it belongs elsewhere.
