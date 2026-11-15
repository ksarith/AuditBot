# Finding format

One finding per entry. `tools/mechanical.py` writes these as JSON objects with the same field names.

| Field | Content |
|---|---|
| `id` | `P<phase>-<check or step>-<number>`, e.g. `P1-M04-007`, `P2-L3-002`, `P3-C6-001` |
| `phase` | 1, 2 or 3 |
| `check` | Check, step or battery class that produced it |
| `severity` | `critical` (blocks), `major`, `minor`, `info` |
| `state` | VERIFIED, PROVISIONAL or UNKNOWN. Mechanical findings about a deterministic fact are VERIFIED; everything else starts PROVISIONAL |
| `target` | File path and, where known, line or section |
| `claim` | What was checked, in one sentence |
| `evidence` | A short quote or the exact computed fact. Keep quotes brief |
| `reproduce` | How to get the same result (command, or the steps) |
| `nearly_failed` | What almost passed, or "n/a" |
| `action` | Recommended next step. A recommendation only |

Findings are append-only. A correction is a new finding that references the old `id`.
