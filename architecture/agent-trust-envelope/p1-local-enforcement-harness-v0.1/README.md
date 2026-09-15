# ATE P1 Local Enforcement Harness v0.1

Deterministic, local-only harness for the first high-value P1 enforcement targets. It intentionally makes **zero model calls** and does not invoke Hermes, providers, or external evaluators.

## Scope

This milestone exercises:

- P1-01 direct resource bypass denial (service-level protected resource);
- P1-02 executor credential separation;
- P1-03 executor reverification / authorization substitution rejection;
- P1-04 durable replay prevention across process restart;
- P1-05 atomic concurrent replay protection;
- P1-06/P1-07 revocation at the execution boundary (modeled as current subject authorization revocation in this focused harness);
- P1-11/P1-12 tamper-evident sequential audit state.

It also includes one clean successful governed execution.

## Run

```bash
python run_p1.py
```

Expected result:

```text
9 passed
ATE_P1_FIRST_TARGETS_PASS
```

## Important limitation

This is **not** a claim of full P1 conformance. The frozen ATE P0/P1 conformance plan requires all P0 tests plus 20/20 mandatory P1 tests. This harness is the first-target enforcement milestone only.

The service-level resource boundary proves that an unauthenticated caller cannot exercise the protected resource interface. It does not establish resistance to host/root compromise, same-UID debugger/process introspection, hardware-backed credential custody, or distributed-service compromise.
