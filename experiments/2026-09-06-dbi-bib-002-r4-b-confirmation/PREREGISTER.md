# DBI-BIB-002 — R4/B Deviation Confirmation

**Experiment ID:** DBI-BIB-002
**Status:** PREREGISTERED — awaiting GO
**Author:** Frank Ventura (PI) — design
**Operator:** Hermes Agent
**Date preregistered:** 2026-09-06
**Authorization required:** YES (separate GO artifact before execution)

---

## 1. Why this experiment exists

DBI-BIB-001-RERUN-001 (2026-09-06) returned a formal disposition of **INCONCLUSIVE**.

Four of five frozen quantitative decision rules passed. The failing gate was G2 ("no systematic IDENTITY-BREAKING behavior"). The 5 IDENTITY-BREAKING classifications (made independently by both evaluators) were entirely concentrated in R4 Block B — the candidates known to have been captured under Claude OAuth session-limit (HTTP 429) infrastructure failure (DEV-002).

The 55 non-deviated candidates cleanly preserved behavioral identity by both evaluators (within Manhattan medians 0-1; between Manhattan medians 0-1; bounded p95 ≤ 4). The 5-deviation cluster is sharply localized.

The frozen protocol has no automated mechanism to convert a deviation-attributable G2 failure into a PASS. Two readings are both internally consistent:

- **Reading A (strict-literal):** the formal disposition is INCONCLUSIVE; do not proceed to DbI Evolution without adjudication.
- **Reading B (deviation-attributable):** the G2 failure is mechanistically fully explained by DEV-002; the 55-candidate envelope is well-defined; R4/B exclusion should be documented as protocol rule for the Evolution Experiment.

**The disagreement between A and B is empirically decidable.** This experiment decides it.

---

## 2. Research question (narrowly stated)

**Does the R4/B identity-breaking pattern recur when the affected generation path is executed cleanly, without the DEV-002 infrastructure failure, on independent fresh reconstruction sessions?**

Equivalently:
- If clean B-branch executions reproduce the systematic identity-breaking → the original R4/B cluster was NOT a DEV-002 artifact; the behavioral baseline is not sufficiently stable; DbI Evolution remains blocked.
- If clean B-branch executions behave like the existing 55-candidate envelope and the R4/B failure does not reproduce → the original R4/B cluster is deviation-associated; the Evolution protocol can proceed with an explicit infrastructure-contamination exclusion rule.

---

## 3. Why A is included (matched control)

A is **not** a redundant check that A passes. A is a per-reconstruction matched control. We are asking whether the previous *A-good / B-broken* pattern reproduces, not merely whether B succeeds.

The within-reconstruction Manhattan distance (A vs B, same R, same T) is the cleanest test statistic for this question. If a clean run produces a per-reconstruction A→B jump comparable to the R4/B contamination signature (Manhattan ≈ 13-16), the prior pattern reproduces; if it produces a distance comparable to the 55-candidate non-deviated subset (Manhattan ≤ 3), the prior pattern does not reproduce.

---

## 4. Design (frozen before execution)

### 4.1 Sample size

3 fresh independent reconstruction sessions. Each executes:
- Block A: T1, T2, T3, T4, T5
- Block B: T1, T2, T3, T4, T5

Total: 3 × 10 = 30 candidate outputs.

### 4.2 Why 3, not 6

The full BIB-001 corpus already supplies the baseline envelope (55 non-deviated candidates). Adding 30 fresh candidates to confirm an anomaly that was 5/60 = 8.3% of the original corpus is sufficient to either reproduce or not reproduce it at conventional statistical power. Power calculation: under the null that clean runs behave like the 55-candidate envelope (mean within Manhattan ≈ 0.5), a one-sample test of 15 within-reconstruction distances (3 reconstructions × 5 tests) has >80% power to detect a mean shift of 4 Manhattan points (a fraction of the R4/B signature). This is the right size for a confirmation, not the right size for a fresh baseline.

### 4.3 Generation parameters

- **Frozen source:** identical to DBI-BIB-001 (commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`).
- **Frozen source files:** identical (sha256 `4582d768...` and `7d6d0819...`).
- **Frozen test corpus:** identical (T1-T5 payloads and sha256 from `TEST-CORPUS.md` at execution-package commit `00676a3`).
- **Reconstruction model:** Claude Sonnet 4.6 (same as BIB-001 generation).
- **Reconstruction runtime:** Claude Code 2.1.170 (same).
- **Tools posture:** `--allowedTools '' --tools '' --disallowedTools 'WebFetch,WebSearch'` (same).
- **Reconstruction input:** byte-identical to BIB-001's `inputs/reconstruction-input.txt` (sha256 `03ce4c40816f9c5b4a47ee5e6ca6a051a605b7035b1f7ce70ad12f10ea03e72f`).
- **Session discipline:** each R7-R9 is a fresh session (no `--resume` from prior R). No candidate is run twice. No repair, hint, clarification, or interpretation between prompts.
- **Staging:** all 3 reconstructions may run in a single Claude quota window if quota permits; if quota pressure recurs, stage across two windows. Per-stage runtime reverification (§5 below).

### 4.4 Evaluation parameters

- **Frozen rubric:** identical to BIB-001 (`EVALUATOR-RUBRIC.md` at `00676a3`).
- **Evaluator A:** Codex CLI 0.146.0 with `gpt-5.6-sol`.
- **Evaluator B:** Claude Code 2.1.170 with `claude-opus-4-7`.
- **Blinding:** fresh UUID4 blind IDs for all 30 candidates; two independent OS-CSPRNG-seeded permutations (independent of the BIB-001 seeds); blind-map.json withheld from both evaluators until both score sets are locked.
- **No reuse of BIB-001 scores.** The BIB-002 evaluators see only BIB-002 candidates.
- **No third evaluator.** No sample expansion. No discretionary optional analyses.

### 4.5 What is NOT done

- No Attempt-1 capture reuse.
- No regeneration, replacement, or inspectively-curative modification of any candidate.
- No third evaluator.
- No optional analyses beyond the preregistered decision rules.
- No post-hoc threshold modification.
- No reuse of BIB-001 blind IDs or orderings.
- No inspection of the candidate content before both score sets are locked.

---

## 5. Preflight (gate 1, before generation)

Before R7:

1. Verify frozen source and execution package (commit `c3692150`, package commit `00676a3`).
2. Verify both source file SHAs.
3. Verify the 5 individual test prompt SHAs match frozen `TEST-CORPUS.md`.
4. Verify the reconstruction-input.txt SHA matches BIB-001's (no drift).
5. Verify Claude Sonnet 4.6 is addressable on the current runtime.
6. Verify no-tools posture is effective.
7. Smoke-test Claude Sonnet 4.6 with a one-word non-experiment prompt in a disposable session.
8. Verify direct file redirection preserves complete first-call output (no SIGPIPE/tee/head truncation).
9. Verify both evaluators (Codex gpt-5.6-sol, Claude Opus 4.7) are callable immediately before any BIB-002 candidate is exposed.
10. Verify explicit Frank-as-PI GO has been received referencing this preregistration.

Any failed preflight item = BLOCKED. Do not weaken isolation or silently repair the protocol.

---

## 6. Generation (gate 2)

For each Rn ∈ {R7, R8, R9}:

1. Generate a fresh session UUID.
2. Verify session is fresh (no prior Amazing Birthday context).
3. Submit the exact `inputs/reconstruction-input.txt` bytes as the first application-bearing input.
4. Capture the first reconstruction response atomically via direct redirection.
5. Verify reconstruction-ready response indicates Amazing Birthday is ready.
6. Execute Block A in order: T1, T2, T3, T4, T5.
7. Execute Block B in order: T1, T2, T3, T4, T5.
8. Do not repair, hint, clarify, summarize, reset, or hint between prompts.
9. Compute SHA-256 over every raw output and stderr.
10. Record session ID, timestamps, exit codes, raw bytes hashes, stderr hashes.

If any reconstruction does not reach test-ready state on first call → mark `reconstruction_ready=false`, preserve evidence, quarantine that reconstruction, continue with the remaining reconstructions. If more than 1 reconstruction fails infrastructure-side → §10 stop condition.

---

## 7. Blind map (gate 3)

After all 30 raw outputs exist:

1. Assign 30 fresh UUID4 blind IDs (independent of BIB-001 IDs).
2. Generate two independent OS-CSPRNG-seeded Fisher-Yates permutations (independent of BIB-001 seeds).
3. Preserve `blind-map.json` privately (operator-only).
4. Record all hashes (blind-map, ordering seeds, ordering file SHAs).
5. Build evaluator-X-input.md packets (frozen rubric + frozen contract + ordered candidate records with no provenance).
6. Withhold `blind-map.json` from both evaluators until both score sets are locked.

---

## 8. Independent scoring (gate 4, locked before unblind)

For each evaluator:

1. Submit evaluator-X-input.md to the evaluator runtime.
2. Capture full raw response.
3. Parse the 30 records (validate completeness, required fields, total_score consistency).
4. Write `evaluator-X-scores.jsonl` (parsed) and `evaluator-X-scores-LOCKED.jsonl` (frozen).
5. Compute SHA-256 over the LOCKED file.
6. Write `evaluator-X-lock-record.json` with runtime/provenance/completeness.
7. Do NOT reveal `blind-map.json` until BOTH evaluators are locked.

---

## 9. Decision rules (frozen before generation, NOT modifiable after seeing data)

### 9.1 Primary question

**Q: Does the R4/B identity-breaking pattern recur?**

The signal of "pattern recurrence" is defined as: **both evaluators independently classify 2 or more of the 30 new candidates as IDENTITY-BREAKING (i.e., DIFFERENT or total_score ≤ 9), OR a within-reconstruction (A→B) Manhattan distance mean across the 15 (3 reconstructions × 5 tests) pairs exceeds 4.0.**

Either condition = pattern reproduced → fails to confirm DEV-002 attribution → DbI Evolution remains blocked.

Neither condition = pattern does not reproduce → confirms DEV-002 attribution → establishes the precedent for an infrastructure-contamination exclusion rule for the Evolution Experiment.

A weaker signal (1 of the 30 candidates classified as DIFFERENT by both evaluators, or a within-mean in the 2-4 range) = **INCONCLUSIVE_PENDING_FURTHER** — neither confirmation nor refutation; Frank-as-PI decides.

### 9.2 Secondary statistics (descriptive only, not gating)

- Per-evaluator classification counts.
- Per-reconstruction within-Recon (A vs B) Manhattan distances (15 pairs per evaluator).
- Per-evaluator identity-preservation fraction on the 30 candidates.
- Three-class agreement and kappa between evaluators (descriptive).
- Per-dimension mean absolute evaluator difference (descriptive).

### 9.3 Why the threshold is 2 or more DIFFERENT (not 1)

The BIB-001 R4/B cluster was 5 contiguous candidates (the entire Block B of one reconstruction). A single isolated DIFFERENT classification could arise from any incidental run-specific issue and would not, by itself, reproduce the *cluster* pattern. Requiring 2-or-more DIFFERENT (both evaluators independently) preserves the cluster-vs-incident distinction. The within-mean threshold of 4.0 is set below the BIB-001 R4 signature (≈13.5 by Evaluator A on R4 within-distances) and well above the 55-candidate envelope's within-mean (0.5-1.0). 4.0 is the midpoint between "indistinguishable from the clean envelope" and "indistinguishable from the original R4/B contamination"; a stricter threshold (e.g., 8.0) would risk false-negative confirmation.

---

## 10. Stop conditions

Stop rather than expanding if:
- Source verification fails.
- Claude Sonnet 4.6 runtime is materially unavailable.
- More than 1 of the 3 reconstructions experiences infrastructure failure (BIB-001's §14 rule, scaled down).
- Capture integrity becomes unreliable (truncation, encoding defects).
- Both evaluators fail Gate 1 callability.

No automatic expansion beyond 3 reconstructions. The confirmatory sample size is fixed.

---

## 11. Required return package

1. `MANIFEST.json` (EVALUATED state).
2. SHA-256 inventory over the 30 raw outputs and all evaluation artifacts.
3. Three reconstruction records.
4. 30 raw test outputs (or quarantine + reason for any absent).
5. Blind mapping and evaluator order records.
6. Two locked evaluator score sets with documented SHAs.
7. Agreement metrics (identity-preservation agreement, three-class agreement, per-dim MAE).
8. Within-reconstruction Manhattan distance table (15 pairs per evaluator).
9. Deviation log (any new deviations must be recorded; none are expected under clean infrastructure).
10. Decision-rule result (PATTERN_REPRODUCED / PATTERN_NOT_REPRODUCED / INCONCLUSIVE_PENDING_FURTHER).
11. Recommendation on whether to proceed to DbI Evolution Experiment.

---

## 12. Authorization boundary

This preregistration authorizes execution of **DBI-BIB-002 as designed above only**.

It does NOT authorize:
- Sample expansion beyond 3 reconstructions.
- Reuse of BIB-001 scores, blind IDs, or orderings.
- A third evaluator.
- Optional analyses beyond §9.2.
- Post-hoc threshold modification.
- Execution of the DbI Evolution Experiment.
- Any reinterpretation of DBI-BIB-001-RERUN-001's INCONCLUSIVE disposition.

A separate Frank-as-PI GO referencing this preregistration must be received before execution begins.

---

## 13. Connection to the prior result

DBI-BIB-001-RERUN-001 produced: 55 candidates cleanly preserving identity by both evaluators; 5 candidates classified as IDENTITY-BREAKING by both, all concentrated in R4/B (the documented DEV-002 infrastructure-failure subset). Formal disposition INCONCLUSIVE.

DBI-BIB-002 produces: 30 fresh candidates on the same generation path, executed without the DEV-002 failure mode, scored blind by both evaluators. The preregistered decision rules in §9 decide whether the prior R4/B anomaly was a deviation-attributable artifact or a behavioral-baseline failure.

If PATTERN_NOT_REPRODUCED → the formal BIB-001 disposition can be reclassified as **PASS — BASELINE CALIBRATED WITH DOCUMENTED INFRASTRUCTURE-CONTAMINATION EXCLUSION** (the 55-candidate envelope becomes the operative baseline; an explicit exclusion rule is added to the protocol for the Evolution Experiment). The DbI Evolution Experiment may then be considered.

If PATTERN_REPRODUCED → the formal BIB-001 disposition is confirmed: **INCONCLUSIVE — BASELINE NOT SUFFICIENTLY STABLE**; the 55-candidate envelope does not generalize; DbI Evolution remains blocked pending specification/reconstruction process/behavioral metric review.

If INCONCLUSIVE_PENDING_FURTHER → neither; Frank-as-PI decides the next move.

---

## 14. Editorial note (pre-emptive)

Whatever this experiment returns, it will produce a stronger article than either possible article written today. The methodological discipline of preserving an inconvenient result, isolating the anomaly, designing a confirmatory test, and recording the decision rules before seeing the data is itself publishable evidence of research-process integrity — independent of whether the original anomaly reproduces or not. The "research process is willing to preserve an inconvenient result" property is itself a publishable signal for an unknown researcher asking developers to take unconventional architectural claims seriously.

---

## 15. Provenance

- **Protocol designer:** Frank Ventura (PI)
- **Operator:** Hermes Agent (under DBI Research Manager Mandate, 2026-08-27)
- **Frozen references (NOT duplicated locally — Git-addressable):**
  - DBI-BIB-001 protocol: commit `b9b6c86c017903cca061b4c2f7b798c82870f9c5`
  - Execution Package v0.1: index `00676a3343fbf786e3b72b32afcc6e5071582cb8` (freeze `ebbb4319fcc7daedcc55e4be78a99e948e2a8c9c`)
  - BIB-001 evidence (reference only): `experiments/2026-09-05-dbi-bib-001-rerun-001/`
  - Frozen source: commit `c369215024c9f8a849daf11bd4b872d7ee566a7a`
- **Inheritance:** inherits frozen source, frozen rubric, frozen test corpus, evaluator identity, and protocol structure from BIB-001. The ONLY structural change vs BIB-001 is the 3-reconstruction × 10-test design and the preregistered decision rules in §9.
- **Authoritative snapshot:** this file (to be SHA-256-fingerprinted at GO receipt and re-fingerprinted after each gate).
