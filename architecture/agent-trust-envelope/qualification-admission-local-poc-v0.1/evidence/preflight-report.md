# PF1..PF14 Preflight Report

**Implementation commit:** `fd6756ac0e2860e2454d20a9ea81847f9cfc2667`
**Branch:** `feature/ate-qa-local-poc-v010-implementation`
**Pushed baseline:** `a7f88006da0ab3d8904c35e1afac7c95aa2d44a6`

**Total:** 14  **Passed:** 14  **Failed:** 0  **Skipped:** 0

| Item | Result | Name | Evidence |
|---|---|---|---|
| PF1 | PASS | frozen_architecture_blob | c881ba76f83392a242415fa4c37a1f61ae6dd92b reachable; v0.2.2 freeze markdown present |
| PF2 | PASS | poc_design_blob | git ls-tree 4f0eb8e55f621283474fe03af0f060f7866affb8 → 48cc34a67a68da573fd96fdbd597ffd85bb7ec90 |
| PF3 | PASS | os_identities_exist | ate-requester/ate-authority/ate-executor present |
| PF4 | PASS | orchestration_path | /home/fjventura20/devProjectsU/development-by-intent-ateqa/architecture/agent-trust-envelope/qualification-admission-loc |
| PF5 | PASS | trusted_code_not_requester_writable | /opt/ate-poc-v010 returncode=1 |
| PF6 | PASS | authority_keys_not_requester_readable | /var/lib/ate/poc/authority/authority_signing.key returncode=1 |
| PF7 | PASS | executor_audit_keys_not_requester_authority_readable | all checks passed |
| PF8 | PASS | enforcement_store_not_requester_authority_writable | all checks passed |
| PF9 | PASS | direct_bypass_probe | requester/authority bypass denied (exit=1/1/1); resource unchanged (baseline='PF9-baseline|0', after='PF9-baseline|0') |
| PF10 | PASS | canonicalization_self_test | test passed |
| PF11 | PASS | signing_domain_separation | test passed |
| PF12 | PASS | monotonic_control_epoch | test passed |
| PF13 | PASS | audit_chain_self_test | test passed |
| PF14 | PASS | sqlite_serialization_available | test passed |

**Result:** PREFLIGHT PASS