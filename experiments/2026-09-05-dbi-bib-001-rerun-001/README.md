# DBI-BIB-001-RERUN-001 — Evidence Package Index

**Experiment:** DBI-BIB-001-RERUN-001 (DbI Behavioral Identity Baseline, Rerun 1)
**Status:** EVALUATED (2026-09-06)
**Formal disposition:** **INCONCLUSIVE** — 4 of 5 frozen quantitative gates pass; G2 fails due to 5 IDENTITY-BREAKING candidates concentrated entirely in R4 Block B (documented DEV-002 quota-deviation subset).
**Recommendation:** **Conditional** — requires Frank-as-PI adjudication. See `analysis/final-result.md`.

---

## What to read first (in this order)

1. **`analysis/final-result.md`** — the formal disposition with full interpretation, sensitivity analysis, and recommendation. This is the deliverable for Frank's adjudication.
2. **`MANIFEST.json`** — the validated experiment manifest with evaluator scores, hashes, and per-gate results embedded.
3. **`analysis/evaluator-agreement.json`** — the rubric-usability gates and agreement metrics in machine-readable form.
4. **`analysis/baseline-envelope.md`** — the variance distributions (within + between, per evaluator).
5. **`analysis/unblinded-score-audit.md` + `analysis/unblinded-per-candidate.csv`** — the per-reconstruction / per-block audit (FOR ADJUDICATION ONLY — does not change the formal disposition).
6. **`PREREGISTER.md`** — the original preflight + GO record.

## Evidence directory structure

```
experiments/2026-09-05-dbi-bib-001-rerun-001/
├── MANIFEST.json                       # Final validated manifest (EVALUATED state)
├── PREREGISTER.md                      # Original preflight + GO record
├── hashes/SHA256SUMS                   # 39-entry SHA inventory (rebuilt 2026-09-06)
├── inputs/                             # Frozen inputs (verified at preflight)
│   ├── 03-behavioral-baseline.md       # sha256 4582d768...
│   ├── RECONSTRUCTION-PROMPT.md        # sha256 7d6d0819...
│   ├── reconstruction-input.txt        # sha256 03ce4c40...
│   ├── test-corpus.txt
│   └── EVALUATOR-RUBRIC.md             # copy of execution-package rubric for evaluator visibility
├── runs/                               # 6 reconstruction sessions × 10 test outputs each
│   ├── R1/ ... R6/                     # Each: reconstruction + captures/A + captures/B
│   ├── _quarantine_R2_partial/         # quarantined v1 R2 partial capture
│   └── _quarantine_R4_partial/         # quarantined v1 R4 capture
├── blinding/                           # Gate 2 — fresh blind map (private to operator)
│   ├── blind-map.json                  # 60 UUID4 → (R/B/T, raw_path, raw_sha256, test_prompt)
│   ├── blind-map-provenance.json
│   ├── evaluator-A-order.json          # Fisher-Yates shuffle, OS CSPRNG seed_A
│   ├── evaluator-B-order.json          # Fisher-Yates shuffle, OS CSPRNG seed_B (different seed)
│   ├── build_blind_map.py              # operator-side construction script
│   ├── build_evaluator_packets.py      # operator-side evaluator packet construction
│   ├── parse_evaluator_scores.py       # operator-side score parser
│   ├── lock_scores.py                  # operator-side lock + SHA + provenance
│   ├── analyze_results.py              # operator-side statistics derivation
│   └── build_audit.py                  # operator-side unblinded audit builder
├── evaluation/                         # Gates 3-5 — independent scoring + lock
│   ├── evaluator-A-input.md            # 364KB packet shipped to A
│   ├── evaluator-A-raw.txt             # A's raw reply (Codex gpt-5.6-sol) — sha256 98ab2f74...
│   ├── evaluator-A-scores.jsonl        # parsed 60 records
│   ├── evaluator-A-scores-LOCKED.jsonl # LOCKED — sha256 df08f504...
│   ├── evaluator-A-lock-record.json    # provenance + completeness check
│   ├── evaluator-A-call.log            # CLI invocation log
│   ├── evaluator-B-input.md            # 364KB packet shipped to B
│   ├── evaluator-B-raw.txt             # B's raw reply (Claude opus-4-7) — sha256 cdf80d0a...
│   ├── evaluator-B-scores.jsonl        # parsed 60 records
│   ├── evaluator-B-scores-LOCKED.jsonl # LOCKED — sha256 d2866a96...
│   ├── evaluator-B-lock-record.json    # provenance + completeness check
│   └── evaluator-B-call.log            # CLI invocation log
├── preflight/                          # Gate 1 — evaluator callability records
│   ├── evaluator-A-preflight.json      # Codex gpt-5.6-sol smoke call passed
│   └── evaluator-B-preflight.json      # Claude Opus 4.7 smoke call passed
├── analysis/                           # Gate 6 — post-lock analysis
│   ├── evaluator-agreement.json        # IP agreement, three-class agreement, kappa, per-dim MAE
│   ├── evaluator-A-within.csv          # 30 within-reconstruction Manhattan distances
│   ├── evaluator-A-between.csv         # 150 between-reconstruction Manhattan distances
│   ├── evaluator-B-within.csv          # 30 within-reconstruction Manhattan distances
│   ├── evaluator-B-between.csv         # 150 between-reconstruction Manhattan distances
│   ├── baseline-envelope.md            # narrative summary of distributions
│   ├── unblinded-score-audit.json      # per-recon + per-block classification counts
│   ├── unblinded-score-audit.md        # human-readable version of the audit
│   ├── unblinded-per-candidate.csv     # full unblinded 60-row audit table
│   ├── final-result.json               # machine-readable disposition + per-gate results
│   └── final-result.md                 # narrative final disposition (READ THIS FIRST)
├── deviations/                         # 2 deviation records (both predate evaluation)
│   ├── DEV-RUNNER-V1-A-T1-A-T2-MISSING.json  # MATERIAL; resolved
│   └── DEV-002-r4-block-b-quota.json         # RUN-INVALIDATING; evaluated as candidate behavior
└── qualification/                      # (empty — reserved for future qualification records)
```

## Frozen references (not duplicated locally — Git-addressable)

- Protocol: `experiments/behavioral-identity-baseline-v0.1/PROTOCOL.md` at commit `b9b6c86c017903cca061b4c2f7b798c82870f9c5` (blob `1d06f02a9d331df279ee4417e23b4d52330b63f9`)
- Execution package v0.1: index commit `00676a3343fbf786e3b72b32afcc6e5071582cb8`; freeze commit `ebbb4319fcc7daedcc55e4be78a99e948e2a8c9c`
- Frozen source commit: `c369215024c9f8a849daf11bd4b872d7ee566a7a`
- Frozen source files (verified SHA-256): `4582d768...` (03-behavioral-baseline.md), `7d6d0819...` (RECONSTRUCTION-PROMPT.md)

## What the operator did NOT do (per authorization boundary)

- Did not regenerate, replace, inspectively curate, or expand the 60-candidate corpus.
- Did not invoke Attempt-1 capture reuse.
- Did not invoke a third evaluator.
- Did not modify thresholds or scoring rules after seeing the data.
- Did not characterize the baseline as PASS or FAIL unilaterally.
- Did not invoke the DbI Evolution Experiment.

## What the operator DID do

- Gate 1: re-verified both evaluators callable immediately before any candidate exposure.
- Gate 2: constructed a fresh blind map (60 UUID4 IDs, two independent OS-CSPRNG-seeded permutations).
- Gates 3-5: ran exactly two evaluator passes; locked each score set with SHA-256 BEFORE revealing the blind map.
- Gate 6: computed all five frozen quantitative decision rules; unblinded the locked score sets; reported per-candidate audit without removing outliers.
- Produced this evidence package for Frank's adjudication.
