# Intelligence-Native Software Architecture (INSA) v0.3 — FROZEN BASELINE

**Status:** FROZEN  
**Freeze date:** 2026-09-09  
**Frozen normative source:** [`INSA-ARCHITECTURE-v0.3-candidate.md`](INSA-ARCHITECTURE-v0.3-candidate.md)  
**Frozen source commit:** `d2c2ad93d95d048e6e2e0c3d42d993a1ecd40f1b`  
**Frozen source Git blob SHA:** `848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`  
**Final freeze review:** [`INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md`](INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md)  
**Freeze-review disposition:** `PASS_FOR_ARCHITECTURE_FREEZE`

## Freeze rule

The exact contents of `INSA-ARCHITECTURE-v0.3-candidate.md` identified by the source commit and blob SHA above constitute **INSA Architecture v0.3 FROZEN**.

The word `candidate` in the historical source filename and header does not alter the freeze. The freeze is established by this manifest and the exact Git object identity above.

The frozen source MUST NOT be edited in place for any experiment claiming to use INSA v0.3 FROZEN.

Any architectural change requires a new version, such as v0.4, and MUST NOT retroactively alter the v0.3 baseline.

## Experimental boundary enabled

The next experiment may now be designed against this frozen architecture:

**INSA-ID-E1 — Targeted Evolution With Preservation**

The experiment design must bind before execution:

```text
B = frozen baseline
D = scored behavioral dimensions
M = mutation dimensions
P = preservation dimensions
O = out-of-scope dimensions
V(d) = dimension-specific permitted variance
A = acceptance tests bound to M
G = preservation gates bound to P
```

No experiment execution is authorized by this freeze manifest itself.

A separate experimental protocol and execution authorization are required.
