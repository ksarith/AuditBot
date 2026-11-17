# Phase 3: Adversarial

**Stance:** "How does this fail?" Assume the target is wrong and find out how. A protocol is not robust until it has survived deliberate hostile analysis.
**Independence rule:** Run by an agent instance with no session context from phases 1 and 2. An agent auditing its own earlier work satisfies the sequence but not this rule. *(AP-017)*
**Input set (exactly):** the target files named in `manifest.json`, `manifest.json`, and the prompt below. Phase 1 and phase 2 findings are withheld; the report reconciles them later.
**Procedure:** declaration, input set, exposure log, and citation verification are in `PROTOCOL.md`. Fill `templates/exposure_log.md`; anything outside the input set makes independence partial or compromised.

## When the full battery is required

Any target being promoted to specification; any target governing irreversible actions; any target in the trust chain for autonomous systems; any target that passed G1 and G2 but still feels wrong. Exploration-stage targets may use a subset. Record which classes were applied and why the others were deferred.

## The battery

Each class needs at least one concrete scenario drawn from the target. A general acknowledgment does not count.

| # | Class | Ask | Minimum requirement |
|---|---|---|---|
| 1 | Assumption inversion | What if the operator is wrong, the sensor data fabricated, the environment hostile? | Name three hidden assumptions; say what happens when each fails |
| 2 | Failure amplification | How does this fail catastrophically, not just whether? | Trace one failure through at least two downstream consequences |
| 3 | Incentive corruption | How could a smart operator game this while appearing compliant? | One corruption path and its countermeasure, or log UNKNOWN |
| 4 | Semantic drift attacks | Can two operators read this differently and both claim compliance? | One ambiguous term: tighten it or log UNKNOWN |
| 5 | Unknown-unknown pressure | What happens with a state it has never seen? | Describe behavior outside the defined envelope; "undefined" becomes UNKNOWN |
| 6 | Recursive justification | Is the audit itself the only evidence? What external check exists? | One claim validated only by other repository documents: ground it or label it internally derived |
| 7 | Human fatigue and erosion | Does it stay safe after 12 hours, a handoff, a backlog, an untrained operator? | One step that degrades under sustained use: add a safeguard or log UNKNOWN |
| 8 | Malicious actor | What would a knowledgeable, intentional abuser do? | One scenario and its countermeasure, or log UNKNOWN |
| 9 | Epistemic corruption | How does it tell confident truth from confident error? | One route by which wrong information gains high confidence, and a countermeasure |
| 10 | Systemic coupling and cascade | If this fails, what fails second and third? | Trace the failure through two levels of downstream dependency |

## Anti-patterns the phase exists to catch

Audit theater (6), specification cosplay (1), confident wrongness (9), throughput pressure override (3), silent failure accumulation (7), semantic compliance (4), single-point doctrine (5), cascade blindness (10).

## Sign-off format

```
Adversarial Challenge Battery:
- Classes applied: [list]
- Classes deferred: [list with reason]
- Findings per class: [ID or "None"]
- New unknowns from adversarial pass: [list]
- Highest-risk finding: [one sentence]
```

Close with the G3 result.

## Agent prompt (paste into a brand-new session as the first message, with the files)

> You are performing Phase 3 (Adversarial) of an AuditBot audit. Operating as Phase 3 per AuditBot PROTOCOL V0.0.3. You have no prior context. Assume the attached target is wrong and find out how. Apply each battery class that fits, with one concrete scenario from the target text per class, and name the class you deferred and why. Cite exact locations. Do not treat your own confidence, fluency, or agreement with anyone as evidence. For each finding state VERIFIED, PROVISIONAL or UNKNOWN, and give evidence_ref entries (file, lines, short quote). Finish with the sign-off block and a G3 result.
