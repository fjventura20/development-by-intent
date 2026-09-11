# INSA-ID-E1 — Audit Trail

This directory preserves the v1 frozen-candidate package as audit trail. The v2 protocol revision was created in response to Frank-as-PI corrections at 2026-09-11 (after the v1 freeze at commit `26f7ed3ecc588a292fbe6983105b0c28ec0c24f5`).

## v1 frozen-candidate (audit-only)

**Commit:** `26f7ed3ecc588a292fbe6983105b0c28ec0c24f5` (pushed to `origin/feature/insa-id-e1-proposal`)
**Status:** Frozen-candidate; superseded by v2.
**MANIFEST.json SHA-256:** `8052e7cfa2403d87faaa4d5008cd13f5f0cafe359e1d1963f2a3c674c605141a`

The 20 files in `v1-frozen-candidate/` are byte-identical to the v1 commit's `experiments/2026-09-11-insa-id-e1/` tree (excluding this audit directory itself).

### v1 defects identified by Frank-as-PI review

1. **Modification_Success semantics wrong.** v1's `inputs/acceptance-tests.json` defined G_mod_c/G_mod_d as intra-evaluator rescoring checks (A-mod-c/A-mod-d) instead of the proposal v4 four-gate pattern. v2 restores the exact four gates: G_mod_a (mean M-conformance ≥3.5/4), G_mod_b (≥80% of Arm-M candidates pass all four M checks), G_mod_c (every Arm-M reconstruction ≥70% all-pass), G_mod_d (Arm-M all-pass rate exceeds Arm-C by ≥50pp).
2. **C12 aggregate rule wrong.** v1 required every individual candidate to pass all eight axes. v2 restores the v0.1-style joint rule: an axis is BROKEN only when Arm-M failure rate on that axis ≥30% AND Arm-M failure rate is ≥30pp worse than Arm-C; preservation fails for an evaluator if ANY of the eight axes is BROKEN.
3. **Scorebooks vs aggregate computation conflated.** v1's evaluator-input-packet had evaluators attempt to compute G_pres_a, but G_pres_a requires contemporaneous Arm-C and Arm-M reconstruction-level statistics that the blinded evaluator cannot see. v2 separates: evaluators return per-candidate raw scores only; the analysis layer (post-lock) computes G_pres_a, G_pres_b, C12 per-axis failure rates, C12-axis-BROKEN.
4. **Execution-order algorithm not frozen.** v1 referenced `hashing/score-derivation.py` as "generated at preflight," leaving the actual ordering algorithm unspecified at freeze — operator discretion. v2 provides the exact deterministic scoring algorithm, content-addressed in MANIFEST.
5. **C20 phase wrong.** v1's protocol §8 placed C20 as a pre-dispatch preflight gate, but C20 verifies Arm-C candidates against the BIB envelope and Arm-C candidates do not exist until generation. v2 moves C20 to the correct phase: pre-dispatch preflight (static only) → generation → Arm-C scoring + C20 → M-arm scoring + substantive analysis.
6. **Authority manifest mutable.** v1's authority manifest contained fields that must be edited at execution time (auth-token SHA, freshness witness). v2 freezes all static policy (including the freshness window in seconds) in the manifest; a separate dynamic `execution-authority-witness.json` artifact is created at preflight (post-GO) carrying execution-time fields.
7. **MANIFEST proposal_binding.sha256 misnamed.** v1's `proposal_binding.sha256` field actually contained the Git commit SHA `ed95705...`, not a SHA-256 hash. v2 separates into `proposal_commit_sha` (the Git commit SHA, 40 hex) and `proposal_file_sha256` (the file-content SHA-256, 64 hex).
8. **Non-collapse verification wording wrong.** v1's MANIFEST non-collapse_check_command used `diff` between two ID lists and expected "empty diff," which is correct for set comparison but ambiguous about whether `BIB-4D-4` and `C12-7` overlap by name (factual discipline) — they do by name, intentionally, but the ID *sets* are disjoint. v2 uses an explicit set-intersection check with assertion `intersection == empty_set`.

## v2 protocol revision (current)

**Path:** `experiments/2026-09-11-insa-id-e1/` (top level, NOT in audit/)
**See:** `MANIFEST.json` SHA-256 in top-level `MANIFEST.sha256.txt` after the v2 freeze.

This audit directory is preserved but **not** part of the v2 binding. The v2 binding references only the top-level artifacts.