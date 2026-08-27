# Artifact Record — Transcript-Only Claude Replication 006

## Frozen source commit (inherited from 004 v0.1.1 / 005 v0.2)

`c369215024c9f8a849daf11bd4b872d7ee566a7a`

## Phase A — Frozen target artifacts (the only inputs the target saw)

| Path | Frozen-source git blob SHA-1 | Staged copy sha256 (content) |
|------|----------------------------|------------------------------|
| `examples/amazing-birthday/02-development-transcript/amazing_birthday_transcript.txt` | `bab34913805c625b9bae46b54169b6decc447cd6` | `9e0b89f91e26b1449864dc6c5de5b42c5752de91232b75f7be915cd0d10f4ed3` (same content; 27384 B) |

`git hash-object /tmp/portability-006/target/transcript.txt` → `bab34913805c625b9bae46b54169b6decc447cd6` ✅

System prompt (prelude + transcript content + closing marker) inlined via `--append-system-prompt-file`:

- **Total system-prompt bytes:** 28,142
- **System-prompt SHA-256:** `c34fe0ec848fdf27824f0b21925a542946b072b366e0c9da8bd68cdbe8b2c63e`
- **Prelude length (the operator's instruction region):** 704 characters (different from 005's 501-character prelude)
- **Marker transformation:** `--- BEGIN TRANSCRIPT ---` / `--- END TRANSCRIPT ---` (005) → `--- BEGIN CONVERSATION ---` / `--- END CONVERSATION ---` (006)

The full prelude text is encoded in `MANIFEST.json` § `operator_prelude_freeze_discipline_v02.prelude_text` and verifiable by extracting the prelude-region bytes of the system prompt:

```text
prelude_end = byte_offset_of("--- BEGIN CONVERSATION ---")
prelude = system_prompt[0:prelude_end]
```

A preflight overlap check on this prelude-region found **no prohibited-phrase hits** across the 20-pattern vocabulary in `MANIFEST.json.operator_prelude_freeze_discipline_v02.prohibited_phrases_in_prelude`. The prelude is the load-bearing change that allows v0.2 freeze discipline to pass.

## Withheld until freeze (inherited from 004 v0.1.1 / 005 v0.2)

| Path | v0.2 expected SHA-256 (content) |
|------|--------------------------------|
| `examples/amazing-birthday/06-validation.md` | `cb3299e4bf4ab110b8b88dd67127586f16f5b53a21a6c60e4dd88cba23fd223d` |
| `examples/amazing-birthday/tests/behavioral-tests.md` | `35d87d8725f30a620e2a97ff14a51cc38a31453a18aa6a8dea889ed6a90a26a1` |

Neither file was supplied to the target before or during the run. The target had the transcript only (Phase A), the v0.2 freeze-discipline prelude, and `--allowedTools ''`.

## Operator-only capture artifacts

| Capture | Bytes | Status | sha256 |
|---------|-------|--------|--------|
| `reconstruction-raw.json` | 1,807 | ✅ clean | `299ca9b91025b71cd9abed95d128852313293c1b11c46b972ea2935cd8998345` |
| `test-1-raw.json` | 7,567 | ✅ clean | `43b47b247fb04bfbcbada4b9c80a3424120afc590d99233b3695238a6f4b46df` |
| `test-2-raw.json` | 8,217 | ✅ clean | `01d179906e88130d045c42e02b1424b0da5eaf43a17664253ea045ed98dae4d0` |
| `test-3-raw.json` | 10,163 | ✅ clean | `b32e94718567bea6dc8cebac4a7bdc19093e41736fb7d30c09382a94944899c2` |

All four belong to fresh target session `19921118-022e-41a6-8323-910103401170`. All four pass the v0.2 gate: `jq empty && size>1KB && size%8192!=0 && sha256sum`.

## Cross-reference

- 005 results: `experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/` (v0.2 capture / v0.1 prelude; freeze-discipline breach; formal INDETERMINATE per ChatGPT independent review).
- 004 results: `experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/` (v0.1 capture broken; operator HUDETERMINATE).
- 006 protocol: `../README.md` + `../MANIFEST.json` + `../protocol/freeze-discipline-prelude-v0.2.md`.
- 006 v0.2 protocol doc: `BEHAVIORAL-PORTABILITY.md` v0.2 (origin commit `6da9b60`).
