# Artifact Record — Transcript-Only Claude Replication 005

## Frozen source commit (per v0.2, inherited from 004 v0.1.1)

`c369215024c9f8a849daf11bd4b872d7ee566a7a` — "Add Amazing Birthday canonical worked example"

## Phase A — Frozen target artifacts (the only inputs the target saw)

| Path | Frozen-source git blob SHA-1 | Staged copy sha256 (content) |
|------|----------------------------|------------------------------|
| `examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` (via `git rev-parse c3692150:path`) | `9e0b89f91e26b1449864dc6c5de5b42c5752de91232b75f7be915cd0d10f4ed3` (via `sha256sum`) |

Cross-check via `git hash-object <staged-copy>`:

```text
$ git hash-object /tmp/portability-005/target/transcript.txt
bab34913805c625b9bae46b54169b6decc447cd6
```

Git blob SHA of the staged copy matches the frozen-source git blob SHA **byte-for-byte**. The transcript content is canonical; only the file format wrapping (raw bytes vs. git blob) differs in which SHA-1 algorithm is computed on top of them.

The transcript (27,384 bytes) was inlined verbatim into the target's `--append-system-prompt-file` for turn 1, combined with the 501-byte prelude plus a closing `--- END TRANSCRIPT ---` marker. **System prompt SHA-256: `d71958298bdb0541f5de03c1e3d9dde5b9cd4806a44c8d36b8ec981cd5cf5de4` (27,909 bytes total). This is the exact bytes the target saw for the reconstruction turn.** (Identical to 004 — same source, same prelude.)

## Withheld until freeze (per v0.2, inherited from 004 v0.1.1)

| Path | v0.2 expected SHA-256 (content) |
|------|--------------------------------|
| `examples/amazing-birthday/06-validation.md` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` |
| `examples/amazing-birthday/tests/behavioral-tests.md` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` |

Neither file was supplied to the target before or during the run. Operator retained exclusive access for post-freeze scoring.

## Operator-only capture artifacts

| Capture | Bytes | Status | sha256 |
|---------|-------|--------|--------|
| `reconstruction-raw.json` | 29,744 | ✅ clean | `caff4af6568f2ac68238983d7d0c4d4d54321809a7c4f0ed7bba44b85493d708` |
| `test-1-raw.json` | 7,486 | ✅ clean | `f40ac763bdaa2ef41c69db8d27f9cfdad2ee1b1c113c04e82281c7a33c910176` |
| `test-2-raw.json` | 8,615 | ✅ clean (vs 004 truncated at 8,192) | `21cff2a5637490e7dcccedc2838355315421290b709640e4d1a4104865db9d2b` |
| `test-3-raw.json` | 8,689 | ✅ clean (vs 004 truncated at 8,192) | `a481c50011aafe4d9dc4f1bc0554a1a488704ae004173dd05507eec666f02fe8` |

All four belong to fresh target session `28a3e235-5490-4799-8eb1-27a17b85cae3`. Every capture passes the v0.2 gate (`jq empty FILE && size>1KB && size%8192≠0`).

## Cross-reference

- Source transfer: `20260827T081500Z-behavioral-portability-transcript-only-claude-replication-005` (proposed; pending exchange pickup).
- 004 audit chain: `experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/` (preregistration + 15 result files).
- 004 v0.1.1 SHA-256 amendment: `experiments/.../004/README.md` § "Protocol amendment: v0.1.1".
- 005 protocol: `../README.md` + `../protocol/capture-discipline-v0.2.md`.
- 005 manifest: `../MANIFEST.json`.
