# Gate Adjudication — Original 76 passed / 5 failed

formal_run_id         : 20260918T183130Z-acl-lifecycle-poc-v0.1 (original claimed PASS preserved at d225399; subsequently invalidated by independent closeout 8d9f7b3; controlling disposition INCONCLUSIVE_EVIDENCE_INVALID)
candidate_run         : PoC development suite at HEAD = 6ffd97b7c3fac825ac535e203f0c04177a20d08d
tester                : python3 -m pytest -q
pytest exit code      : 1

COUNTS
------
passed : 76
failed : 5
skipped: 0
xfailed: 0

FAILED TESTS
------------
1. tests/test_attack_regressions.py::test_f4_mismatched_issuer_id_rejected
2. tests/test_attack_regressions.py::test_f4_mismatched_issuer_key_id_rejected
3. tests/test_attack_regressions.py::test_f4_tampered_artifact_digest_rejected
4. tests/test_attack_regressions.py::test_h1_exact_correct_digest_fake_profile_replacement_attack_rejected
5. tests/test_authority_boundary.py::test_ab04_subject_and_observer_reads_are_defensive_copies

GATE DECISION
-------------
Status : CHANGES REQUIRED
Disposition is governed by the frozen protocol: any test failure
classifies the run as CONFORMANCE_LIFECYCLE_POC_FAIL absent authorized
relaxation. No relaxation is in scope; the run is not a PASS.

AUTHORIZATION FOR REPAIRS
--------------------------
Per successor operator directive, the following three correction groups
are authorized, bounded, and limited to the source files named below.
No redesign, no scope widening, no frozen-artifact modification, no
external models, no formal run, no merge to main.

  Group 1: caller-fixture verification in
           conformance/authorization.py
           AuthorizationService.issue_capability() — verify the
           complete caller-supplied qualification and admission
           fixtures before resolving authoritative records. Closes
           mismatched issuer ID, mismatched issuer-key ID, and
           tampered artifact-digest acceptance.

  Group 2: fresh-evidence semantics in
           tests/test_attack_regressions.py
           test_h1_exact_correct_digest_fake_profile_replacement_attack_rejected
           — explicitly prove the invalidation evidence is rejected as
           not fresh; submit new observer-authoritative v2 evidence
           with a distinct artifact_id; evaluate fresh evidence;
           prove profile-v1 remains active and attacker-created
           profile does not restore conformance.

  Group 3: observer-history assumption in
           tests/test_authority_boundary.py
           test_ab04_subject_and_observer_reads_are_defensive_copies
           — record history length before submitting rt-ev-v1-ab04,
           require growth of exactly one, mutate the newly returned
           record (not index zero), verify fresh authoritative read.

EVIDENCE AT THIS STEP
---------------------
candidate_HEAD : 6ffd97b7c3fac825ac535e203f0c04177a20d08d
prior_PASS_run : 20260918T183130Z-acl-lifecycle-poc-v0.1 (evidence dir
                 preserved byte-for-byte under
                 architecture/agent-trust-envelope/agent-conformance-local-lifecycle-poc-v0.1/evidence/formal-20260918T183130Z/)
frozen_artifacts: all 8 verified byte-identical
no_formal_run   : CONFIRMED
no_merge        : CONFIRMED
no_push_yet     : CONFIRMED (correction candidate not pushed at this step)
