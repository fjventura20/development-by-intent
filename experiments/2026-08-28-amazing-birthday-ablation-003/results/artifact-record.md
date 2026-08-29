# Artifact Record — BP-AB-ABLATION-003

## Frozen experiment package

- **Freeze commit:** `254d892d3b8150d5da419824b2307269fe4be8af`
- **Freeze branch:** `feat/ablation-003-protocol-freeze`
- **Freeze repo:** `https://github.com/fjventura20/development-by-intent`
- **Freeze path on disk:** `experiments/2026-08-28-amazing-birthday-ablation-003/protocol/`
  - `PROTOCOL.md` — the protocol text
  - `EXPERIMENT-MANIFEST.json` — the preregistered conditions + fresh-birthday test set pointer
  - `fresh-birthday-test-set.json` — the 5 fresh birthdates used as triggers
  - `FREEZE.sha256` — signed digest of the frozen files
  - `conditions/condition-a-thin.md` — Condition A treatment text
  - `conditions/condition-b-contract.md` — Condition B treatment text
  - `conditions/condition-c-inventory.json` — Condition C durability-package inventory
  - `conditions/common-prelude.md` — the common reconstruction prelude
  - `tools/ablation-capture.sh` — the capture wrapper (v0.2 shell-redirect discipline)
  - `preflight/...` — preflight artifacts (claude version, fresh-dates absence check, wrapper smoke test)

The freeze branch was NOT modified during this experiment.

## Evidence projection

The behavioral scoring required complete trigger stdout (the prior execution result only carried the first 400 characters per trigger). The operator shipped a new evidence-only package at:

- **Transfer ID:** `20260829T120000Z-ablation-003-behavioral-scoring-evidence-001`
- **Location on origin:** `HANDOFFS/exchange/hermes-to-chatgpt/pending/20260829T120000Z-ablation-003-behavioral-scoring-evidence-001/` on `mailbox/main` (commit `2dadbc1` + `1aa6d6a`)
- **Contents:**
  - 45 trigger stdout files in `trigger-stdout/<cond>/<sess>/attempt-NN-<sha7>.stdout.txt` (Option A — complete stdout)
  - 45 records in `blinded-packet/blinded-trigger-packets.jsonl` (Option B — compact blinded packet)
  - `blinded-packet/blinded-codes.json` — unblinding key (labeled `DO_NOT_OPEN_DURING_SCORING`)
  - `captures-index/raw-output-index.json` — verbatim copy of the prior transfer's index (SHA-256 `10b16fad...` byte-identical)
  - `captures-index/SHA256SUMS` — signed digest of the 45 trigger stdout files
  - `evidence-package.md`, `provenance.md`, `manifest.json`, `result.json`, `COMPLETE`

## Capture files on host filesystem

The 162 capture files (54 captures × 3 files each: stdout, stderr, exit) are at the absolute paths declared in `captures-index/raw-output-index.json`. They are NOT mirrored into this DBI repo (per the freeze-discipline gate: experiment results live outside the freeze branch to avoid contamination).

Host filesystem layout (relative to `~/devProjectsU/development-by-intent-experiments/ablation-003/runs/`):

```
2026-08-28A-TZ-ablation-003-A/captures/A/{a,b,c}/attempt-{00-05}-{sha7}.{stdout,stderr,exit}.txt
2026-08-28B-TZ-ablation-003-B/captures/B/{a,b,c}/attempt-{00-05}-{sha7}.{stdout,stderr,exit}.txt
2026-08-28C-TZ-ablation-003-C/captures/C/{a,b,c}/attempt-{00-05}-{sha7}.{stdout,stderr,exit}.txt
```

A-b session `attempts/_failed-attempt-audit-bad-session-id/` is preserved for audit (one §6.3 deviation, recovered).

## Execution result

The execution result (54/54 captures, COMPLETE) is at:

- **Transfer ID:** `20260829T105000Z-ablation-003-experiment-result-001`
- **Location on origin:** `HANDOFFS/exchange/hermes-to-chatgpt/pending/20260829T105000Z-ablation-003-experiment-result-001/` on `mailbox/main`
- **Required deliverables (all present):**
  - `result.json` — machine-readable result envelope
  - `execution-report.md` — full execution report
  - `analysis.md` — operator preliminary, descriptive only (no scoring per §6.5)
  - `deviations/deviations.md` — A-b §6.3 recovery narrative
  - `results/{A,B,C}/condition-{A,B,C}-result-block.json` — per-condition result blocks
  - `captures-index/raw-output-index.json` — 54 captures with absolute paths + sizes + SHA-256
  - `scorebook/blinded-scorebook.csv` — 45 trigger rows + 9 reconstructions
  - `prompts/condition-prompts.md` — exact reconstruction prompt + trigger prompts + per-condition system prompts

## Scoring result (ChatGPT independent)

- **Transfer ID:** `20260829T124500Z-ablation-003-chatgpt-behavioral-score-001`
- **Location on origin:** `HANDOFFS/exchange/chatgpt-to-hermes/completed/20260829T124500Z-ablation-003-chatgpt-behavioral-score-001/` on `mailbox/main` (moved to completed/ at commit `f7f989e`)
- **Required deliverables (all present, copied verbatim into `results/`):**
  - `result.json` → `results/score-independent-result.json`
  - `behavioral-scoring.md` → `results/score-independent.md`
  - `controller-disposition.md` → `results/controller-disposition.md`

## Acknowledgement outbound

- **Transfer ID:** `20260829T130000Z-ablation-003-behavioral-scoring-acknowledgement-001`
- **Location on origin:** `HANDOFFS/exchange/hermes-to-chatgpt/pending/20260829T130000Z-ablation-003-behavioral-scoring-acknowledgement-001/` on `mailbox/main` (commit `f7f989e`)
- **Status:** validator ACCEPT, COMPLETE marker present, schema-conformant
- **Source transfer ID:** `20260829T124500Z-ablation-003-chatgpt-behavioral-score-001` (kind=response, status=PASS)
