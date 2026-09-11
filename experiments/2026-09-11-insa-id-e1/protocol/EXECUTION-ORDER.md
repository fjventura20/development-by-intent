# INSA-ID-E1 — Execution Order (frozen pre-execution, v3)

**Status:** v3 (frozen-candidate-rev3), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:**
- Proposal: `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` commit `1f84c3101d6add7d44ed821681946c10be8f5f5c` (proposal v5.1)
- Protocol: `protocol/INSA-ID-E1-protocol.md` (SHA-256 filled at MANIFEST freeze)
- Frozen scoring algorithm: `hashing/score-derivation.py` (SHA-256 in MANIFEST)
- Frozen C20 derivation: `hashing/c20-derivation.py` (SHA-256 in MANIFEST)
- Frozen reconstruction input builder: `preflight/build-reconstruction-input.py` (SHA-256 in MANIFEST)

---

## §1. Frozen execution-order algorithm

The execution order is produced by a **single deterministic algorithm** defined at protocol freeze: the operator (Hermes) has **zero discretion** in producing the ordering after GO.

**Algorithm:** `hashing/score-derivation.py` (Python 3 standard library only). The script takes an immutable 32-byte seed file as input and produces a JSON file containing the locked ordering of all 60 (R, B, arm, candidate) tuples.

**Scoring rule (frozen):**
```
salt_t = sha256("INSA-ID-E1:" + R + ":" + B + ":" + arm + ":" + candidate)
score_t = first 8 bytes of HMAC-SHA256(draw_event_key, salt_t), interpreted as little-endian uint64
Sort tuples ascending by score_t; tie-break by lexicographic (R, B, arm, candidate).
```

**Frozen constants in the script:**
- Reconstructions: `("R1", "R2", "R3")` (matches v0.1 BIB-001 non-deviated count)
- B values: `("B1",)` (single BIB exemplar source)
- Arms: `("C", "M")` (control, modification)
- Candidates per (R, B, arm) cell: `10`
- Total tuples: `60`

**Per-tuple salt format:** `"INSA-ID-E1:" + R + ":" + B + ":" + arm + ":" + candidate` (1-indexed candidate numbers).

---

## §2. OS-CSPRNG seed capture (at execution preflight time)

At execution preflight time (NOT at protocol freeze time), the operator captures the seed as follows:

1. Capture `utc_timestamp = datetime.utcnow().isoformat() + "Z"`
2. Capture `csprng_sample = os.urandom(32)` (from `/dev/urandom` on Linux)
3. Compute `draw_event_key = sha256(utc_timestamp || csprng_sample).digest()` (32 bytes)
4. Write `draw_event_key` raw 32 bytes to `hashing/execution-order-seed.bin` (immutable; mode 0444 after write)
5. Compute `draw_event_sha256 = sha256(draw_event_key).hexdigest()` (64-hex)
6. Record `draw_event_sha256` (64-hex, NOT the draw_event_key bytes) in the execution-authority witness (§6 below)
7. The 32-byte `draw_event_key` itself is **never** written to disk in plain form beyond `execution-order-seed.bin`, and is **never** committed to git

The seed file `hashing/execution-order-seed.bin` is created at preflight. It is **not** in MANIFEST.json's frozen artifacts (because it doesn't exist at protocol freeze time); it is a dynamic artifact created at preflight under the static-authority policy. Its SHA-256 is recorded in the execution-authority witness.

---

## §3. Locked ordering generation (at preflight)

At preflight time, after the seed file is created, the operator runs:

```
python3 hashing/score-derivation.py \
    --seed-file hashing/execution-order-seed.bin \
    --out hashing/execution-order-list.json
```

The script atomically writes `hashing/execution-order-list.json` (write to `.tmp`, fsync, rename). The output JSON contains:
- `draw_event_sha256` (64-hex, top-level)
- `ordering_algorithm` (string describing the algorithm for audit)
- `draw_event_key_bytes` (64-hex, included for reproducibility; the bytes themselves are sensitive and the file should be mode 0600)
- `frozen_constants` (the script's frozen constants for cross-check)
- `total_tuples` (60)
- `order` (the ordered list of 60 per-tuple entries)

The operator records the output file's SHA-256 in `preflight/execution-authority-witness.json` (§6).

---

## §4. Reproducibility verification

**Verification command (post-preflight, can be run at any time):**

```
# 1. Confirm seed file bytes match recorded SHA
sha256sum hashing/execution-order-seed.bin

# 2. Re-run the scoring algorithm with the same seed; confirm output SHA matches
python3 hashing/score-derivation.py \
    --seed-file hashing/execution-order-seed.bin \
    --out /tmp/order-verify.json
sha256sum /tmp/order-verify.json   # compare to recorded SHA in witness

# 3. Verify-only mode prints the first/last tuples for spot-check
python3 hashing/score-derivation.py \
    --seed-file hashing/execution-order-seed.bin \
    --verify-only
```

**Determinism properties (verified during v2 freeze with synthetic seeds):**
- Same seed file → identical output SHA (deterministic)
- Different seed file → different output (seed-sensitive)
- No operator discretion: the script takes no operator input beyond the seed file path and the output path

---

## §5. Phases (per Frank-as-PI v3 review)

The experiment runs in five explicit phases. **No phase may be skipped or reordered.** Each phase transition requires explicit operator log + timestamp.

### Phase 0 — Pre-dispatch preflight (static only)

Static checks that can be performed without any model invocation:

1. Verify all 16+ frozen pre-execution artifact SHAs match `MANIFEST.json`.
2. Verify the frozen v0.3 architecture blob (`848e0fe014f5b4a61ba2cb92e772ee3499dca9c1`) is unchanged in git history.
3. Verify the dbi-evolution-v0.1 frozen protocol SHA-256 (`079138163f0b59f71002480feffc008d9b350d460731c5d51f037163b17c2ab4`, blob `8874692d560d9a6363ef4105fae5384b18cf6ef2`) is unchanged.
4. Verify model preflight (protocol §13): model identifiers (claude-opus-4-7 executor; gpt-5.6-sol evaluator A; claude-opus-4-7 evaluator B), CLI versions, frozen source commits, tool postures, authentication paths.
5. Verify the static authority manifest is current and the grant provenance references the Frank-as-PI protocol-authorization approval (v5.1 commit `1f84c31`).
6. Capture the OS-CSPRNG seed per §2 above; record `draw_event_sha256` in the execution-authority witness.
7. Run the frozen scoring algorithm per §3 above; lock `hashing/execution-order-list.json`; record its SHA-256 in the execution-authority witness.
8. Verify evaluator blinding packet (`evaluation/evaluator-input-packet.md`) is frozen and contains no arm identity, no reconstruction number, no experiment identity, no candidate number, no phase indication.
9. Verify the executor's `freshness_window_seconds` (from the frozen authority manifest) is acceptable for the planned execution duration.

**C20 does NOT run in Phase 0.** C20 requires Arm-C candidates to exist, which requires Phase 1.

**Phase 0 STOP conditions:**
- Any frozen artifact SHA mismatch → STOP, classify `INVALID_EXPERIMENT`.
- v0.3 or v0.1 modification detected → STOP, classify `INVALID_EXPERIMENT`.
- Model preflight deviation material and unadjudicated → STOP.
- Static authority manifest outdated → STOP.
- OS-CSPRNG seed capture fails → STOP.

### Phase 1 — Generation

For each (R, B, arm, candidate) tuple in the locked `hashing/execution-order-list.json` order:

1. The executor (claude-opus-4-7 via Claude Code CLI, **fresh session per candidate**) receives the per-tuple clean-room input: the pre-built reconstruction input file (`preflight/reconstruction-input-<R>-<B>-<arm>.txt`).
2. The executor produces the candidate output and commits it to `runs/<R>/<B>/<arm>/candidate-<N>.md` with the per-candidate evidence file (`runs/<R>/<B>/<arm>/evidence-<N>.json`) per protocol §12.
3. Per-candidate freshness witness is captured (session_creation_timestamp, m_commit_timestamp) for INV-AUTH-5.
4. Runtime failures are logged per protocol §9 (no automatic retry; unaffected candidates analyzed normally).

**Phase 1 STOP conditions:**
- Material deviation during generation → STOP per protocol §15.
- Evaluator substrate failure (systematic T1/T2/T3) → STOP per proposal v5.1 §5.5.

### Phase 2 — Arm-C scoring + control-validity gate C20

After Phase 1 completes for **all Arm-C tuples** (regardless of whether all Arm-M tuples have completed — Phase 2 only requires Arm-C candidates to exist):

1. **Per-candidate fresh-evaluator-session blinding** (v3 item 8): Evaluator-A and Evaluator-B score each Arm-C candidate in a **fresh independent session** (per candidate, not per cell). The evaluator receives only the blinded evaluator input packet. No evaluator session is told "this is Phase 2" or "control" or any cue from which staged arm identity could be inferred.
2. Lock `evaluation/evaluator-A-arm-C-scorebook.json` and `evaluation/evaluator-B-arm-C-scorebook.json`. Locked = SHA-256 recorded in `results/score-independent.md`. **No further appends permitted** to the locked Arm-C scorebooks.
3. Construct `results/de-blinding-table.json` (operator-side, post-lock, auditable; maps blinded IDs to (R, B, arm, candidate) tuples).
4. **Compute C20 deterministically via `hashing/c20-derivation.py`** (per §8 of protocol):
   - Re-verify the four frozen BIB scorebook SHAs (mismatch → fatal; cannot derive C20)
   - Load 85 envelope records from `inputs/baseline-statistics.json`
   - Compute per-evaluator 4-dim reference vectors (mean of 85 envelope observations per dim)
   - Compute C20 envelope bounds per evaluator (max per-(R, B) mean 4-dim Manhattan-from-ref across 85 envelope)
   - Compute per-(R, B) Arm-C mean Manhattan distances per evaluator from the locked Arm-C scorebooks
   - C20 PASS for evaluator e IF AND ONLY IF (a) no missing envelope cells AND (b) every (R, B) cell mean <= C20 envelope bound[e]
   - C20 joint PASS iff both evaluators PASS
   - Output: `preflight/c20-decision-record.json` (SHA-256 recorded externally in `results/score-independent.md`)
5. C20 decision (joint): C20 FAILS if C20 fails for either evaluator.

**Phase 2 STOP conditions:**
- C20 FAILS for either evaluator → STOP, classify `INVALID_EXPERIMENT` (per proposal v5.1 §5.4). Do NOT proceed to Phase 3.
- Scorebook locking violation (post-lock edit detected) → STOP, deviation record, classify per §15.

### Phase 3 — Arm-M scoring

If C20 PASSES (Phase 2):

1. **Per-candidate fresh-evaluator-session blinding** (v3 item 8): Evaluator-A and Evaluator-B score each Arm-M candidate in a **fresh independent session** (per candidate, not per cell). The evaluator receives only the blinded evaluator input packet. No evaluator session is told "this is Phase 3" or "modification" or any cue from which staged arm identity could be inferred.
2. Lock `evaluation/evaluator-A-arm-M-scorebook.json` and `evaluation/evaluator-B-arm-M-scorebook.json`. Locked = SHA-256 recorded in `results/score-independent.md`. **No further appends permitted.**
3. The Arm-C scorebooks remain locked and untouched. No cross-arm appends.

### Phase 4 — Substantive analysis (post-lock)

After all Phase 1, Phase 2, Phase 3 scorebooks are locked and the C20 derivation record is locked:

1. Apply the §9 T1/T2/T3 systematic runtime failure thresholds using the locked runtime-failure records. If any threshold is met, classify `EXECUTOR_RUNTIME_FAILURE` and STOP substantive analysis for the affected substrate.
2. Compute the four M-gates G_mod_a..d per evaluator (per `inputs/acceptance-tests.json`). `Modification_Success_per_evaluator = G_mod_a AND G_mod_b AND G_mod_c AND G_mod_d`.
3. Compute G_pres_subset_a_a and G_pres_subset_a_b per evaluator (per `inputs/preservation-gates.json`). Compute C12 per-axis failure rates per evaluator; determine C12-axis-BROKEN per axis per evaluator; subset-(b) gate per evaluator.
4. `Non-target_Identity_Preservation_per_evaluator = (G_pres_subset_a_a AND G_pres_subset_a_b) AND no C12-axis-BROKEN`.
5. Apply proposal v5.1 §5.4 STEP 3 substantive classification: emit one of `ARCHITECTURAL_PASS`, `MUTATION_FAILURE`, `PRESERVATION_FAILURE`, `MODIFICATION_AND_PRESERVATION_FAILURE`.
6. Apply proposal v5.1 §4.1 Level 2 reading for the synthesis report.
7. Write `results/score-independent.md` (locked), `results/analysis.md`, `results/disposition.md`, `results/unblinded-analysis-results.json`.

### Phase 5 — Synthesis

PI adjudicates Level 2, signs synthesis.

---

## §6. Execution-authority witness schema (post-GO)

The static authority manifest is byte-identical at freeze. A separate **execution-authority witness artifact** is created at execution preflight time (after the Frank-as-PI execution GO has been issued) and lives in `preflight/execution-authority-witness.json` (NOT in MANIFEST frozen artifacts). Schema:

```json
{
  "schema_version": "1.0",
  "witness_kind": "execution-authority-witness",
  "experiment_id": "INSA-ID-E1",
  "execution_GO": {
    "issuer": "Frank (PI)",
    "message_provenance": {
      "telegram_sender": "Frank Ventura",
      "telegram_thread": "Hermes Workstreams, topic 279",
      "telegram_timestamp_utc": "<post-GO message UTC>",
      "telegram_message_id": "<post-GO message id>"
    },
    "execution_GO_timestamp_utc": "<UTC>",
    "execution_GO_referenced_shas": {
      "proposal_commit_sha": "1f84c3101d6add7d44ed821681946c10be8f5f5c",
      "proposal_file_sha256": "f675090e4d72a50bd2c86445fd1154585539359f38e6f9ecd3c9db20cfb599f1",
      "manifest_sha256": "<filled at GO time>",
      "protocol_sha256": "<filled at GO time>",
      "v0_3_architecture_blob_sha1": "848e0fe014f5b4a61ba2cb92e772ee3499dca9c1"
    }
  },
  "current_authority_verification": {
    "static_authority_manifest_sha256": "<frozen manifest SHA>",
    "static_authority_manifest_byte_identical_to_frozen": true,
    "frozen_freshness_window_seconds": 3600,
    "per_session_freshness_evidence": "<per-candidate witness file path pattern>"
  },
  "session_freshness_evidence_pattern": "runs/<R>/<B>/<arm>/evidence-<N>.json",
  "execution_order_evidence": {
    "draw_event_sha256": "<64-hex from §2>",
    "execution_order_list_sha256": "<64-hex from §3>",
    "execution_order_algorithm_sha256": "<score-derivation.py SHA from MANIFEST>"
  },
  "permitted_authentication_fingerprint_evidence": {
    "auth_token_sha256": "<hash only; never plaintext>",
    "auth_token_capture_time_utc": "<UTC>",
    "auth_token_byte_identical_to_go_authorization": true
  },
  "witness_timestamp_utc": "<UTC>"
}
```

**Self-referential hash prohibition:** The witness file does NOT contain its own SHA-256 inside its bytes. The witness's SHA-256 is recorded externally in `results/score-independent.md` and in MANIFEST's dynamic-artifacts section. Use a sidecar file `preflight/execution-authority-witness.sha256.txt` for the local record.

The witness captures all dynamic execution-time fields; the frozen static manifest stays byte-identical. Secrets (the OAuth token itself, etc.) are never written to disk in plaintext — only their SHA-256 hashes.

---

## §7. Reconstruction input (correction from v1; preserved in v3)

The per-(R, B, arm) reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py` (content-addressed in MANIFEST) as the **concatenation** of:

1. The frozen BIB reconstruction prompt (already content-addressed at `inputs/reconstruction-prompt.md`, byte-identical to git blob `2e37f47d99059238bd9484560e310d2f89744069` at c3692150).
2. The frozen BIB behavioral baseline (already content-addressed at `inputs/identity-contract.txt`, byte-identical to git blob `7ef4356f657884d65dbd4462d85c1c81b3f6fa2a` at c3692150).
3. For Arm-M only: the modification specification (`inputs/modification-specification.txt`, content-addressed).
4. For Arm-C only: the no-op directive (`inputs/arm-c-directive.txt`, content-addressed).

For each (R, B, arm) tuple, the resulting `preflight/reconstruction-input-<R>-<B>-<arm>.txt` is the per-tuple clean-room input for Phase 1 generation.

---

## §8. Authority boundary

This artifact's authorization boundary is protocol + frozen-artifact preparation only. The Frank-as-PI execution GO is a separate event with its own SHA references.

**Until the execution GO is issued, no model dispatch, no evaluator invocation, no candidate generation.**

---

**End of EXECUTION-ORDER.md v3 (frozen-candidate-rev3).**