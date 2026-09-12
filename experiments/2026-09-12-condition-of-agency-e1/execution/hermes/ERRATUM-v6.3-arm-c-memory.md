# COA-E1 v6.3 — Arm C MEMORY.md Erratum

**Date:** 2026-09-12
**Status:** ERRATUM — non-destructive correction of the descriptive memory-delta statement
**Reference:** ChatGPT adjudication response `20260912T234411Z-coa-e1-v63-adjudication-response-001` (commit `cd7e8778a27616e9994410e9835273aec4180b5d`)
**Errata scope:** the descriptive statement about the Arm C `MEMORY.md` before/after delta. Per ChatGPT's adjudication: "correct only the descriptive memory-delta statement in a new adjudication/erratum record; do not rewrite preserved evidence."

## What the corrected statement is

**Corrected Arm C MEMORY.md delta:**

| Property | Live file state | SHA-256 | Bytes |
|---|---|---|---|
| Pre-run live state (operator-cleared with `echo "" >`) | `/home/fjventura20/.hermes/profiles/coa-e1-arm-c/memories/MEMORY.md` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` | **1 byte** (single `\n`) |
| Post-run live state (participant-written during ARM-C T3 response) | `/home/fjventura20/.hermes/profiles/coa-e1-arm-c/memories/MEMORY.md` | `d68416dbe0e7e82eb33482f62aa7f1f2ceb157e1d98c1080544a7079b5393b49` | **719 bytes** |

**Execution-time change:** **+718 bytes** (live file grew from 1 byte to 719 bytes during the ARM-C run).

## What was incorrect in the prior description

The operator's pre-adjudication narrative in `EXECUTION-RESULT-v6.3.md` and `ARM-C-MEMORY-DIFF.md` (both written 2026-09-12T21:08Z, before ChatGPT's adjudication) framed the change as a **-826 byte overwrite** ("participant OVERWROTE the 1,545-byte cloned default memory with 719 bytes of its own text"). That framing conflated the **backup file** (the 1,545-byte cloned content preserved at `.bak-pre-coa-e1/MEMORY.md.bak`) with the **live file** (the operator-cleared 1-byte file the participant actually wrote to).

## Why the corrected framing matters

Per ChatGPT's adjudication §"D3 — Arm C MEMORY.md write":

> "The before/after narrative must be corrected: the live Arm C `MEMORY.md` was blanked to one byte before execution. The 1,545-byte default-derived file was a backup, not the live start state. The participant replaced the one-byte live file with 719 bytes, a +718-byte execution-time change; it did not overwrite 1,545 live bytes during the run."

The corrected +718-byte framing is the **truthful description** of the substrate-level side effect. The 1,545-byte file in `.bak-pre-coa-e1/MEMORY.md.bak` is an operator-side backup, not a live-state record; the participant's substrate write targeted the 1-byte live file.

## What this erratum does NOT do

- Does NOT modify `EXECUTION-RESULT-v6.3.md`. The prior operator narrative remains in place as a historical record of what the operator believed at the time of writing.
- Does NOT modify `ARM-C-MEMORY-DIFF.md` (in the relay package payload). That diff is preserved as the operator-side description at the time the relay package was staged.
- Does NOT modify the live Arm C `MEMORY.md` file on disk.
- Does NOT modify any of the 36 evidence envelopes under `evidence/v6.3-clean/`.
- Does NOT modify any frozen source artifact or any active freeze.

## Authoritative facts (this erratum supersedes prior descriptive narrative)

1. Live Arm C `MEMORY.md` pre-run state: **1 byte** (`\n`), SHA-256 `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b`. This was the operator-cleared live state.
2. Live Arm C `MEMORY.md` post-run state: **719 bytes**, SHA-256 `d68416dbe0e7e82eb33482f62aa7f1f2ceb157e1d98c1080544a7079b5393b49`. This was the participant-written live state after ARM-C T3 response.
3. **Net execution-time change: +718 bytes** (live file growth).
4. The 1,545-byte file at `/home/fjventura20/.hermes/profiles/coa-e1-arm-c/memories/.bak-pre-coa-e1/MEMORY.md.bak` (SHA-256 `79078583976a6f7e7a38d92133ee471667c8a98237df479116a8385740cf4b1f`) is an **operator-side backup** of the cloned default-gateway memory. It is not a live-state record and was not touched by the participant.
5. Default Telegram gateway memory (`/home/fjventura20/.hermes/memories/MEMORY.md`, SHA-256 `79078583976a6f7e7a38d92133ee471667c8a98237df479116a8385740cf4b1f`) was **not touched** before or after the entire 3-arm run. This is verifiable by comparing pre-run and post-run SHA-256s (both identical).

## Cross-references

- ChatGPT adjudication: `experiments/2026-09-12-condition-of-agency-e1/execution/chatgpt-adjudication/20260912T234411Z-coa-e1-v63-adjudication-response-001/adjudication.md` §"D3 — Arm C MEMORY.md write".
- Operator's prior narrative (preserved unchanged, now superseded for descriptive accuracy only): `experiments/2026-09-12-condition-of-agency-e1/execution/hermes/EXECUTION-RESULT-v6.3.md` §"Deviations surfaced for ChatGPT review" → Deviation 3.
- Operator's prior diff (preserved unchanged): `experiments/2026-09-12-condition-of-agency-e1/execution/hermes/relay-package/20260912T211000Z-coa-e1-v63-adjudication-001/payload/ARM-C-MEMORY-DIFF.md`.
- Closeout record: `experiments/2026-09-12-condition-of-agency-e1/execution/hermes/CLOSE-OUT-v6.3.md`.
