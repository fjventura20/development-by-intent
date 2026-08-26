# Artifact Record — Behavioral Portability Replication 002

## Phase A — Frozen target artifacts (the only inputs the target saw)

| Path | SHA-256 | Source |
|------|---------|--------|
| `03-behavioral-baseline.md` | `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159` | Frozen source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a` |
| `RECONSTRUCTION-PROMPT.md` | `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce` | Frozen source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a` |

Both were verified byte-for-byte before target launch, staged at `/tmp/portability-rep2/target/`, and inlined into the target system prompt. The inlined system prompt SHA-256 was `064c33b8ab9e70e84b8c37571b3cbd9f0c782c3e944042eec4fd7ff8815b1dab`.

## Withheld until freeze

The test set, rubric, preregistration, transcript, and prior provider results were not target inputs before freeze. Hermes retained operator-only access for post-freeze scoring.

## Operator-only capture artifacts

- `/tmp/portability-rep2/operator/reconstruction-raw.json`
- `/tmp/portability-rep2/operator/test-1-raw.json`
- `/tmp/portability-rep2/operator/test-2-raw.json`
- `/tmp/portability-rep2/operator/test-3-raw.json`

All belong to fresh target session `b1f41015-a416-44cc-b5eb-35abc83274de` and were captured atomically on their first calls.

## Source transfer

Inbound request: `20260826T002800Z-behavioral-portability-claude-replication-002` on `mailbox/main`.  
Hermes result: `20260826T013000Z-behavioral-portability-claude-replication-002-result-001`.

A later duplicate inbound was withdrawn before operation and is not part of this experiment.
