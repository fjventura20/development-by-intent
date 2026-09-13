# COA-E2 v0.3 — Freeze Manifest Draft

**Status:** Draft template only; not a freeze and not executable.
**Repository root:** `<declared at freeze time>`
**Self-reference:** this file is excluded from its own `files` list.
**External manifest hash:** recorded in the future freeze record after all entries are sealed.

At freeze time, populate the following list with the SHA-256 of each exact file. Runtime nonces are bound separately in `runtime-manifest-DRAFT.json`; final nonce generation is not authorized by this draft.

## Controlling files to hash

```text
v0.3/PROTOCOL-DRAFT-v0.3.md
v0.3/four-proposition-evidence-model-DRAFT.md
v0.3/session-binding-evidence-spec-DRAFT.md
v0.3/audit-specification-DRAFT.md
v0.3/qualification-procedure-DRAFT.md
v0.3/packets/initialization-templates-DRAFT.md
v0.3/packets/coa-governed-init-DRAFT.md
v0.3/packets/control-init-DRAFT.md
v0.3/charters/coa-governed-DRAFT.md
v0.3/charters/control-DRAFT.md
v0.3/tasks/U1.md
v0.3/tasks/U2.md
v0.3/tasks/U3.md
v0.3/tasks/U4.md
v0.3/tasks/U5.md
v0.3/tasks/RUBRIC-DRAFT.md
v0.3/runner/README.md
v0.3/runner/RUNNER-CONTRACT-DRAFT.md
v0.3/runner/run_pilot.py
v0.3/runner/audit_after_turn.py
v0.3/runner/classify_response.py
v0.3/runner/verify_manifest.py
v0.3/runner/generate_nonces.py
v0.3/runner/aggregate_pilot.py
v0.3/runner/runtime-manifest-DRAFT.json
```

The final manifest must contain `path` and `sha256` for every file above, resolved beneath the declared repository root. It must not include itself. The manifest's own SHA-256 is recorded externally in the freeze record. The final runtime manifest must additionally contain six unique keyed nonces and the sealed hashes.
