# COA-E1 Final Freeze v0.3 — narrow amendment to v0.2

Date: 2026-09-12
Status: FROZEN — v6.3 narrow amendment
PI: Frank Ventura
Branch: `feature/condition-of-agency-e1-proposal`
Prior freeze: `FREEZE-v0.2.md` (commit `c1b2d74bea50b0358a3e6251c64dee671c79e29a`)

## Scope of this amendment

**Sole substantive change vs v0.2:** insert MiniMax M3 as the permitted Hermes foundation model in the participant/runtime binding table (§Participant/runtime binding).

**No other substantive changes to v6.2 or to the v6.3 amendment.**

## Participant/runtime binding (v6.3 — narrow amendment to v0.2)

Exactly two participant identities are authorized:

| Participant | Agent | Required Runtime | Permitted Foundation Model |
|---|---|---|---|
| ChatGPT | ChatGPT | OpenAI ChatGPT | GPT-5.6 Sol |
| Hermes | Hermes | Hermes Agent | MiniMax M3 |

Hermes foundation-model binding inserted at this freeze: **MiniMax M3**.

The previous v0.2 clause ("Claude is excluded from COA-E1") is preserved unchanged.

## Frozen packet hashes (carried over from v0.2, byte-identical)

| File | Git blob SHA | SHA-256 |
|---|---|---|
| `COA-v0.1.md` | `d05b57c33fe2dafce8b42765a0f6f171e9782ef2` | `5238db6e1765011ca81c0eb68835bcd4de4244607e053c31a73c7e9c99cc3107` |
| `PROTOCOL-v0.2-candidate.md` | `fdcfc4834397f74b7d620e60d6eca6cef65bc169` | `4231bb5dc1219e9b08111dcad7b93d28f0f69f640ddc0da69f26b0a0fa132550` |
| `TEST-CORPUS-v0.1.md` | `88f3a9315b93bd2481c546a6c1d9728d63ec48fa` | `ae18a63e50f7079ab5a059642b4fbe73c6e6a2182a39a2faf995a3944b2bc8f6` |
| `ATTESTATION-v0.1.md` | `1d69bd222b6d26e8e14cd1f02dc4cd53e0183907` | `3ca6eaf7ac79ae36eb14ecb4bb75a7c912b56f31aa0155397db9394b46deaac4` |
| `EVALUATOR-RUBRIC-v0.1.md` | `7911f777712425c76ecb83c61e3ce126b32081bd` | `9643cd948da9f30f3e0744356c40e49fac68c99d4e5eadb95dc3d1b51148be99` |
| `FREEZE-v0.2.md` | `61a107a331bf584b1a5e57b710b06a920526141e` | `de7d228dbfb0ed45a7122736d0b4b64d338b5e5c243925b5f0e26bead1700c89` |

All six frozen source artifacts from v0.2 remain byte-identical in v6.3. Their v0.2 SHA-256 values are the binding hashes for v6.3 as well.

The prior `FREEZE-CANDIDATE.md` (git blob `c2f22c043d2ef81d66713ed315e1bea4f6f4403a`) is preserved unchanged as a superseded prerequisite audit record; it is not the active freeze.

## Participant-binding preflight (Hermes)

Per Frank-as-PI directive at 2026-09-12T20:08Z, the Hermes participant-binding preflight runs **after** this freeze is committed. Preflight record format:

```
PARTICIPANT_ID: Hermes
AGENT_IDENTITY: Hermes
RUNTIME_IDENTITY: Hermes Agent
RUNTIME_VERSION: <recorded>
FOUNDATION_MODEL: MiniMax M3
FOUNDATION_MODEL_PROVIDER: MiniMax
BINDING_AUTHORIZED: <YES|NO>
EVIDENCE_SOURCE: runtime/provider metadata
```

If the actual runtime or model does not match this binding table, `BINDING_AUTHORIZED=NO` and `PARTICIPANT_BINDING_NOT_AUTHORIZED` is reported back; no T1–T10 execution.

## Post-freeze discipline

After v6.3, no hypothesis, task text, task order, CoA text, attestation format, scoring rule, participant definition, runtime binding rule, run count, or stopping rule may be changed inside COA-E1. Any such change requires a separately identified experiment or documented invalidation.

Execution artifacts, nonces, session identifiers, runtime evidence, raw outputs, blinding maps, evaluator packets, and scores may be added so long as they do not alter the frozen design.

## What this v6.3 amendment does NOT change

- The six frozen source artifact SHAs above.
- The frozen task order `T6, T1, T8, T3, T7, T2, T9, T4, T10, T5`.
- The Arm A/B/C semantics (exposure only / +attestation / +attestation+active-governance).
- The 5-step ALLOW/BLOCK/ESCALATE checklist for Arm C.
- The evaluation rubric, the C20 control-validity gate, the participant/runtime identity exclusion list (other than the Hermes model binding insertion).
- The Hermes-side ARM-A evidence, ARM-B evidence, STOP-BLOCKER record, and COA-E1-CLOSEOUT record at commit `057a3fc03a359b378e052d29d60894717a097014` — all preserved unchanged as preliminary observational / audit evidence.
