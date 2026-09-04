# DBI-BIB-001 — Evaluation Procedure

**Version:** v0.1

## Role assignment

The experiment requires two independent evaluator roles:

- **Evaluator A:** an evaluator/model instance not used as the reconstruction engine and not involved in protocol design or experiment operation.
- **Evaluator B:** a second independent evaluator/model instance that does not see Evaluator A's scores and is not involved in protocol design or experiment operation.

ChatGPT, as protocol designer and final synthesizer, is **not** an evaluator for DBI-BIB-001. Hermes, as operator, is **not** an evaluator.

The exact evaluator provider/model/runtime identifiers must be locked in the run manifest **before either evaluator receives candidate outputs**. Prefer distinct model families for A and B. If two eligible independent evaluators cannot be established, generation evidence may be preserved, but evaluation status is `BLOCKED` and no PASS/FAIL baseline conclusion may be issued.

## Blind candidate construction

After all raw generation outputs are captured and hashed, the operator creates 60 opaque candidate IDs using a cryptographically random or UUID-based identifier. Candidate IDs must not encode:

- R1–R6;
- Block A/B;
- T1–T5;
- execution order;
- timestamp order.

The operator retains a private mapping file:

`blind-map.json`

mapping each blind ID to reconstruction ID, block, test ID, raw-output path, and raw-output hash.

`blind-map.json` must not be supplied to either evaluator before both evaluator score sets are locked.

## Randomization

Create one random permutation of the 60 blind candidates for Evaluator A and an independently generated second permutation for Evaluator B.

Record:

- randomization method;
- random seed or reproducible randomization record when available;
- ordered candidate-ID list supplied to each evaluator.

The two orderings should differ unless random chance produces the same ordering.

## Evaluator input packet

Each evaluator receives:

1. frozen `03-behavioral-baseline.md`;
2. frozen `EVALUATOR-RUBRIC.md`;
3. for each blind candidate: blind ID, exact test input, and raw candidate output.

No other experimental context is required or permitted during primary scoring.

## Locking scores

Each evaluator's complete 60-record score set must be written and hashed before any cross-evaluator comparison occurs.

After lock:

1. preserve Evaluator A score artifact and hash;
2. preserve Evaluator B score artifact and hash;
3. reveal `blind-map.json` to the analysis stage;
4. compute evaluator agreement and variance statistics;
5. do not overwrite original evaluator scores.

Any adjudication is a separate derived artifact and may clarify interpretation but may not replace primary evaluator records.

## Agreement metrics

Pre-registered rubric-usability checks:

1. **Identity-preservation agreement:** collapse `SAME` and `SAME_WITH_VARIANCE` to `IDENTITY_PRESERVED`; compare against `DIFFERENT`. Require at least **90% raw agreement** across 60 candidates.
2. **Three-class agreement:** report raw exact agreement and Cohen's kappa for SAME / SAME_WITH_VARIANCE / DIFFERENT. Kappa is descriptive because high class imbalance can depress it.
3. **Dimension agreement:** for each of the four 0–4 dimensions, report mean absolute evaluator difference. The rubric-usability gate requires mean absolute difference <= **1.0 point** for each dimension.

Failure of either gate in items 1 or 3 makes the experiment-level disposition `INCONCLUSIVE — EVALUATOR RUBRIC NOT SUFFICIENTLY CALIBRATED`, regardless of candidate performance.

## Variance metric

For evaluator E and candidate behavior vector

`v = [C, S, N, F]`

use Manhattan distance:

`D(v1,v2) = |C1-C2| + |S1-S2| + |N1-N2| + |F1-F2|`

Range: 0–16.

### Within-reconstruction distances

For each R1–R6 and T1–T5:

`D_within(R,T) = D(vector for Block A, vector for Block B)`

This yields 30 within-reconstruction distances per evaluator.

### Between-reconstruction distances

For each block and test, compare all unordered reconstruction pairs:

`D_between(Ri,Rj,T,B)` for `i < j`.

Six reconstructions yield 15 pairs × 5 tests × 2 blocks = 150 between-reconstruction distances per evaluator.

Report for each distribution:

- count;
- mean;
- median;
- standard deviation;
- minimum;
- maximum;
- 25th, 75th, 90th, and 95th percentiles.

Do not collapse Evaluator A and B scores into a single averaged behavior vector. Compute distributions separately, then compare interpretations.

## Baseline envelope

The provisional behavioral-identity envelope for the later Evolution Experiment is defined separately for each evaluator as:

- the observed range and percentile distribution of within-reconstruction distances;
- the observed range and percentile distribution of between-reconstruction distances;
- the frequency of SAME, SAME_WITH_VARIANCE, and DIFFERENT classifications;
- the frequency and type of violations.

The final synthesizer may recommend a prospective evolution threshold from these observed distributions, but may not retroactively change DBI-BIB-001's frozen scoring rules.

## Experiment-level gate

A `PASS — BASELINE CALIBRATED` requires all of the following:

1. at least 90% of valid observations are classified by **both** evaluators as SAME or SAME_WITH_VARIANCE;
2. no systematic identity-breaking behavior appears across multiple reconstructions;
3. evaluator-usability gates above pass;
4. the between-reconstruction distance distribution is bounded and interpretable rather than dominated by categorical DIFFERENT outcomes;
5. no protocol-level stop condition invalidates interpretation.

Otherwise the final disposition is either `FAIL — BEHAVIORAL IDENTITY NOT STABLE` or `INCONCLUSIVE`, with the reason recorded.
