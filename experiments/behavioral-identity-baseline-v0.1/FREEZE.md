# Behavioral Identity Baseline Experiment v0.1 — Freeze Record

**Freeze ID:** DBI-BIB-001-FREEZE-001  
**Protocol:** DbI Behavioral Identity Baseline Experiment v0.1  
**Protocol ID:** DBI-BIB-001  
**Freeze date:** 2026-09-04  
**Status:** FROZEN  
**Execution authorized:** NO

## Authoritative protocol

- Repository: `fjventura20/development-by-intent`
- Path: `experiments/behavioral-identity-baseline-v0.1/PROTOCOL.md`
- Protocol commit: `b9b6c86c017903cca061b4c2f7b798c82870f9c5`
- Git content hash (blob SHA): `1d06f02a9d331df279ee4417e23b4d52330b63f9`

The protocol at the commit above is the frozen Baseline Experiment v0.1 protocol. Later edits on any branch do not alter this freeze. Any change to the protocol requires a new protocol version and a new freeze record.

## Execution gate

This freeze does **not** authorize Hermes or any other operator to execute the experiment.

Execution may begin only after a separate **Execution Package v0.1** has been completed and frozen. That package must contain, at minimum:

1. the exact five-case test corpus and byte-for-byte trigger text;
2. the complete evaluator rubric, including score anchors and identity-classification rules;
3. the experiment manifest schema and required evidence fields;
4. operator instructions for isolation, reconstruction, execution, retries, deviation capture, randomization, evidence packaging, and stop conditions;
5. the exact Amazing Birthday generator-visible specification package, repository/ref, file list, and verification hashes;
6. evaluator assignment and blinding procedure;
7. explicit execution authorization.

## Next work item

**Build and freeze Execution Package v0.1.**

No Hermes implementation or execution request has been issued by this freeze record.
