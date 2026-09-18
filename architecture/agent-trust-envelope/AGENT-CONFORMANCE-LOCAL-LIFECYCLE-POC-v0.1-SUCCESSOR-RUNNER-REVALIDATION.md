# Successor Runner Revalidation — IMPLEMENTATION_BASELINE rebind

runner_file        : architecture/agent-trust-envelope/agent-conformance-local-lifecycle-poc-v0.1/formal-runner-v0.1.1/run_formal.py
prior_baseline     : 82dc8df570b5946fb291575a44e73755b6c3213a
new_baseline       : 76e0816ca729bbef3fde197970c1958352023c7f
scope_of_change    : single-string replacement at
                     IMPLEMENTATION_BASELINE = "<sha>"
lines_changed      : 1

VERIFIED BEHAVIOR PRESERVATION
------------------------------
The successor-runner substantive execution logic is unchanged.
Specifically, the runner still:

  [x] requires exactly 81 clean tests (the preflight gate asserts
      "81 passed" + "failed" not in stdout + "skipped" not in stdout
      + "xfailed" not in stdout);
  [x] defaults to dry-run mode (mode = "formal" iff args.formal);
  [x] requires both --formal AND ACL_FORMAL_RUN_AUTHORIZED=YES for
      formal execution;
  [x] checks the clean worktree (git status --short empty);
  [x] checks the implementation baseline (git diff --name-only
      IMPLEMENTATION_BASELINE -- <subtree> empty);
  [x] verifies all 8 frozen artifact hashes (FROZEN_BLOBS dict);
  [x] uses ONE live execution path: a single bootstrap-driven
      build_harness_with_controls -> attach_executor sequence driving
      a linear causal flow through R13 -> R14 -> capability issuance
      -> executor.execute for C0, C1, post-invalidation, C2, replay;
  [x] requires fresh post-denial evidence (rt-ev-v2-fresh must have
      a distinct artifact_id, later logical_ts, and later
      event_sequence than rt-ev-v2-initial);
  [x] requires C2 to succeed exactly once (after_c2 == before_c2 + 1
      and after_c2 == 2);
  [x] denies replay with zero effect (after_replay == before_replay == 2
      and replay.reason == "REPLAYED_NONCE");
  [x] verifies audit integrity (verify_chain) and causal order
      (verify_causal_order with EXPECTED_CAUSAL_ORDER);
  [x] creates the manifest only after evidence generation (the
      manifest loop at the end of main() walks evidence_dir and writes
      99_manifest.json after all prior 00..08_*.json files).

FROZEN ARTIFACTS STILL BYTE-IDENTICAL AT NEW BASELINE
-----------------------------------------------------
git rev-parse 76e0816ca729bbef3fde197970c1958352023c7f:<path>:
  all 8 OK (same table as the correction-detached-gate artifact).

NOT EXECUTED
------------
This artifact records the rebind decision only. The successor-runner
dry-run was NOT executed under this directive. The successor formal
run was NOT executed. No merge to main was performed.

NEXT STEP (out of scope here)
-----------------------------
Push the rebind commit to origin/feature/agent-conformance-local-lifecycle-poc-v0.1
and await operator authorization for the successor dry-run only.
