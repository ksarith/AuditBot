# Finding format

One finding per entry. `tools/mechanical.py` writes phase 1 findings as JSON objects with the same field names. Phase 2 and 3 agents may write JSON (preferred, so `tools/verify_findings.py` can read it) or Markdown with the same fields.

| Field | Content |
|---|---|
| `id` | `P<phase>-<check or step>-<number>`, e.g. `P1-M04-007`, `P2-L3-002`, `P3-C6-001`, `P2-ADJ-001` |
| `phase` | 1, 2 or 3 |
| `check` | Check, step or battery class that produced it |
| `severity` | `critical` (BLOCK), `major` (HOLD), `minor`, `info` |
| `state` | VERIFIED, PROVISIONAL or UNKNOWN. Mechanical findings about a deterministic fact are VERIFIED; everything else starts PROVISIONAL |
| `target` | File path and, where known, line or section |
| `claim` | What was checked, in one sentence |
| `evidence` | The exact computed fact, or a one-line summary of the cited text |
| `evidence_ref` | Phases 2 and 3: a list of `{"file": "...", "lines": "12-18", "quote": "..."}`. Keep quotes brief. Use `...` inside a quote to skip text. Verified by `tools/verify_findings.py` |
| `no_evidence_reason` | Required when `evidence_ref` is empty (for example, a finding about something missing) |
| `reproduce` | How to get the same result (command, or the steps) |
| `nearly_failed` | What almost passed, or "n/a" |
| `action` | Recommended next step. A recommendation only |

Adjudication findings (`P2-ADJ-nnn`) add `adjudicates` (list of finding ids) and `verdict` (`false_positive`, `accepted_risk` or `confirmed`) and must give a reason in `claim` or `evidence`.

Findings are append-only. A correction is a new finding that references the old `id`.
