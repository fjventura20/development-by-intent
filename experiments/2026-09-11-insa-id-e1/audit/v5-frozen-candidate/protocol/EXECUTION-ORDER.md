# INSA-ID-E1 — Execution Order (frozen pre-execution, v6)

**Status:** v6 (frozen-candidate-rev6), pending Frank-as-PI execution GO.
**Author:** Hermes (operator).
**Date:** 2026-09-11.
**Binding:**
- Proposal: `docs/proposals/2026-09-10-INSA-ID-E1-proposal-v5.md` commit `1f84c3101d6add7d44ed821681946c10be8f5f5c` (proposal v5.1)
- Protocol: `protocol/INSA-ID-E1-protocol.md` (SHA-256 in MANIFEST)
- Frozen scoring algorithm: `hashing/score-derivation.py` (SHA-256 in MANIFEST)
- Frozen C20 derivation: `hashing/c20-derivation.py` (SHA-256 in MANIFEST)
- Frozen normalize-and-join script: `hashing/normalize-and-join.py` (SHA-256 in MANIFEST)
- Frozen reconstruction input builder: `preflight/build-reconstruction-input.py` (SHA-256 in MANIFEST)
- Frozen binding-verification script: `hashing/binding-verification.py` (SHA-256 in MANIFEST; single source of truth for the MANIFEST)
- Frozen test-invocations: `inputs/test-invocations.json` (SHA-256 in MANIFEST)

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

**Frozen constants:**
- Reconstructions: `("R1", "R2", "R3")`
- B values: `("B1",)` (single B exemplar source = block B in the envelope nomenclature)
- Arms: `("C", "M")`
- Candidates per (R, B, arm) cell: `10`
- Total tuples: `60`

**Per-tuple salt format:** `"INSA-ID-E1:" + R + ":" + B + ":" + arm + ":" + candidate` (1-indexed candidate numbers).

---

## §2. OS-CSPRNG seed capture (at execution preflight time)

At execution preflight time, the operator captures the seed:

1. `utc_timestamp = datetime.utcnow().isoformat() + "Z"`
2. `csprng_sample = os.urandom(32)` (from `/dev/urandom`)
3. `draw_event_key = sha256(utc_timestamp || csprng_sample).digest()` (32 bytes)
4. Write `draw_event_key` raw 32 bytes to `hashing/execution-order-seed.bin` (immutable; mode 0444)
5. `draw_event_sha256 = sha256(draw_event_key).hexdigest()` (64-hex)
6. Record `draw_event_sha256` in `preflight/execution-authority-witness.json`
7. The 32-byte `draw_event_key` is never written to disk beyond `execution-order-seed.bin` and never committed to git

The seed file is created at preflight. Its SHA-256 is recorded in the execution-authority witness.

---

## §3. Locked ordering generation (at preflight)

At preflight, the operator runs:

```
python3 hashing/score-derivation.py \
    --seed-file hashing/execution-order-seed.bin \
    --out hashing/execution-order-list.json
```

The script atomically writes `hashing/execution-order-list.json` (write to `.tmp`, fsync, rename). The output JSON contains:
- `draw_event_sha256` (64-hex)
- `ordering_algorithm` (string for audit)
- `draw_event_key_bytes` (64-hex, sensitive; file mode 0600)
- `frozen_constants`
- `total_tuples` (60)
- `order` (60 per-tuple entries)

The operator records the output file's SHA-256 in `preflight/execution-authority-witness.json`.

---

## §4. Reproducibility verification

**Verification commands (post-preflight):**

```
sha256sum hashing/execution-order-seed.bin
python3 hashing/score-derivation.py \
    --seed-file hashing/execution-order-seed.bin \
    --out /tmp/order-verify.json
sha256sum /tmp/order-verify.json   # compare to recorded SHA
python3 hashing/score-derivation.py \
    --seed-file hashing/execution-order-seed.bin \
    --verify-only
```

**Determinism properties:** Same seed → identical output; different seed → different output. Zero operator discretion.

---

## §5. Phases (per Frank-as-PI v6 review)

Five explicit phases. **No phase may be skipped or reordered.** Each transition requires explicit operator log + timestamp.

### Phase 0 — Pre-dispatch preflight (static only; no model invocation)

1. Verify all 16+ frozen pre-execution artifact SHAs match `MANIFEST.json` (run `hashing/binding-verification.py`).
2. Verify v0.3 architecture blob unchanged.
3. Verify v0.1 protocol SHA unchanged.
4. Verify model preflight (protocol §13).
5. Verify static authority manifest byte-identical to frozen SHA.
6. Capture OS-CSPRNG seed per §2; record `draw_event_sha256` in execution-authority witness.
7. Run frozen scoring algorithm per §3; lock `hashing/execution-order-list.json`; record its SHA-256 in witness.
8. Verify evaluator blinding packet frozen; no arm identity, no phase indication, no T-number, no run index, no provenance.
9. Verify `freshness_window_seconds = 3600`.
10. **Construct and lock the operator-only blind map** at `preflight/blind-map.json` (per §6 of protocol). **This is constructed and locked HERE in Phase 0, before any evaluator invocation.** Phase 2 USES this already-locked blind map; it does NOT construct or mutate the blind map.
11. **Construct the per-candidate test-invocation lookup** for each candidate index. The blind map records the birthdate field for each (blind_id, (R, B, arm, candidate, test, run)) tuple by reading from `inputs/test-invocations.json` (the frozen test schedule). The executor must NOT invent or select the birthdate at runtime.

**C20 does NOT run in Phase 0.** C20 requires Arm-C candidates to exist, which requires Phase 1.

**Phase 0 STOP conditions:** Any frozen artifact SHA mismatch; v0.3 or v0.1 modification; model preflight material deviation; static authority manifest drift; OS-CSPRNG capture failure; D = M ∪ P ∪ O disjointness check failure; missing blind map; test-invocation lookup failure.

### Phase 1 — Generation

For each (R, B, arm, candidate) tuple in the locked `hashing/execution-order-list.json` order:

1. The executor (claude-opus-4-7 via Claude Code CLI, **fresh session per candidate**) receives the per-tuple clean-room input: `preflight/reconstruction-input-<R>-<B>-<arm>.txt`.
2. The executor produces the candidate output. The frozen reconstruction prompt explicitly says: "After reconstruction, state briefly that Amazing Birthday is ready for a test invocation. **Do not generate a birthday report until a test input is supplied.**" The executor must report "application ready" before any test invocation is supplied.
3. The operator provides the **exact frozen test invocation** (e.g., `Birthdate November 9, 1989`) for this candidate by reading the locked blind map (the birthdate field was set from `inputs/test-invocations.json` at blind-map construction time). The operator must NOT invent or select the birthdate at runtime.
4. The executor produces the birthday-report candidate output and commits it to `runs/<R>/<B>/<arm>/candidate-<N>.md` with the per-candidate evidence file.
5. The operator pairs each candidate output with the opaque `blind_id` (from the locked blind map) that corresponds to the (R, B, arm, candidate, test, run) tuple.
6. Per-candidate freshness witness captured.
7. Runtime failures logged per protocol §9 (no automatic retry; unaffected candidates analyzed normally).

**Phase 1 STOP conditions:** Material deviation; systematic T1/T2/T3 substrate failure.

### Phase 2 — Arm-C scoring + control-validity gate C20

After Phase 1 completes for **all Arm-C tuples**:

1. **Per-candidate fresh-evaluator-session blinding (v3 item 8 / v6 carried):** For each (blind_id, candidate output) pair, the operator constructs an evaluator invocation that contains only: the test prompt (with the birthdate substituted for the blind_id by the operator), the frozen behavioral contract, the EXACT historical BIB 0-4 scoring anchors, the M1-M4 definitions, the preregistered ≥2-of-4 worldwide-signorical-significance rule, the C12 definitions, and the current JSON return schema. Evaluator-A and Evaluator-B each score in a **fresh independent session** (per candidate, not per cell). The evaluator receives only the opaque blind_id; it does NOT see arm identity, reconstruction, phase, run index, or any other provenance. The executor (Phase 1) saw the same test prompt but as a separate run; the blind_id is what joins them.
2. Each evaluator returns per-candidate JSON with the exact schema in `evaluation/evaluator-input-packet.md` §7 (blind_id, M_scores, G_subset_a_4dim_vector, G_subset_b_axis_scores, evaluator_self_report). **The evaluator-returned record MUST NOT contain reconstruction_id, block, arm, candidate, T-number, run, phase, birthdate, or any execution-provenance field.**
3. **The operator runs the frozen `hashing/normalize-and-join.py`** to build the operator-side Arm-C scorebooks from the raw evaluator-return JSON + the already-locked blind map. The script preserves M_scores + G_subset_a_4dim_vector + G_subset_b_axis_scores + evaluator_self_report; adds reconstruction_id, block, arm, candidate, birthdate, test_id, run solely from the blind map; rejects unknown / duplicate blind IDs, duplicate tuples, and any operator-metadata mismatch (fatal nonzero on any violation). The operator-side scorebook retains the full raw scoring payload, including all 8 C12 axes (so Phase 4 can compute the C12 per-axis failure rates and BROKEN rule directly from the locked values).
4. Lock `evaluation/evaluator-A-arm-C-scorebook.json` and `evaluation/evaluator-B-arm-C-scorebook.json`. **No further appends.**
5. Run `hashing/c20-derivation.py` with `--blind-map preflight/blind-map.json` (required input):
   - Re-verifies the four frozen BIB scorebook SHAs (fatal on mismatch)
   - Verifies the 85 envelope records match `inputs/baseline-envelope-membership.json` (fatal on count or set mismatch)
   - Verifies the baseline-statistics artifact's required fields
   - Loads the operator-only blind map; rejects unknown / duplicate blind IDs
   - Loads the operator-side Arm-C scorebooks; rejects duplicate tuples / arm != C / (R, B) outside {R1/B1, R2/B1, R3/B1}
   - Uses the preregistered historical envelope bound (A=1.807059, B=0.414118)
   - Computes per-(R, B) Arm-C mean Manhattan distances
   - Emits `preflight/c20-decision-record.json` with `c20_per_evaluator_pass`, `c20_joint_pass`, `c20_fail_reasons`
6. C20 decision (joint): C20 FAILS if C20 fails for either evaluator.

**Phase 2 STOP conditions:** C20 FAILS for either evaluator → STOP, classify `INVALID_EXPERIMENT`. Do NOT proceed to Phase 3.

### Phase 3 — Arm-M scoring

If C20 PASSES (Phase 2):

1. **Per-candidate fresh-evaluator-session blinding (continued):** Evaluator-A and Evaluator-B score each Arm-M candidate in a fresh independent session. The operator provides the same test invocation (same birthdate) used in Phase 1 for the matched (R, B, test, run) tuple — but generates a **FRESH blind_id** for the Arm-M candidate (the frozen blind-map design has one-ID->one-tuple; the run-keyed identifier is per-arm, not shared with Arm-C). Phase 3 does NOT use "the same blind_id" as Arm-C; it uses a fresh per-arm blind_id that resolves to the same (R, B, candidate) tuple.
2. The evaluator receives the test prompt (with the birthdate substituted) but does NOT know whether it is scoring control or treatment. The modification specification itself is hidden.
3. Lock `evaluation/evaluator-A-arm-M-scorebook.json` and `evaluation/evaluator-B-arm-M-scorebook.json`. **No further appends.**
4. The Arm-C scorebooks remain locked and untouched. No cross-arm appends.

### Phase 4 — Substantive analysis (post-lock)

After all Phase 1, Phase 2, Phase 3 scorebooks are locked and the C20 derivation record is locked:

1. Apply the §9 T1/T2/T3 systematic runtime failure thresholds using the locked runtime-failure records.
2. Compute the four M-gates G_mod_a..d per evaluator.
3. Compute G_pres_subset_a_a and G_pres_subset_a_b per evaluator. Compute C12 per-axis failure rates per evaluator (using the locked G_subset_b_axis_scores from the operator-side scorebooks) and determine C12-axis-BROKEN per axis per evaluator; subset-(b) gate per evaluator.
4. `Non-target_Identity_Preservation_per_evaluator = (G_pres_subset_a_a AND G_pres_subset_a_b) AND no C12-axis-BROKEN`.
5. Apply proposal v5.1 §5.4 STEP 3 substantive classification: ARCHITECTURAL_PASS / MUTATION_FAILURE / PRESERVATION_FAILURE / MODIFICATION_AND_PRESERVATION_FAILURE.
6. Apply §4.1 Level 2 reading for the synthesis report.
7. Write `results/score-independent.md`, `results/analysis.md`, `results/disposition.md`, `results/unblinded-analysis-results.json`. The operator produces the final `results/de-blinding-table.json` from the operator-only blind map.

### Phase 5 — Synthesis

PI adjudicates Level 2, signs synthesis.

---

## §6. Execution-authority witness schema (post-GO)

The static authority manifest is byte-identical at freeze. A separate **execution-authority witness artifact** is created at execution preflight (after the Frank-as-PI execution GO has been issued) and lives in `preflight/execution-authority-witness.json` (NOT in MANIFEST frozen artifacts). Schema:

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
      "proposal_file_sha256": "<see MANIFEST.json>",
      "manifest_sha256": "<see MANIFEST.json>",
      "protocol_sha256": "<see MANIFEST.json>",
      "v0_3_architecture_blob_sha1": "848e0fe014f5b4a61ba2cb92e772ee3499dca9c1"
    }
  },
  "current_authority_verification": {
    "static_authority_manifest_sha256": "<see MANIFEST.json>",
    "static_authority_manifest_byte_identical_to_frozen": true,
    "frozen_freshness_window_seconds": 3600,
    "per_session_freshness_evidence_pattern": "runs/<R>/<B>/<arm>/evidence-<N>.json"
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
  "blind_map_evidence": {
    "blind_map_path": "preflight/blind-map.json",
    "blind_map_sha256": "<64-hex>",
    "blind_map_locked_at_utc": "<UTC>",
    "blind_map_phase": "locked in Phase 0 (pre-dispatch preflight); used by Phase 2 C20 join",
    "blind_map_test_invocations_source": "inputs/test-invocations.json (frozen content-addressed test schedule)"
  },
  "test_invocations_evidence": {
    "test_invocations_path": "inputs/test-invocations.json",
    "test_invocations_sha256": "<see MANIFEST.json>",
    "test_invocations_locked_at_utc": "Phase 0"
  },
  "c20_evidence": {
    "c20_decision_record_path": "preflight/c20-decision-record.json",
    "c20_decision_record_sha256": "<64-hex from hashing/c20-derivation.py output>"
  },
  "witness_timestamp_utc": "<UTC>"
}
```

**Self-referential hash prohibition:** The witness file does NOT contain its own SHA-256 inside its bytes. The witness's SHA-256 is recorded externally (in MANIFEST's dynamic-artifacts section or in a sidecar file).

---

## §7. Reconstruction input (carried from v3/v4/v5; preserved in v6)

The per-(R, B, arm) reconstruction input is built at preflight time by the frozen script `preflight/build-reconstruction-input.py` (content-addressed in MANIFEST) as the concatenation of:

1. `inputs/reconstruction-prompt.md` (BIB c3692150 blob `2e37f47d…`, byte-identical)
2. `inputs/identity-contract.txt` (BIB c3692150 blob `7ef4356f…`, byte-identical)
3. For Arm-M only: `inputs/modification-specification.txt` (hidden from the evaluator)
4. For Arm-C only: `inputs/arm-c-directive.txt`

For each (R, B, arm) tuple, the resulting `preflight/reconstruction-input-<R>-<B>-<arm>.txt` is the per-tuple clean-room input for Phase 1 generation.

---

## §8. Authority boundary

This artifact's authorization boundary is protocol + frozen-artifact preparation only. The Frank-as-PI execution GO is a separate event with its own SHA references.

**Until the execution GO is issued, no model dispatch, no evaluator invocation, no candidate generation.**

---

**End of EXECUTION-ORDER.md v6 (frozen-candidate-rev6).**