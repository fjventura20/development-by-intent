# DBI Repeat-Invocation / State Isolation Experiment v0.1

**Status:** Protocol v0.3 frozen-candidate, awaiting PI final-freeze authorization.
**Origin:** the failure of DBI-Evolution v0.1 (commit `649d398` on `integration-merge-ab-ro-2026-08-27`, disposition `MODIFICATION_AND_PRESERVATION_FAILURE`) revealed that 5 R2_B records were driven by repeat-invocation deferrals. This experiment isolates that mechanism.

## Directory structure

```
experiments/2026-09-08-dbi-state-isolation-v0.1/
├── README.md                                        # this file
├── protocol/
│   ├── PROTOCOL-DRAFT-v0.3.md                       # current draft (post PI adjudication pass 2; F1-F7 applied)
│   └── _superseded/
│       ├── PROTOCOL-DRAFT-v0.1-SUPERSEDED-BY-v0.2.md
│       └── PROTOCOL-DRAFT-v0.2-SUPERSEDED-BY-v0.3.md
├── preflight/
│   ├── SUBSTRATE-EQUIVALENCE-VALIDATION.md          # documents Evolution v0.1 substrate constants (F2-corrected)
│   ├── MULTITURN-PERSISTENCE-VALIDATION.md          # validates `claude --resume` on this host
│   ├── date-order.json                               # T1..T5 canonical Evolution order (F8.1 freeze gate)
│   └── randomization-script.py                       # OS-CSPRNG coin-flip drawer (executed AT F8.2)
└── results/                                         # (empty; populated by main experiment)
```

## Version history

| Date | Version | Status | Notes |
|------|---------|--------|-------|
| 2026-09-08 | v0.1 | SUPERSEDED | First draft. 10 PI rulings (Q1-Q5 + C1-C5) from pass 1. |
| 2026-09-08 | v0.2 | SUPERSEDED | Applied 10 PI rulings. 7 execution-integrity issues (F1-F7) from pass 2. |
| 2026-09-08 | v0.3 | DRAFT (awaiting freeze) | Applied F1-F7: each fresh target = own reconstruction + 1 trigger; trigger positional to --print not stdin; opaque UUID4 blind IDs; report_produced independent of BIB quality; per-evaluator disposition; runtime retry preserves treatment; 4-gate separation. |

## Audit trail

- **PI adjudication pass 1 (Q1-Q5 + C1-C5):** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T112600Z-dbi-state-isolation-pi-adjudication-001/` (commit `14a3f3ac` on `mailbox/main`)
- **PI final-freeze review pass 2 (F1-F7):** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T130600Z-dbi-state-isolation-final-freeze-review-002/` (commit `5f8f3d5` on `mailbox/main`)
- **D034:** `hermes-coordination/DECISIONS.md` — "Do not rerun Evolution v0.1; proceed to State Isolation v0.1"
- **D035:** `hermes-coordination/DECISIONS.md` — "DBI State Isolation v0.1 v0.2 protocol revision (post PI adjudication pass 1)"
- **D036 (pending):** v0.3 frozen-candidate
- **FROZEN-FINAL predecessor:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`)
- **R2_B deferrals being reproduced:** `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/captures/B/T{1..5}.raw.json`

## Current state

- **No generation GO has been given.** Awaiting final PI freeze authorization and a separate explicit GO referencing v0.3's commit SHA before any generation begins.
- All 7 PI pass-2 rulings (F1-F7) addressed in v0.3.
- 4 preflight artifacts ready: SUBSTRATE-EQUIVALENCE (F2-corrected), MULTITURN-PERSISTENCE, date-order, randomization-script.
- `replicate-order-flips.json` is created AT F8.2 freeze time, not before. The v0.3 protocol does not claim it exists.

End of README.
