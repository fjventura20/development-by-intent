# DBI Repeat-Invocation / State Isolation Experiment v0.1

**Status:** FROZEN-FINAL. Authorized by Frank-as-PI on 2026-09-08 (disposition `CONDITIONAL_FINAL_FREEZE_AUTHORIZED`) after applying P1-P3 to v0.3. **No generation GO has been given.** No reconstruction, priming, fresh target, repeated target, evaluator invocation, or scoring run may begin until a separate explicit Frank-as-PI GO references the FROZEN-FINAL commit SHA.
**Origin:** the failure of DBI-Evolution v0.1 (commit `649d398` on `integration-merge-ab-ro-2026-08-27`, disposition `MODIFICATION_AND_PRESERVATION_FAILURE`) revealed that 5 R2_B records were driven by repeat-invocation deferrals. This experiment isolates that mechanism.

## Directory structure

```
experiments/2026-09-08-dbi-state-isolation-v0.1/
├── README.md                                        # this file
├── protocol/
│   ├── PROTOCOL-v0.1-frozen-final.md                # FROZEN-FINAL (committed at the F8.2 step)
│   └── _superseded/
│       ├── PROTOCOL-DRAFT-v0.1-SUPERSEDED-BY-v0.2.md
│       ├── PROTOCOL-DRAFT-v0.2-SUPERSEDED-BY-v0.3.md
│       └── PROTOCOL-DRAFT-v0.3-SUPERSEDED-BY-v0.1-FROZEN-FINAL.md
├── preflight/
│   ├── SUBSTRATE-EQUIVALENCE-VALIDATION.md          # documents Evolution v0.1 substrate constants (F2-corrected)
│   ├── MULTITURN-PERSISTENCE-VALIDATION.md          # validates `claude --resume` on this host
│   ├── date-order.json                               # T1..T5 canonical Evolution order (F8.1 freeze gate)
│   ├── randomization-script.py                       # OS-CSPRNG coin-flip drawer (executed AT F8.2)
│   ├── replicate-order-flips.json                    # the 3 OS-CSPRNG flips (created at F8.2 freeze time, immutable)
│   └── artifact-hashes.json                          # initial SHA set (replicate-order-flips.json + randomization-script.py)
└── results/                                         # (empty; populated by main experiment after generation GO)
```

## Replicate-order coin flips (F8.2, recorded 2026-09-08T13:27:01Z)

| Replicate | Coin flip |
|-----------|-----------|
| replicate_1 | `repeated_first` |
| replicate_2 | `repeated_first` |
| replicate_3 | `repeated_first` |

These are the preregistered condition-order assignments for the 3 replicates. They are immutable at the FROZEN-FINAL commit. The first condition to run is the **repeated** condition in all 3 replicates; the **fresh** condition runs second in all 3 replicates.

## Version history

| Date | Version | Status | Notes |
|------|---------|--------|-------|
| 2026-09-08 | v0.1 | SUPERSEDED | First draft. 10 PI rulings (Q1-Q5 + C1-C5) from pass 1. |
| 2026-09-08 | v0.2 | SUPERSEDED | Applied 10 PI rulings. 7 execution-integrity issues (F1-F7) from pass 2. |
| 2026-09-08 | v0.3 | SUPERSEDED | Applied F1-F7. 3 deterministic integrity corrections (P1-P3) from pass 3. |
| 2026-09-08 | **v0.1-frozen-final** | **FROZEN-FINAL** | Applied P1-P3; passed `CONDITIONAL_FINAL_FREEZE_AUTHORIZED`. SHA-256 `472d7b9f0058875be1c6a84ca5e7e6b0e2065ac2055bcad4b8d3bc00744d18ac`. |

## Audit trail

- **PI adjudication pass 1 (Q1-Q5 + C1-C5):** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T112600Z-dbi-state-isolation-pi-adjudication-001/` (commit `14a3f3ac` on `mailbox/main`)
- **PI final-freeze review pass 2 (F1-F7):** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T130600Z-dbi-state-isolation-final-freeze-review-002/` (commit `5f8f3d5` on `mailbox/main`)
- **PI final-freeze authorization pass 3 (P1-P3):** `HANDOFFS/exchange/chatgpt-to-hermes/pending/20260908T131800Z-dbi-state-isolation-final-freeze-authorization-004/` (commit `9afd89e` on `mailbox/main`)
- **D034:** `hermes-coordination/DECISIONS.md` — "Do not rerun Evolution v0.1; proceed to State Isolation v0.1"
- **D035:** `hermes-coordination/DECISIONS.md` — "DBI State Isolation v0.1 v0.2 protocol revision (post PI adjudication pass 1)"
- **D036:** `hermes-coordination/DECISIONS.md` — "DBI State Isolation v0.1 v0.3 protocol (post PI final-freeze review pass 2)"
- **D037 (pending):** v0.1-frozen-final protocol committed; P1-P3 applied; 3 OS-CSPRNG coin flips recorded
- **FROZEN-FINAL predecessor:** `experiments/2026-09-06-dbi-evolution-v0.1/protocol/PROTOCOL-v0.5-frozen-final.md` (commit `da11836`)
- **R2_B deferrals being reproduced:** `experiments/2026-09-06-dbi-evolution-v0.1/runs/R2_M/captures/B/T{1..5}.raw.json`

## Current state

- **FROZEN-FINAL** protocol committed. 3 OS-CSPRNG coin flips recorded. SHA-256 of the protocol file: `472d7b9f0058875be1c6a84ca5e7e6b0e2065ac2055bcad4b8d3bc00744d18ac`.
- **No generation GO has been given.** Awaiting separate explicit Frank-as-PI GO referencing the FROZEN-FINAL commit SHA before any generation begins.

End of README.
