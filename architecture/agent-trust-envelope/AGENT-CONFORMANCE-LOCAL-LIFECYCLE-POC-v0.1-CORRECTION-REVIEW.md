# Correction Review — Three Authorized Correction Groups

candidate           : 76e0816ca729bbef3fde197970c1958352023c7f
parent              : 6ffd97b7c3fac825ac535e203f0c04177a20d08d
reviewer            : Hermes (independent, post-authorization)
scope_authorized    : three correction groups only
files_changed_count : 3
insertions          : +62
deletions           : -5

GROUP 1 — caller-fixture verification
-------------------------------------
File        : conformance/authorization.py
Insertion   : +22 lines after the authoritative-subject resolution,
              before the authoritative-fixture resolve.
              AuthorizationService.issue_capability() now invokes
              verify_qualification() and verify_admission() on the
              caller-supplied qualification and admission fixtures
              against the authoritative subject's (subject_id, role_id,
              trust_domain) binding.
Result      : F4 regressions (mismatched issuer ID, mismatched
              issuer-key ID, tampered artifact-digest) all reach the
              verify path on the caller-supplied object. The four-gate
              check (signature, issuer-id, issuer-key-id, artifact-
              digest) closes the three acceptance paths.
Continue    : independent authoritative fixture resolution and
              verification are preserved unchanged after the new
              caller-fixture check. The stale-signed-ACTIVE-snapshot
              denial after authoritative revocation is preserved.

GROUP 2 — fresh-evidence semantics (H1)
---------------------------------------
File        : tests/test_attack_regressions.py
Insertion   : +34 lines, deletion of 2 lines in the body of
              test_h1_exact_correct_digest_fake_profile_replacement_attack_rejected.
              The test now:
              (a) retains registry replacement denial and unauthorized
                  activation denial checks (both still raise
                  PermissionError);
              (b) asserts profile-v1 remains active;
              (c) explicitly proves rt-ev-v2-h1 (used for
                  invalidation) is rejected as not fresh — wrapped in
                  pytest.raises(PermissionError);
              (d) submits new observer-authoritative v2 evidence
                  under a distinct artifact_id (rt-ev-v2-h1-fresh);
              (e) evaluates the fresh evidence;
              (f) asserts profile-v1 is still the active profile and
                  the fresh evidence evaluation yields
                  REATTESTATION_REQUIRED, so the attacker-created
                  profile does not restore conformance.

GROUP 3 — observer-history assumption (AB04)
---------------------------------------------
File        : tests/test_authority_boundary.py
Insertion   : +11 lines, deletion of 2 lines in
              test_ab04_subject_and_observer_reads_are_defensive_copies.
              The test now:
              (a) records `initial_history_len = len(history())` before
                  submitting rt-ev-v1-ab04;
              (b) requires the history to grow by exactly one
                  (history_after_submit has length
                  initial_history_len + 1);
              (c) mutates the newly returned record
                  (`history_copy[-1].measured_runtime_version`), not an
                  assumed index zero;
              (d) verifies a fresh authoritative read of rt-ev-v1-ab04
                  remains unchanged at "v1".

FROZEN ARTIFACT VERIFICATION
----------------------------
All 8 frozen blobs remain byte-identical to the frozen hashes
(verified by `git rev-parse HEAD:<path>` at candidate HEAD):
  - 4faea2a16261ca9416fe8bb4eceaaff80593eb59  DESIGN
  - d1da477dfaa8bb4682a01408596cd468a6e3fd64  DESIGN FREEZE
  - f8bc4464db197a58b6402e01d0378592ba7dc220  CONFORMANCE PROTOCOL
  - 62630ddc3bdbf114c7d07beffa2621737c623aaf  PROTOCOL FREEZE
  - 28b4b0a36e7ded946686c0eb45d4ee820a35c2bf  QA PROTOCOL
  - 0a4c42c30b0914bd0c0dc660c3aa8cc80ae5cb86  REVOCATION TRUST STATE
  - 154465106614f1448f9bbbca94ff7b5862bfd00a  ENFORCEMENT PLANE
  - 82450a5d049cc1d6f53a6cc2a4f952dcb442aa8c  AUDIT ACCOUNTABILITY

NO SCOPE VIOLATION
------------------
Only the three authorized files were modified:
  - conformance/authorization.py
  - tests/test_attack_regressions.py
  - tests/test_authority_boundary.py

No additional source/test files were modified.
No frozen design/protocol artifacts were modified.
No runner file was modified at this step.
No formal run was executed.
No merge was performed.

TEST RESULT AT CANDIDATE
------------------------
pytest -q from the PoC root:
    ........................................................................
    81 passed in 0.4s
    0 failed / 0 skipped / 0 xfailed

DETACHED CLEAN WORKTREE GATE
----------------------------
A new detached worktree was created at ~/devProjectsU/dbi-correction-gate
pinned to candidate HEAD 76e0816ca729bbef3fde197970c1958352023c7f.
git status --short : empty
HEAD               : 76e0816ca729bbef3fde197970c1958352023c7f
all 8 frozen blobs : OK
pytest -q          : 81 passed / 0 failed / 0 skipped / 0 xfailed

This gate evidence is the subject of a separate artifact:
AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1-CORRECTION-DETACHED-GATE.md
