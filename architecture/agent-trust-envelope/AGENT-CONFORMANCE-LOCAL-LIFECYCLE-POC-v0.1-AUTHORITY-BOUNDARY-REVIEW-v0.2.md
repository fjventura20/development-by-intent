# Agent Conformance Local Lifecycle PoC v0.1 — Authority Boundary Review v0.2

**Candidate implementation/test baseline:** `82dc8df570b5946fb291575a44e73755b6c3213a`

## Disposition

**PASS FOR ISOLATED DEVELOPMENT PYTEST**

**FORMAL RUN NOT AUTHORIZED**

This review supersedes the prior authority-boundary review that pinned
`7d6dad17cf95c2e29afdf45b97c73a07f54bc870`.

## Additional v0.2 finding closed — authoritative QA at capability issuance

The frozen design requires the Authorization Service itself to verify current
qualification/admission state on every relevant authorization decision.

The prior candidate verified caller-supplied signed QA snapshots at issuance.
After authoritative revocation, a participant could replay an older signed
`ACTIVE` fixture and obtain a fresh capability. The executor would later deny
that capability when resolving current state, but issuance itself violated the
frozen authorization-service contract.

The corrected Authorization Service now:

1. resolves authoritative subject identity from StateStore;
2. rejects caller role/domain values that disagree with authoritative identity;
3. resolves qualification/admission fixtures from StateStore by stable artifact ID;
4. verifies the authoritative current fixtures, including `current_state == ACTIVE`;
5. treats caller QA artifacts only as identifiers of the authoritative records;
6. checks current lifecycle state;
7. signs only the frozen governed action digest.

New regressions:

- `test_ab06_authorization_rejects_stale_active_qualification_after_revocation`
- `test_ab07_authorization_rejects_mutated_participant_subject_binding`

Both tests use the exact frozen governed `ACTION_PAYLOAD`, so denial cannot be
satisfied accidentally by the action-digest gate.

## Previously closed authority boundaries retained

The candidate also retains:

- no public raw `private_key` authority attributes;
- R13 binding to current observer-authoritative signed evidence;
- R13 post-invalidation freshness enforcement;
- authoritative qualification/admission state in R13;
- insert-only subject/qualification/admission registration;
- defensive subject, observer-evidence, and audit snapshots;
- one-time bound observer evidence writer;
- one-time bound protected-resource authority;
- immutable frozen profile registry installation;
- authorization restricted to the frozen governed action;
- participant-facing denial of observer/audit/resource authority mutation.

## Test inventory

Static inventory at `82dc8df...`:

- lifecycle: 23
- negative security: 8
- audit: 9
- attack regressions: 34
- authority-boundary regressions: 7

**Total: 81 tests**

This is inventory only. Runtime PASS is still required.

## Next gate

Run exactly the complete 81-test suite from a clean detached worktree pinned to:

`82dc8df570b5946fb291575a44e73755b6c3213a`

No code corrections during the run.
No successor dry-run.
No formal execution.
No merge.

Only after an exact clean pytest result may the successor runner be revalidated.
