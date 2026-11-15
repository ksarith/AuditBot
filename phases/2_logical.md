# Phase 2: Logical

**Stance:** "What does this document actually claim?" Characterize faithfully before judging. Do not hunt for exploits here; that is phase 3.
**Input:** the target files, the manifest, and phase 1 findings (read them, do not edit them).

## Steps

| Step | Task | Produces |
|---|---|---|
| L-1 | **Scope.** Specification bleed, duplicate ownership, hidden interface assumptions, content in the wrong layer | Findings; a dispute or UNKNOWN where ownership is unclear |
| L-2 | **Assumptions.** Environmental, material, infrastructure, skill, resource, safety, simulation simplifications | Each one stated, kept, or logged UNKNOWN if indefensible |
| L-3 | **Coherence.** Internal contradictions, then contradictions with other files, term drift between files | Findings with both locations quoted |
| L-4 | **Evidence.** Label each meaningful claim with a confidence label and a provenance label; apply the provenance ceiling | A label per claim; PROVISIONAL cap enforced |
| L-5 | **Fallacy checklist** (below), with a note of one or two sentences per item | G1 evidence |

**Confidence labels:** Measured, Replicated, Simulated, Analogous, Placeholder. Unlabeled numbers count as Placeholder. A Placeholder cannot justify promotion.
**Provenance labels:** Internally Derived, Analogous External, Experimentally Verified, Operationally Hardened. Only the last two can reach VERIFIED.

## Fallacy checklist

1. **Magic energy:** is every energy flow traced to a source, storage and loss?
2. **Friction blindness:** are drag, wear and thermal losses ignored?
3. **Energy density paradox:** does a recovery step cost more than it returns?
4. **Semantic drift:** has a term changed meaning without a recorded revision?
5. **Scope creep as refinement:** did a revision quietly expand claimed capability?
6. **Hallucinated references:** does it cite files, sources or numbers that do not exist?
7. **Confidence without basis:** are claims labeled higher than their evidence supports?
8. **Lifecycle truncation:** are degraded operation, failure detection, maintenance and end of life covered?
9. **Incomplete by omission:** what critical subsystem or consideration is missing?
10. **The turd problem:** reduce the foundation to one falsifiable sentence. Does it survive?

Items 1 to 3 and 8 apply to physical designs; skip them for other targets and say so.

## Output

Findings per `templates/finding.md`, each with `evidence_ref` or a `no_evidence_reason`. Adjudicate every phase 1 major or critical finding (`P2-ADJ-nnn`, see `PROTOCOL.md`). Close with the G1, G2, G4 and G6 results. Sign off by declaring the phase closed.

## Agent prompt (paste into a fresh session with the files)

> You are performing Phase 2 (Logical) of an AuditBot audit. Operating as Phase 2 per AuditBot PROTOCOL V0.0.2. Read the attached target files and the Phase 1 findings. Do not edit Phase 1. Work through L-1 to L-5 in order. For every finding give evidence_ref entries (file, lines, a short quote), what you checked, what nearly failed, and your confidence state (VERIFIED, PROVISIONAL or UNKNOWN). Treat agreement with other agents, fluency and your own confidence as non-evidence. Do not look for exploits; that is a later phase. End with G1, G2, G4 and G6 results.
