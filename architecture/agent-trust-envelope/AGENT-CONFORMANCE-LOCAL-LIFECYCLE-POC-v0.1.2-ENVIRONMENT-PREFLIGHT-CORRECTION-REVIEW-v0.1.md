# Agent Conformance Local Lifecycle PoC v0.1.2
## Environment-Preflight Correction Review v0.1

**Correction commit reviewed:** `7d7a680c68f7493d8be7e68dc6e636c264a36c4a`
**Correction parent:** `fd39cce365a09119cc20d1630ff75137a3008121`
**Reviewed implementation baseline:** `ffa03453818b15b3643ff3b1c77fabb446f38ea6`
**Review method:** narrow static review plus in-memory gate tests
**Hermes or external model execution:** none
**Development dry run executed by this review:** no
**Formal run authorized or executed:** no

---

## 1. Disposition

```text
ENVIRONMENT_PREFLIGHT_CORRECTION: PASS
ONE_FRESH_DEVELOPMENT_DRY_RUN: AUTHORIZED
FORMAL_RUN: NOT_AUTHORIZED
```

The correction is bounded to detecting an unavailable pytest dependency before
the runner creates an evidence directory or invokes the test suite. It does not
change conformance behavior, lifecycle logic, evidence thresholds, signature
verification, the independent verifier, the reviewed implementation baseline,
or either formal authorization gate.

---

## 2. Finding Reviewed

The isolated attempt at runner commit `fd39cce` reached the pytest subprocess
with an interpreter that did not contain pytest. The subprocess exited before
collection, but the runner labeled the result `CONFORMANCE_LIFECYCLE_POC_FAIL`.

Because no conformance test or scored lifecycle operation executed, the
controlling disposition is `STOP_BEFORE_SCORING`, not a conformance failure.

---

## 3. Exact Correction

The runner now:

1. imports `importlib.util`;
2. calls `require_test_environment()` after the formal authorization gate and
   before run identity or evidence-directory creation;
3. requires `importlib.util.find_spec("pytest")` to resolve;
4. raises exactly `STOP_BEFORE_SCORING: pytest dependency unavailable` when it
   does not resolve.

No other runner logic changed.

---

## 4. Verification Results

| Check | Result |
|---|---|
| Missing-pytest simulation returns the exact fail-closed reason | PASS |
| Available-pytest simulation permits continuation | PASS |
| Corrected runner parses as valid Python | PASS |
| Reviewed implementation subtree differs from `ffa0345` | 0 files |
| Runner change scope | 1 file |
| `ACL_FORMAL_RUN_AUTHORIZED` gate remains present | PASS |
| `ACL_REVIEWED_DRY_RUN_GATE` gate remains present | PASS |
| Failed attempt contains exactly three preserved files | PASS |
| All three preserved file hashes match the failure record | PASS |

---

## 5. Authorized Execution Boundary

One fresh default-mode development dry run may execute only when:

- the checkout is detached and clean at the commit containing this review;
- pytest and the existing cryptographic dependency are importable from the
  exact interpreter used to invoke the runner;
- both formal authorization environment variables are absent;
- the prior failed evidence directory remains untouched;
- a new run ID and evidence directory are created;
- the runner is invoked exactly once, without a separate pytest invocation.

If the runner stops or fails, do not retry. Preserve its output and return for
adjudication.

No merge to `main` is authorized by this review.
