# COA-E1 Final Freeze v0.2

Date: 2026-09-12
Status: FROZEN — EXECUTION AUTHORIZED
PI: Frank Ventura
Authorization: `EXECUTION GO — COA-E1`
Branch: `feature/condition-of-agency-e1-proposal`

This record freezes the E1 packet exactly as it existed at PI execution authorization. The source files retain their `FROZEN CANDIDATE` labels as immutable historical bytes; this freeze record promotes those exact bytes to the governing execution packet without rewriting them.

## Frozen packet hashes

| File | Git blob SHA | SHA-256 |
|---|---|---|
| `COA-v0.1.md` | `d05b57c33fe2dafce8b42765a0f6f171e9782ef2` | `5238db6e1765011ca81c0eb68835bcd4de4244607e053c31a73c7e9c99cc3107` |
| `PROTOCOL-v0.2-candidate.md` | `fdcfc4834397f74b7d620e60d6eca6cef65bc169` | `4231bb5dc1219e9b08111dcad7b93d28f0f69f640ddc0da69f26b0a0fa132550` |
| `TEST-CORPUS-v0.1.md` | `88f3a9315b93bd2481c546a6c1d9728d63ec48fa` | `ae18a63e50f7079ab5a059642b4fbe73c6e6a2182a39a2faf995a3944b2bc8f6` |
| `ATTESTATION-v0.1.md` | `1d69bd222b6d26e8e14cd1f02dc4cd53e0183907` | `3ca6eaf7ac79ae36eb14ecb4bb75a7c912b56f31aa0155397db9394b46deaac4` |
| `EVALUATOR-RUBRIC-v0.1.md` | `7911f777712425c76ecb83c61e3ce126b32081bd` | `9643cd948da9f30f3e0744356c40e49fac68c99d4e5eadb95dc3d1b51148be99` |

SHA-256 values were independently recomputed from the exact UTF-8 file contents retrieved from GitHub. The governing CoA digest matches the preregistered digest.

## Participant/runtime binding

Exactly two participant identities are authorized:

1. **ChatGPT** — runtime/model: OpenAI GPT-5.6 Sol.
2. **Hermes** — exact active runtime/model must be recorded before its first scored session and held fixed for Arms A/B/C.

Claude is excluded from COA-E1.

## Execution matrix

- 2 participants
- 3 arms per participant
- 1 fresh session per arm
- 10 tasks per session
- 60 scored responses total
- frozen order: `T6, T1, T8, T3, T7, T2, T9, T4, T10, T5`

## Post-freeze discipline

After this record, no hypothesis, task text, task order, CoA text, attestation format, scoring rule, participant definition, runtime binding rule, run count, or stopping rule may be changed inside COA-E1. Any such change requires a separately identified experiment or documented invalidation.

Execution artifacts, nonces, session identifiers, runtime evidence, raw outputs, blinding maps, evaluator packets, and scores may be added so long as they do not alter the frozen design.
