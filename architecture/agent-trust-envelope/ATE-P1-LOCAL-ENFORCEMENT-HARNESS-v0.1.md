# ATE P1 Local Enforcement Harness v0.1

## Status

Focused implementation milestone for the first high-value P1 enforcement properties.

This artifact does **not** supersede `ATE-P0-P1-CONFORMANCE-TEST-PLAN-v0.1.md` and does not redefine the full P1 acceptance bar.

## Objective

Move ATE from logical trust decisions to locally executable enforcement mechanics while conserving subscriptions and avoiding unnecessary live-agent work.

## Required properties for this milestone

1. **Direct resource bypass denial** — a caller lacking executor authority cannot invoke the protected resource operation successfully.
2. **Executor credential separation** — governed resource authority is held on the executor side and is absent from the authorization request.
3. **Durable nonce state across restart** — consumed authorization remains consumed after state objects are destroyed and recreated from durable storage.
4. **Concurrent replay protection** — atomic nonce consumption yields exactly one winner for simultaneous replay attempts.
5. **Executor reverification** — authorization binding is checked again at the final execution boundary; altered parameters are denied.
6. **Revocation enforcement** — authorization revoked after initial admission but before the final protected operation is denied.
7. **Tamper-evident audit state** — sequential hash linking detects historical modification or deletion.

## Architecture

```text
Participant / untrusted caller
        |
        | Authorization (no resource credential)
        v
Local Enforcement Harness
  - admission verification
  - durable nonce transaction
  - current revocation check
  - final executor reverification
  - tamper-evident audit append
        |
        | executor-held capability only
        v
Protected Resource Service
```

## Durable state

SQLite is used for:

- consumed nonces (primary-key uniqueness + `BEGIN IMMEDIATE` atomic consumption);
- current revocation state;
- ordered audit records with `previous_hash` and `event_hash`.

`PRAGMA journal_mode=WAL` and `PRAGMA synchronous=FULL` are enabled for the local durability experiment.

## Test mapping

| Test | Property | Expected |
|---|---|---|
| P1-F01 | direct bypass denied | unauthenticated resource call denied |
| P1-F02 | executor credential separation | credential absent from request/public executor API |
| P1-F03 | durable replay after restart | replay denied |
| P1-F04 | concurrent replay | exactly one nonce consumption succeeds |
| P1-F05 | revocation at execution boundary | execution denied, no resource effect |
| P1-F06 | executor reverification | substituted authorization denied |
| P1-F07 | audit payload tamper | chain invalid |
| P1-F08 | audit record deletion | chain invalid |
| P1-F09 | governed positive path | one authorized effect + valid audit chain |

## Acceptance rule

`ATE_P1_FIRST_TARGETS_PASS` requires 9/9 focused tests PASS.

A PASS does **not** imply `P1_CONFORMANT`. Full P1 remains governed by the frozen 20-test P1 matrix and all P0 prerequisites.

## Explicit deferred P1 controls

Deferred rather than silently assumed:

- independent CapabilityToken and TrustDecision revocation cases;
- policy supersession/currentness and policy-service fail-closed behavior;
- revocation-service unavailable behavior;
- audit tail-truncation external checkpointing;
- canonicalized target/path traversal control;
- mutable-target / TOCTOU state binding;
- unknown external effect handling;
- audit dependency failure behavior;
- trust-root and revocation epoch rollback resistance;
- participant self-authorization rejection;
- production-grade OS identity isolation / hardware-backed credential custody.

These are successor work, not hidden requirements of this focused milestone.
