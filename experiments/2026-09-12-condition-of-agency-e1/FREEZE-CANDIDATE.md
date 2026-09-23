# E1 Freeze Candidate

Date: 2026-09-12
Status: READY FOR PI FREEZE REVIEW — NO EXECUTION AUTHORIZED
Branch: `feature/condition-of-agency-e1-proposal`

## Packet
- `COA-v0.1.md`
- `PROTOCOL-v0.2-candidate.md`
- `TEST-CORPUS-v0.1.md`
- `ATTESTATION-v0.1.md`
- `EVALUATOR-RUBRIC-v0.1.md`
- preserved audit predecessor: `PROTOCOL-v0.1-candidate.md`

## Governing CoA digest
SHA-256 `5238db6e1765011ca81c0eb68835bcd4de4244607e053c31a73c7e9c99cc3107`

## Participant binding
Exactly two participant identities: ChatGPT and Hermes.

For E1, ChatGPT is instantiated by OpenAI GPT-5.6 Sol. The runtime/model is an implementation detail recorded as evidence, not a third participant identity.

Hermes must record its exact active runtime/model before dispatch and use the same runtime/model across Arms A/B/C.

Claude is excluded from this E1 execution.

## Lean execution size
2 participants × 3 arms × 10 tasks = 60 scored responses.

## Execution gate
No task generation or experimental execution may begin from this candidate packet until Frank, acting as PI, reviews the packet and issues a separate explicit execution GO.

Before final freeze, independently compute and record SHA-256 hashes for every packet file and verify that the CoA digest above matches the exact bytes of `COA-v0.1.md`. Any mismatch invalidates the freeze candidate until corrected.
