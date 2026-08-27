# Artifact Record — Transcript-Only Claude 004

## Frozen source commit (per v0.1.1)

`c369215024c9f8a849daf11bd4b872d7ee566a7a` — "Add Amazing Birthday canonical worked example"

Reachable from current HEAD via `git rev-parse c369215024c9f8a849daf11bd4b872d7ee566a7a` → returns the commit hash (current HEAD is `99dcb69b40837ab151910ca9415cee513e6deb0c`, which is a descendant of c3692150). The frozen source commit is an ancestor of HEAD with no rewriting since.

## Phase A — Frozen target artifacts (the only inputs the target saw)

| Path | Frozen-source git blob SHA-1 | Staged copy SHA-256 |
|------|----------------------------|---------------------|
| `examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` (from `git rev-parse c3692150:path`) | `9e0b89f91e26b1449864dc6c5de5b42c5752de91232b75f7be915cd0d10f4ed3` (from `sha256sum /tmp/portability-004/target/transcript.txt`) |

Cross-check `git hash-object <staged-file>`:
```text
$ git hash-object /tmp/portability-004/target/transcript.txt
bab34913805c625b9bae46b54169b6decc447cd6
```
Git blob SHA of the staged copy matches the frozen-source git blob SHA exactly — **byte-for-byte reproduction.**

The transcript file was staged at `/tmp/portability-004/target/transcript.txt` (27384 bytes) via:
```text
git show c369215024c9f8a849daf11bd4b872d7ee566a7a:examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt > /tmp/portability-004/target/transcript.txt
```

It was then **inlined verbatim into the target's `--append-system-prompt-file`** argument for turn 1 only. The system prompt combines a 501-byte prelude (instructions to "Reconstruct the application purely from this transcript alone...") with the transcript content verbatim, terminated with an `--- END TRANSCRIPT ---` marker. Target had no need to read any file from disk.

**The system prompt SHA-256 was `d71958298bdb0541f5de03c1e3d9dde5b9cd4806a44c8d36b8ec981cd5cf5de4` (27909 bytes total).** This is the exact bytes the target saw.

## Withheld until freeze (per v0.1.1)

| Path | v0.1.1 expected SHA-256 (canonical content) |
|------|--------------------------------------------|
| `examples/amazing-birthday/06-validation.md` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` |
| `examples/amazing-birthday/tests/behavioral-tests.md` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` |

Neither file was supplied to the target before or during the run. Operator retained exclusive access for post-freeze scoring.

## Operator-only capture artifacts

- `/tmp/portability-004/operator/reconstruction-raw.json` (1993 bytes; clean JSON envelope)
- `/tmp/portability-004/operator/test-1-raw.json` (7616 bytes; clean JSON envelope)
- `/tmp/portability-004/operator/test-2-raw.json` (8192 bytes; **truncated** mid-envelope, partial JSON)
- `/tmp/portability-004/operator/test-3-raw.json` (8192 bytes; **truncated** mid-envelope, partial JSON)

All four belong to fresh target session `eec5da0c-ede0-4777-9bd6-29c367fd24e1`. Captures #1 and #2 are clean; captures #3 and #4 are truncated in the trailing envelope metadata; the assistant-text content (`"result"` JSON string) is fully present up through the closing prose in all four captures.

| Capture | sha256 |
|---------|--------|
| reconstruction-raw.json | `5373a43e3e58c536fd3d888462c21dc5985d3fa8f620c5dcf8f6f7344de35367` |
| test-1-raw.json | `58ce1cef023f99a16295c1c24003ec706ed6118f2d5288250a132d84b198db7f` |
| test-2-raw.json | `c8340c77c9bafb9a535c4eb672d22ad861fa013a0d8252076983562413d2c893` |
| test-3-raw.json | `8dfca78f3681b5228c7b15ff934e51783461c335aeeb509f4cacb0578c1ba5ff` |

Extracted-readable outputs preserved separately as `*-output.md` files.

## Cross-reference

- Source transfer: `20260826T204100Z-behavioral-portability-transcript-only-claude-004`.
- v0.1.1 SHA-256 amendment: see experiment `README.md` § "Protocol amendment: v0.1.1, 2026-08-27 — SHA-256 correction."
- v0.1.1 preflight record: `results/preflight-PASS-v0.1.1-2026-08-27.md`.
- v0.1 BLOCKED record: `results/preflight-BLOCKED-2026-08-27.md`.
