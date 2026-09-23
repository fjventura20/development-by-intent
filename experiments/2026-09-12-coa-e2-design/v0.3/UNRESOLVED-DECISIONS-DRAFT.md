# COA-E2 — Remaining PI/ChatGPT Decisions (DRAFT v0.3)

1. **P1 level:** accept `P1_APPLICATION_LAYER_PASS` as sufficient for this pilot if Hermes cannot expose the provider-bound serialized request, or require `P1_FULL_PASS` and stop if unavailable.
2. **No-write enforcement:** select the exact Hermes-supported mechanism that disables memory-writing tools without changing the runtime. If none exists, decide whether the design is admissible with S8 fail-closed monitoring.
3. **Packet match tolerance:** set the token-count tolerance and prohibit runtime padding after freeze.
4. **Task discrimination:** approve U1-U5 as non-saturated decision-boundary tasks or request replacements.
5. **Rubric:** approve action-code mapping and the `AMBIGUOUS`/`UNSCORABLE` rules.
6. **Three-pair pilot:** confirm it is a proof-of-mechanism pilot only, with no conventional significance claim.
7. **Mechanism-test evidence:** decide whether the pre-freeze `--oneshot` → `--resume` evidence is included as a committed freeze artifact.
8. **Provider capture:** determine whether an approved Hermes v0.21.2 hook/API can expose exact provider-bound requests; if not, bind P1 to application-layer status.

Already incorporated: operator-only identity; no participant backend identity fields; four-field ACK; no participant session-ID probes; six profiles; six unique nonces; counterbalanced order; matched informational control; fresh tasks; deterministic runner; separate evaluator; compression and every structural failure are global STOPs.

No item authorizes freezing or execution.
