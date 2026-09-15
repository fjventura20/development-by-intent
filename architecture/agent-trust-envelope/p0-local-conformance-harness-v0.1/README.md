# ATE P0 Local Conformance Harness v0.1

Deterministic, local-only harness for the 15 mandatory P0 tests in `ATE-P0-P1-CONFORMANCE-TEST-PLAN-v0.1.md`.

## Run

```bash
python run_p0.py
```

Dependencies: Python 3.11+ and `cryptography`.

No model, provider, Hermes participant, external evaluator, or network call is used.

The harness uses deterministic Ed25519 fixture authorities and sandbox/in-memory execution state. A passing result demonstrates P0 logical/mechanical conformance only; it does not establish P1 isolation, durable replay state, host-compromise resistance, or production key custody.
