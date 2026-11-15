# Open questions before creation

Each has my default in brackets. Please rule or redirect. Questions 1, 3 and 4 are load-bearing; `PROTOCOL.md` treats them as pending until you rule.

1. **Phase shape.** Keep Mechanical, Logical, Adversarial, with Synthesis as the closing report step? Or restore LazarusForge's Audit, Adversarial, Synthesis? [Keep yours.]
2. **Where does a check live?** Semantic drift: mechanical term counting, or judgment? [Judgment now; term counts later.]
3. **Authority.** LazarusForge gives auditors binding block authority. Should AuditBot's gate results bind, or only recommend? [Recommend only; you ratify.]
4. **Source of truth.** After creation, does AuditBot own audit doctrine and LazarusForge's `Auditor_Protocols.md` point to it? Or does LazarusForge stay authoritative and AuditBot track it? The constitutional text (EF-0.x) cannot be amended without your ratification. [LazarusForge stays authoritative until you ratify a transfer.]
5. **Ethical lens.** LazarusForge has an Ethical Auditor role. Keep a lens for it inside phase 2, or leave it in LazarusForge? [Leave it; revisit.]
6. **Independence tooling.** The procedure is now in `PROTOCOL.md`. Port `cold_session_bundler.py` and `BATTERY_SEED.md` as its implementation in V0.0.3? [Yes, after review.]
7. **Target scope.** LazarusForge only, or any repo through profiles? [Any repo. Two non-LazarusForge profiles now exist; the claim is untested beyond a small fixture.]
8. **Audit records.** Do the 141 audit reports in `Admin/AAudits/` stay in LazarusForge as its history? [Yes.]
9. **Mechanical gaps.** Cross-file duplicate IDs are in. Routing coverage and version-citation drift stay LazarusForge-specific or later? [Leave out for now.]
10. **G5 broadened.** LazarusForge's G5 covers cross-references. Here it covers all phase 1 findings, with a severity mapping (critical BLOCK, major HOLD). Accept, or split into two gates? [Accept; revisit if it proves coarse.]
11. **License.** AuditBot derives from LazarusForge text. Which license, and what goes in NOTICE? [Match LazarusForge unless you want otherwise.]
12. **Adjudication authority.** Only the phase 2 agent or you may adjudicate phase 1 majors. Should phase 3 be able to challenge an adjudication? [Yes, as a new finding.]

## How other agents should review this

Check the rule text against the LazarusForge sections named in `CHARTER.md` and `MIGRATION.md`, and report where the condensation changed meaning, dropped a requirement, or added one. Style opinions are not needed. Agreement among reviewers does not settle a point; a mismatch against the source text, or a reproduced failure of the tools, does.
