# Migration from LazarusForge

**Package:** AuditBot V0.0.3 draft. **Source:** LazarusForge 1.38 (head `62d831e5`, 2026-11-13). **Reviewed for this draft:** `Admin/Auditor_Protocols.md` (read in full for the sections below; headings only for the rest) and `Automation/README.md`. **Not yet reviewed:** the other audit documents, listed under "Untriaged".

## Where each piece went

| LazarusForge source | AuditBot destination | Treatment |
|---|---|---|
| Auditor_Protocols EF-0.0, EF-0.1, EF-0.4, EF-0.7 §3 | `CHARTER.md` rules 1, 2, 3, 5, 6 | Condensed |
| Evidence Classification, Provenance Ceiling | `CHARTER.md` rule 4; `phases/2_logical.md` L-4 | Labels kept (5 confidence, 4 provenance) |
| Core Auditor Doctrine | `CHARTER.md` rule 5; `README.md` | Condensed |
| Audit Entry Conditions | `PROTOCOL.md` entry conditions | Adapted; the `Unknowns.md` exception has no equivalent here |
| Audit Sequence (10 steps) | Folded into three phases (see below) | Restructured |
| Fallacy Checklist (10 items) | `phases/2_logical.md` L-5 | One line per item; full text stays in LazarusForge |
| Verification Gate Enforcement G1 to G6 | `PROTOCOL.md` gates | IDs kept; authority changed to advisory (open question 3) |
| Adversarial Audit Layer, battery (10 classes), sign-off format | `phases/3_adversarial.md` | Condensed; minimum requirements kept |
| Audit Phase Separation, freeze rules | `CHARTER.md` rule 8; `PROTOCOL.md` freeze and report | See "Phase structure" below |
| Auditor Role Classes (5) | Not migrated as roles | Replaced by one posture per phase (open question 5) |
| Sidecar model, Unknowns registry, dispute handling, human attestation, contributor protocols | Stay in LazarusForge | AuditBot emits findings, not sidecar entries |

### The 10-step sequence in three phases

| LazarusForge step | AuditBot |
|---|---|
| 1 Structural validation | Phase 1 (M-02, M-03) |
| 2 Scope validation | Phase 2 L-1 |
| 3 Assumption extraction | Phase 2 L-2 |
| 4 Internal coherence; 5 Cross-module consistency; 7 Drift detection | Phase 2 L-3 (term counting could move to phase 1 later) |
| 6 Evidence validation | Phase 2 L-4 |
| 8 Unknown classification | The `state` field of every finding |
| 9 Resolution pathway assessment | Not migrated; stays in LazarusForge |
| 10 Gate status | `PROTOCOL.md` gates |

### Phase structure: a difference to rule on

LazarusForge already has three phases, but they split by posture: **Audit, Adversarial Challenge, Synthesis**. Yours split by method: **Mechanical, Logical, Adversarial**. They overlap but differ. This draft keeps your three and moves Synthesis to a closing report step ("integrate, do not reconcile") instead of a fourth phase. Open question 1.

## Tools

| LazarusForge tool | Status |
|---|---|
| `audit_lib.py` (`Finding` class) | Reimplemented as the finding collector in `tools/mechanical.py` |
| `integrity_check.py` | Checks M-02 to M-07 reimplemented generically (cross-file duplicate heading IDs now included, as a minor lead). **Not ported:** Routing.md coverage pass, version-citation drift, T1 size census queue |
| (new, not from LazarusForge) | `tools/verify_findings.py`: citation verifier, added in V0.0.2 after review |
| `AUDIT_HARNESS.py` (50 KB) | Not ported; tied to LazarusForge's GitHub fetch and alias map |
| `cold_session_bundler.py`, `Admin/BATTERY_SEED.md` | Candidates for V0.0.2, for phase 3 independence. Not reviewed in detail |
| `parser.py`, `coverage_ledger_regen.py`, Colab launchers | Not ported |
| Candidate 3 experiment files | Not audit logic; stay in LazarusForge |

## Untriaged (not read for this draft)

`Admin/Forge_Audit_Kit.md` (60 KB), `Admin/Verification_Gates.md` (50 KB), `Admin/Repository_Integrity_Protocol.md` (117 KB), `Admin/Resolution_Methodology.md` (49 KB), `Admin/INTEGRITY_SWEEP_PROMPT.md` (23 KB), `Admin/PROBE_INVOCATION.md` (21 KB), `Admin/BATTERY_SEED.md`. Together with `Auditor_Protocols.md` (160 KB) the audit documents total about 478 KB, against about 41 KB for this draft (about 25 KB of it documentation). The audit records (`Admin/AAudits/`, 141 files, 1.2 MB) are history, not doctrine, and are not proposed for migration.

## What I checked on the draft tooling

- `tools/mechanical.py` ran on the LazarusForge 1.38 tree: 95 files in scope, 0 critical, 82 major, 43 minor, 10 info (exit code 3). Output is byte-identical across runs. 26 unit tests pass.
- LazarusForge's own `integrity_check.py`, run offline on the same tree, agrees on the Ethical Anchor check: no mismatch among the 95 in-scope files. Its three constitution criticals are in audit reports outside this profile's scope. It also reports a cross-file duplicate ID (GOV-007) that falls outside this profile's scope, because one copy is a sidecar under `Admin/ALogs/`.
- The major findings are M-02 (36) and M-04 (46) leads. I did not adjudicate them. Twenty M-04 leads point into `Archive/`. At least one is historical narrative about the relocation itself (`Admin/Governance_Charter.md` line 1353); others may be stale citations. That judgment belongs to phase 2.
- Run on itself (`profiles/auditbot_self.json`, fixtures excluded), the tool finds nothing.
- `tools/verify_findings.py` on LazarusForge: of three trial citations (one real, one with an invented quote, one to a nonexistent file), it verified the real one and rejected the other two.
- Rule text in `CHARTER.md` and the phase files is condensed from LazarusForge. It has not been compared line by line, which is the review I would ask other agents for.
