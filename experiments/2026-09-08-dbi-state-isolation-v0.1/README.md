# DBI Repeat-Invocation / State Isolation Experiment v0.1

**Status:** Protocol v0.2 in draft, awaiting PI freeze review.
**Origin:** the failure of DBI-Evolution v0.1 (commit `649d398` on `integration-merge-ab-ro-2026-08-27`, disposition `MODIFICATION_AND_PRESERVATION_FAILURE`) revealed that 5 R2_B records were driven by repeat-invocation deferrals. This experiment isolates that mechanism.

## Directory structure

```
experiments/2026-09-08-dbi-state-isolation-v0.1/
├── README.md                                        # this file
├── protocol/
│   ├── PROTOCOL-DRAFT-v0.2.md                       # current draft (post PI adjudication pass 1)
│   └── _superseded/
│       └── PROTOCOL-DRAFT-v0.1-SUPERSEDED-BY-v0.2.md  # v0.1 draft (superseded 2026-09-08)
├── preflight/
│   ├── SUBSTRATE-EQUIVALENCE-VALIDATION.md          # documents Evolution v0.1 substrate constants (per C1, C2)
│   └── MULTITURN-PERSISTENCE-VALIDATION.md          # validates `claude --resume` on this host (per Q2)
└── results/                                         # (empty; populated by main experiment)
```

## Version history

| Date | Version | Status | Notes |
|------|---------|--------|-------|
| 2026-09-08 | v0.1 | SUPERSEDED | Original draft. 4 design errors per Frank: (1) presented 5 different dates once instead of repeating the same 5; (2) used single-prompt-multi-trigger approximation rather than true conversational persistence; (3) changed generator to Opus (the evaluator model) instead of holding Evolution generator constant; (4) included anti-deferral instructions that would suppress the phenomenon. PI adjudication: REVISION_REQUIRED_BEFORE_FREEZE. |
| 2026-09-08 | v0.2 | DRAFT (post PI adjudication) | Incorporates all 10 PI rulings (5 Q + 5 C). Uses `claude --resume <session_id>` for true multi-turn persistence. Uses `claude-sonnet-4-6` (Evolution generator) not Opus. Holds frozen Evolution Arm M intent constant. Repeated condition = same 5 dates in same order in same persistent session (priming pass + second pass). No anti-deferral language. Two blinded evaluators (gpt-5.6-sol + claude-opus-4.7) with binary `report_produced` primary. |

## Audit trail

- **PI adjudication (Q1-Q5 + C1-C5):** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T112600Z-dbi-state-isolation-pi-adjudication-001/` (commit `14a3f3ac` on `mailbox/main`)
- **D034:** `hermes-coordination/DECISIONS.md` — "Do not rerun Evolution v0.1; proceed to State Isolation v0.1"
- **D035:** `hermes-coordination/DECISIONS.md` — "DBI State Isolation v0.1 v0.2 protocol revision (post PI adjudication pass 1)"
- **FROZEN-FINAL predecessor:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`)
- **R2_B deferrals being reproduced:** `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/captures/B/T{1..5}.raw.json`

## Current state

- **No generation GO has been given.** Awaiting final PI freeze review and a separate explicit GO referencing v0.2's commit SHA before any generation begins.
- **All 10 PI rulings addressed in v0.2** (§0 change log explicitly maps each ruling to its application site).
- **True multi-turn persistence validated** (`preflight/MULTITURN-PERSISTENCE-VALIDATION.md`).
- **Substrate equivalence to Evolution v0.1 documented** (`preflight/SUBSTRATE-EQUIVALENCE-VALIDATION.md`).

End of README.
