# Clean Detached Worktree Gate — 81 / 81 / 0 / 0

candidate_HEAD    : 76e0816ca729bbef3fde197970c1958352023c7f
detached_worktree : /home/fjventura20/devProjectsU/dbi-correction-gate
preflight_command : git worktree add --detach <path> <candidate>

PRECONDITIONS
-------------
git status --short     : empty
HEAD                   : 76e0816ca729bbef3fde197970c1958352023c7f
frozen blob check      : all 8 OK (see below)

FROZEN BLOB VERIFICATION
------------------------
git rev-parse HEAD:<path> vs expected:

  [OK] AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-DESIGN.md
       4faea2a16261ca9416fe8bb4eceaaff80593eb59
  [OK] AGENT-CONFORMANCE-LOCAL-LIFECYCLE-POC-v0.1.1-FREEZE.md
       d1da477dfaa8bb4682a01408596cd468a6e3fd64
  [OK] AGENT-CONFORMANCE-PROTOCOL-v0.1.2.md
       f8bc4464db197a58b6402e01d0378592ba7dc220
  [OK] AGENT-CONFORMANCE-PROTOCOL-v0.1.2-FREEZE.md
       62630ddc3bdbf114c7d07beffa2621737c623aaf
  [OK] AGENT-QUALIFICATION-AND-ADMISSION-PROTOCOL-v0.2.2.md
       28b4b0a36e7ded946686c0eb45d4ee820a35c2bf
  [OK] ATE-REVOCATION-TRUST-STATE-MODEL-v0.1.md
       0a4c42c30b0914bd0c0dc660c3aa8cc80ae5cb86
  [OK] ATE-ENFORCEMENT-PLANE-v0.1.md
       154465106614f1448f9bbbca94ff7b5862bfd00a
  [OK] ATE-AUDIT-ACCOUNTABILITY-MODEL-v0.1.md
       82450a5d049cc1d6f53a6cc2a4f952dcb442aa8c

PYTEST EXECUTION
----------------
cd <worktree>/architecture/agent-trust-envelope/agent-conformance-local-lifecycle-poc-v0.1
python3 -m pytest -v > /tmp/detached-gate-76e0816.txt 2>&1
exit code : 0
result    :
    ........................................................................
    81 passed in 0.38s
    0 failed / 0 skipped / 0 xfailed

EVIDENCE
--------
detailed test log    : /tmp/detached-gate-76e0816.txt
evidence SHA-256     : 3bc4fec1681c180ba66cca8bf4645a075f39748f2d53e42e29dfa02c7c580958
                      (sha256sum of /tmp/detached-gate-76e0816.txt captured at gate time)

POST-TEST CLEANLINESS
---------------------
git status --short post-test : empty (worktree remained clean)
HEAD post-test               : 76e0816ca729bbef3fde197970c1958352023c7f (unchanged)
no formal run                : CONFIRMED
no merge                     : CONFIRMED

DECISION
--------
Gate result is exact 81-pass clean. The detached gate PASSES. The
candidate is authorized to advance to the successor-runner baseline
update step.
