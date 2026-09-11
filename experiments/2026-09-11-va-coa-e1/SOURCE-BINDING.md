# VA-COA-E1 Source Binding

## Authoritative source required before freeze-final

The governing Condition of Agency baseline is recorded in prior project evidence as:

```text
aegis-exchange/constitution/condition-of-agency.md
```

Frank previously approved this as the frozen **CoA v1.0 Baseline** after earlier draft iterations. The experiment must bind to the actual authoritative file bytes, not reconstruct the baseline from memory, excerpts, or an earlier draft.

## Required preflight evidence

Before FROZEN-FINAL, obtain and preserve:

1. absolute or repository-relative authoritative source path;
2. byte size;
3. SHA-256 of the source file;
4. exact byte copy saved as `inputs/condition-of-agency-v1.0-baseline.md`;
5. SHA-256 of the copied file, proving byte identity;
6. source provenance: repository/commit if tracked, otherwise filesystem evidence and timestamp;
7. confirmation that the file is the baseline Frank froze, rather than the earlier v1.0/v1.1 drafts.

## Freeze-final rule

Freeze-final is allowed only if source SHA-256 equals copied-input SHA-256.

If the authoritative source cannot be found or its baseline identity is ambiguous, stop with:

```text
BLOCKED: COA_SOURCE_BINDING_UNRESOLVED
```

Do not substitute any uploaded excerpt or remembered text.

## Execution boundary

Source discovery and hashing are preflight only. They do not authorize model dispatch, qualification cases, gate execution, or experiment scoring.
