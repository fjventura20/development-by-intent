# Artifact Record — Hermes-Operated Claude Portability 001

## Phase A — target inputs before freeze

| Artifact | SHA-256 |
|---|---|
| `03-behavioral-baseline.md` | `4582d768b696bbce41729ff05475ff9a8edf86c7b55668aaa46a230690e66159` |
| `RECONSTRUCTION-PROMPT.md` | `7d6d08196a825058fe677f0cf9b0367c4f8135a0ce50b2445bef54928f4084ce` |

These were the only application artifacts exposed to the target before freeze. They were inlined into the target system prompt; all target tools were denied.

## Withheld until after freeze

- preregistration
- `06-validation.md`
- `behavioral-tests.md`
- operator instructions and prior outputs

## Frozen-source verification

Frozen source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`.

Hermes did not have this object locally at run start, but fetched it after execution. Post-run verification found both Phase A artifacts byte-identical to the frozen source. Hermes also checked that the development transcript's demonstrated dates—Dec 7, 1951; Feb 20, 1952; Aug 24, 1931—did not overlap the frozen test dates—Nov 9, 1989; Feb 29, 1960; Jun 23, 1956.

## Operator result provenance

Inbound experiment transfer: `20260825T213058Z-behavioral-portability-claude-001`

Hermes result transfer: `20260825T234500Z-behavioral-portability-claude-result-001`

Initial operator-result commit: `abd881162c5984b01e0921eb6b7f8f027fec2dab`

Post-run F1/F3/F4 resolution commit: `5f59b5a8738bc844f03203783b291ec1a2938fd9`

The Hermes SHA manifest is preserved separately as `hermes-manifest.json`.