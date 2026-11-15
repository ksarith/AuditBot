# Protocol (V0.0.1 draft)

## Entry conditions

An audit starts only when all of these hold. If one fails, stop and record why.

1. The target and its exact version (commit, release or zip name) are recorded.
2. A profile is chosen (`profiles/<name>.json`) and named in the report.
3. A manifest of SHA-256 hashes exists for every in-scope file (phase 1 produces it).
4. The phase 2 and phase 3 agents are named, and phase 3 is a different instance with no session context from phases 1 and 2.

## Sequence

| Phase | Output | Freezes when |
|---|---|---|
| 1 Mechanical | `manifest.json`, `findings.json` | The script run completes and both files are hashed |
| 2 Logical | Findings (template: `templates/finding.md`) | The agent signs off |
| 3 Adversarial | Findings plus the battery sign-off | The independent agent signs off |
| Report | `templates/report.md` | Human reads it |

Skipping a phase needs a written reason in the report. Each agent declares its phase before contributing: *"Operating as Phase N per AuditBot PROTOCOL V0.0.1."* An undeclared phase shift is a drift indicator.

## Freeze and corrections

A closed phase is never edited. If a later phase finds something an earlier one missed, that is a new finding attributed to the later phase.

## Gates

Gate IDs keep their LazarusForge numbering so lineage stays traceable.

| Gate | Test | Phase | If it fails |
|---|---|---|---|
| G1 | Fallacy checklist applied with substantive notes | 2 | Return to author |
| G2 | Physical and logical plausibility | 2 | Return for revision |
| G3 | Adversarial battery applied by an independent instance | 3 | Cannot be promoted |
| G4 | Scope alignment | 2 | Route to the owner of the right scope |
| G5 | Cross-reference integrity; no critical mechanical findings | 1 | Hold at draft |
| G6 | No contradiction with existing specifications | 2 | Resolve before committing |

**Result per gate:** CLEAR, HOLD or BLOCK. **Overall:** the worst gate result.

**Authority:** AuditBot's results are recommendations. Ratification rests with the human owner. (LazarusForge gives auditors binding block authority; whether AuditBot keeps that is an open question.)

## Report: integrate, do not reconcile

The report lists findings by phase, states how they relate, and gives a gate result. When phase 1 says "structure intact" and phase 3 says "found an exploit", both stand: they answer different questions. The report must not force agreement between phases or between agents. Where findings truly conflict (not merely differ in wording), list both and mark the point UNKNOWN.

## Self-application

This protocol and the tools in this repository are audit targets under the same rules.
