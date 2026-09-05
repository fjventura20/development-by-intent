# DBI-BIB-001 — Clean Rerun Plan (DBI-BIB-001-RERUN-001)

**Issued:** 2026-09-05T09:44:00Z
**Issued by:** Hermes (operator)
**Status:** PLAN — awaiting Frank-as-PI authorization. **Not executed.**

**Issuing transfer:** `20260905T094400Z-dbi-bib-001-incomplete-adjudication-001`
**Supersedes (planned):** the abandoned portion of DBI-BIB-001 v0.1 execution
where R6 failed Claude-account quota mid-run.

---

## 1. Why this plan

The 2026-09-04T23:57Z execution reached 50/60 valid captures before Claude OAuth
session limit (HTTP 429) hit R6. The same Claude account was then unable to
power Evaluator B (Claude Opus 4.7) under the §12 blinding protocol. Both
failures shared an account-level quota surface.

Per Frank's recommendation: do **not** simply wait for the quota to reset and
re-execute the same script. The 50 already-captured R1–R5 outputs would
re-enter the same evaluator-session counter, and the operator-side time spent
on those captures is not recoverable. A clean staged run with quota-aware
pacing is preferred.

## 2. Design choice — what stays frozen, what changes

### 2.1 Stays frozen (no protocol amendment)

- **Protocol:** `b9b6c86c` (`experiments/behavioral-identity-baseline-v0.1/PROTOCOL.md`)
- **Execution package:** `ebbb4319` (`.../execution-package-v0.1/`)
  - EVALUATOR-RUBRIC.md
  - MANIFEST.schema.json
  - OPERATOR-INSTRUCTIONS.md
  - TEST-CORPUS.md (T1–T5)
  - SOURCE-PACKAGE.md
  - BLINDING-PROCEDURE.md
- **Source package:** `c3692150` (amazing-birthday frozen intent)
- **Runtime target:** claude-sonnet-4-6, claude CLI ≥ 2.1.x, `--allowedTools ''`
- **Sample size:** 6 reconstructions × 5 tests × 2 evaluation blocks = 60 outputs
- **Blinding:** UUID4 blind-map, Fisher-Yates shuffle per evaluator with frozen seed
- **Score rubric:** identical 4-dimension vector (contract_compliance,
  selection_behavior, narrative_behavior, functional_completeness) +
  classification (SAME / SAME_WITH_VARIANCE / DIFFERENT)

### 2.2 Changes vs. the prior run

| Element | Prior run | Rerun | Why |
|---|---|---|---|
| Reconstructions | R1–R6 same session family (single Claude account, single CLI install) | **R1–R6 entirely new sessions on a fresh quota window** | Avoid the half-failed state from R1–R5 + R6-quota |
| Quota pacing | Single contiguous run until failure | **Staged across two quota windows:** R1–R4 in window A, R5–R6 in window B (after observed reset) | Avoid hitting account-level quota mid-execution |
| Blinding timing | Built at end (post-generation) | **Built at end (unchanged)** | Per §12 the blind map must be sealed before any evaluator sees content; no change needed |
| Evaluation | Started immediately after generation | **Deferred until all 60 outputs exist** | Frank's recommendation: "no blinding or evaluation until all 60 outputs exist" — eliminates evaluator-side drift from a half-complete blind-map |
| Evaluator pairing | Codex gpt-5.6-sol + Claude Opus 4.7 | **Same pairing** (or substitute per §12 if Opus remains blocked on a fresh window — see §4.2) | Protocol-mandated role separation |
| R1–R5 captures from prior run | n/a | **Preserved on disk under `runs/R1/..R5/`, NOT re-used as part of the new 60 outputs** | Old captures were captured under a partial-failure run; freezing them as audit evidence but excluding them from the new analysis keeps the rerun clean. They remain queryable for cross-validation but are not in the new candidate set. |

## 3. Execution sequence

### Phase 0 — Pre-flight (no model calls)

Operator-side, before any new reconstruction:

1. Verify Claude CLI is at the same runtime version (or note delta) and confirm
   `--allowedTools ''` posture is intact.
2. Re-run source SHA-256 verification against the frozen package
   `c3692150` (amazing-birthday).
3. Verify the 60 R1–R6 output slots are empty.
4. Confirm quota reset window by polling the Claude CLI smoke call (per
   §3 preflight). **This is the only model call authorized in preflight.**
5. If quota has not reset by the planned Phase-1 start, defer start.

### Phase 1 — Generation window A (R1–R4)

Target: produce **20 valid test outputs** (R1–R4 × 5 tests × 2 blocks).

- One fresh `--session-id` per reconstruction.
- Capture via shell redirect (`claude ... > FILE 2>stderr`) per v0.2 capture
  discipline; reject SIGPIPE-truncated files via the per-turn gate
  (jq empty && size>1KB && size%8192!=0 && sha256sum).
- Run reconstruction turn + Block A + Block B with no intermediate turns.
- Mark each output `valid_capture=true` only after the gate passes.
- On any infrastructure failure in R1–R4, stop and surface — do NOT proceed
  to R5 within the same window.
- On reaching 20 valid outputs, end window A. Operator pause point.

### Phase 2 — Quota reset wait

- Poll Claude CLI smoke call hourly until the session-limit indicator clears.
- Document the observed reset time as `deviations/DEV-XXX-QUOTA-RESET.md`.

### Phase 3 — Generation window B (R5–R6)

Target: produce **20 valid test outputs** (R5–R6 × 5 tests × 2 blocks).

- Identical procedure to Phase 1.
- New `--session-id` per reconstruction.
- Per-turn gate identical.

### Phase 4 — Generation completion gate

- Total valid outputs: 40/60 (R1–R4 × 5 × 2) + 20/60 (R5–R6 × 5 × 2) = **40? — WAIT.**

**Correction to operator counting above.** Each reconstruction produces 5 tests
× 2 blocks = 10 captures. R1–R6 = 6 × 10 = **60 valid test outputs total**,
matching the original design.

Phase 1 + Phase 3 produce all 60 outputs.

### Phase 5 — Blinding

- Build fresh UUID4 blind-map of 60 entries
  (R1–R6 × {A,B} × T1–T5 → blind_id, prompt_sha256, raw_output_path).
- Fisher-Yates shuffle Evaluator A order (seed `0xA1A1A1A1` unchanged).
- Fisher-Yates shuffle Evaluator B order (seed `0xB2B2B2B2` unchanged).
- Blind-map + orderings are sealed; evaluators receive input packets with
  no reconstruction/block/test metadata.

### Phase 6 — Evaluation (both evaluators)

- Evaluator A (Codex gpt-5.6-sol): score all 60 candidates in one or two
  fresh sessions. Lock score SHA. Per-turn capture gate.
- Evaluator B (Claude Opus 4.7 if available; else §4.2 fallback):
  same procedure.
- DEFER any cross-evaluator agreement analysis until both score sets are
  locked.

### Phase 7 — Variance and identity analysis

- Within-reconstruction Manhattan distances (n=30 across R1–R6 × T1–T5 × 2 blocks).
- Between-reconstruction Manhattan distances (n=300 across 6 × 5 × 2 × C(6,2)=15).
- Cross-evaluator agreement: identity-preservation raw %, Cohen's kappa,
  per-dimension MAE.
- Per §13 central calibration test outcome (A/B/C).
- Per §14 prospective threshold derivation.

### Phase 8 — Outbound package

- Standard DBI outbound: manifest + result.json + execution-report.md +
  execution-manifest.json + evidence-inventory.json.
- Disposition: PASS / FAIL / INCONCLUSIVE based on §13 + §14 outcome, not
  pre-set.
- Validator pre-flight, push to origin mailbox/main.

## 4. Open questions requiring Frank-as-PI decision

### 4.1 Confirm the staged-run design

Specifically: is R1–R4 first window / R5–R6 second window the right quota
pacing? The alternative is a single longer wait + one window for all 6
reconstructions (cleaner accounting, longer calendar time). Frank's
recommendation was the two-window split; this plan adopts that.

### 4.2 Evaluator B fallback

If Claude Opus 4.7 remains blocked even on a fresh quota window, the §12
two-evaluator design requires a substitute. Options:

- **(a)** Wait longer for Opus to become available — preserves protocol.
- **(b)** Substitute Claude Sonnet 4.6 — keeps Claude family but changes
  evaluator model. Requires a §12 protocol amendment because Sonnet is the
  *reconstruction* model.
- **(c)** Substitute a third-party evaluator with comparable role separation
  (e.g., Gemini CLI if a ChatGPT-OAuth path is available; or a human
  evaluator with §15 role constraints). Requires §12 amendment.
- **(d)** Run with a single evaluator and pre-register Evaluator B at a
  later date as a follow-up experiment — does NOT close §13.

Frank should pick (a)–(d). Default if no signal by execution-ready time: (a)
with a 24-hour max wait, then escalate.

### 4.3 Disposition of preserved R1–R5 captures from the prior run

This plan assumes **PRESERVE-but-do-not-re-use**. Alternatives:

- **(i)** Delete R1–R5 captures — clean break, but loses audit evidence.
- **(ii)** Treat prior R1–R5 as a separate pre-pilot and report both
  experiments in the final analysis — preserves evidence, doubles paperwork.
- **(iii)** Use prior R1–R5 as the new R1–R5 and only generate R6 fresh —
  fastest path to 60 outputs, but mixes runs from two Claude-account states.

Default: **(ii)** is the cleanest; (iii) is fastest but most fragile.

### 4.4 Authorization form

This plan expects an explicit GO transfer (analogous to
`20260904T225700Z-dbi-bib-001-execution-go-001`) before Phase 1 starts.
The GO must include:

- Execution-package version reference (v0.1 unchanged)
- Phase-window timing (start of Phase 1, expected Phase-3 window)
- §4.2 Evaluator B fallback decision
- §4.3 Prior-capture disposition decision

## 5. What this plan explicitly does NOT do

- It does **not** modify the frozen protocol or execution package.
- It does **not** amend the blind-map seed values.
- It does **not** expand beyond 6 reconstructions (would violate §14 unless
  a new authorization explicitly carves it out).
- It does **not** authorize any model call (Phase 0 preflight smoke call
  excluded; that is an §3-mandated preflight action).

## 6. Estimated cost and time

- Phase 1 (R1–R4): 4 reconstructions × ~13 turns × ~$0.02–0.04/turn ≈
  **$1.04–$1.60** + ~30 min wall time
- Phase 2 (quota wait): variable; expected 1–6 hours
- Phase 3 (R5–R6): 2 reconstructions × ~13 turns × ~$0.02–0.04/turn ≈
  **$0.52–$0.80** + ~15 min wall time
- Phase 5–8: ~1 hour operator time + ~$0.50 evaluator cost
- **Total estimate: $2.06–$2.90 + 3–8 hours wall time, of which ~1 hour is
  active operator time**

---

## 7. Linked artifacts (this correction packet)

- `deviations/STOP-CONDITION-CORRECTION.md` (corrected §14 analysis)
- `analysis/evaluator-A-between-100.csv` (the missing 100-distance table)
- `analysis/evaluator-A-between-100.json` (structured exploratory analysis)
- `deviations/stop-condition-correction.json` (machine-readable correction record)

**This plan is staged but not started.** Awaiting Frank-as-PI authorization.