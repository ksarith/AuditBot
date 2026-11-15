# Protocol (V0.0.2 draft)

Rulings on authority, source of truth and phase shape are **pending human ratification** (`OPEN_QUESTIONS.md` 1, 3, 4). The defaults below follow the draft; they are not decided.

## Entry conditions

An audit starts only when all of these hold. If one fails, stop and record why.

1. The target and its exact version (commit, release or zip name) are recorded.
2. A profile is chosen (`profiles/<name>.json`) and named in the report.
3. Phase 1 has run cleanly: exit code 0, 1 or 3 (never 2), a manifest with at least one file, and a `checks_run` block in `findings.json`. A phase 1 result without these is invalid.
4. The phase 2 and phase 3 agents are named, and phase 3 is a different instance with no session context from phases 1 and 2.

## Sequence

| Phase | Output | Freezes when |
|---|---|---|
| 1 Mechanical | `manifest.json`, `findings.json` | The run completes and both files are hashed |
| 2 Logical | Findings (`templates/finding.md`) | The agent signs off |
| 3 Adversarial | Findings plus the battery sign-off | The independent agent signs off |
| Verification | `verification.json` from `tools/verify_findings.py` | The script run completes |
| Report | `templates/report.md` | Human reads it |

Skipping a phase needs a written reason in the report. Each agent declares its phase before contributing: *"Operating as Phase N per AuditBot PROTOCOL V0.0.2."* An undeclared phase shift is a drift indicator.

## Freeze and corrections

A closed phase is never edited. A later phase that finds something an earlier one missed, or disagrees with it, adds a new finding attributed to itself.

## Severity and gate results

| Severity | Gate result |
|---|---|
| critical | BLOCK |
| major | HOLD until adjudicated or fixed |
| minor, info | Recorded; never gating alone |

The same mapping applies to findings from every phase. A gate's result is the worst of its findings after adjudication. The overall result is the worst gate.

### Adjudication

Only the phase 2 agent or the human owner may adjudicate a major or critical finding. An adjudication is a new finding (`P2-ADJ-nnn`) with `adjudicates` (the ids), `verdict` (`false_positive`, `accepted_risk` or `confirmed`), a reason, and evidence. A `false_positive` or `accepted_risk` verdict lowers the gate result for that finding to CLEAR; `confirmed` leaves it standing. Phase 1 findings are never edited or deleted. Unverified citations (see below) cannot support an adjudication.

## Gates

Gate IDs keep their LazarusForge numbering so lineage stays traceable.

| Gate | Test | Phase |
|---|---|---|
| G1 | Fallacy checklist applied with substantive notes | 2 |
| G2 | Physical and logical plausibility | 2 |
| G3 | Adversarial battery applied by an independent instance | 3 |
| G4 | Scope alignment | 2 |
| G5 | Structural and cross-reference integrity: all phase 1 findings, after adjudication | 1 |
| G6 | No contradiction with existing specifications | 2 |

G5 is broader than LazarusForge's version, which covers cross-references only (`OPEN_QUESTIONS.md` 10). A gate cannot be CLEAR if its phase was skipped or its citations failed verification.

## Phase 1 exit codes

| Code | Meaning | Gate effect |
|---|---|---|
| 0 | No critical or major findings | G5 may be CLEAR |
| 1 | At least one critical finding | G5 BLOCK |
| 2 | Error: bad profile, bad usage, or nothing in scope | No valid phase 1 result |
| 3 | Major findings, no critical | G5 HOLD until adjudicated |

## Phase 3 independence procedure

1. **Declaration.** The agent states: phase, model or instance name, session identifier or "fresh session", and "no prior audit context".
2. **Input set.** Exactly the target files named in `manifest.json`, plus `manifest.json` itself, plus the phase 3 prompt. Phase 1 and phase 2 findings are withheld.
3. **Exposure log.** The operator fills `templates/exposure_log.md`: everything the agent saw before and during the pass. Anything outside the input set marks independence **partial** or **compromised**, and G3 cannot be CLEAR.
4. **Verification.** Phase 3 findings go through `tools/verify_findings.py` like phase 2 findings.

## Citations

Every phase 2 and phase 3 finding carries `evidence_ref` entries (file, lines, quote) or a `no_evidence_reason`. `tools/verify_findings.py` checks that the cited file is in the manifest and unchanged, the lines exist, and the quote is there. It does not judge whether the finding is right, and it cannot prove an agent examined anything. A finding that fails verification is listed in the report as unverified and cannot support a gate result.

## Report: integrate, do not reconcile

The report lists findings by phase, states how they relate, and gives a gate result. When phase 1 says "structure intact" and phase 3 says "found an exploit", both stand: they answer different questions. The report must not force agreement between phases or between agents. Where findings truly conflict, list both and mark the point UNKNOWN.

The report must include **what was not checked**: disabled checks, skipped symlinks and references, skipped phases, deferred battery classes, manifest files no finding cites, and unverified citations. A report that omits this section is incomplete.

**Authority:** AuditBot's results are recommendations. Ratification rests with the human owner.

## Self-application

This protocol and the tools in this repository are audit targets under the same rules (`profiles/auditbot_self.json`).
