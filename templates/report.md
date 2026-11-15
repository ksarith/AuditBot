# Audit report

**Target:** [name, exact version or commit]
**Profile:** [profiles/<name>.json]
**Date:** [YYYY-MM-DD]
**Manifest hash:** [SHA-256 of manifest.json]   **Phase 1 findings hash:** [SHA-256 of findings.json]
**Verification hash:** [SHA-256 of verification.json]   **Exposure log:** [attached; independence: full / partial / compromised]
**Agents:** Phase 2: [name/model]   Phase 3: [name/model, confirmed no prior session context]
**Phases skipped, with reason:** [none, or list]

## Phase 1: Mechanical
[Exit code and counts by severity. List critical and major findings by id, each with its adjudication or "unadjudicated".]

## Phase 2: Logical
[Findings by step L-1 to L-5. Fallacy checklist notes.]

## Phase 3: Adversarial
[Battery sign-off block. Findings by class.]

## What was not checked
[From `checks_run` and `verification.json`: disabled checks, skipped symlinks, references skipped by marker or prefix, skipped phases, deferred battery classes, manifest files no finding cites, unverified citations. Write "nothing" only if that is true.]

## How the findings relate
[State the relationship between phases. Do not force agreement. Where findings conflict, list both and mark UNKNOWN.]

## Gates
| Gate | Result (CLEAR / HOLD / BLOCK) | Basis |
|---|---|---|
| G1 | | |
| G2 | | |
| G3 | | |
| G4 | | |
| G5 | | |
| G6 | | |

**Overall (worst gate):** [ ]
**Recommendation to owner:** [ ]
**Ratification:** [human owner decision and date]
