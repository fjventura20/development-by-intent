# Independent Review — BP-RO-ARTIFACT-ONLY-CLAUDE-001

Reviewer: ChatGPT

Review type: independent documentary review, **not blinded**. The review package exposed condition, operator interpretation, and operator scores before this assessment. This review therefore checks the recorded outputs against the stated rubric; it is not an independent blinded efficacy evaluation.

## Integrity

All 33 files declared in the v0.2 request manifest were fetched from `mailbox/main` and independently checked over their UTF-8 bytes. All 33 SHA-256 values matched.

## Per-test scoring

| Test | Critical requirement | Score | Disposition | Independent finding |
|---|---|---:|---|---|
| T1 — CVS Pharmacy | ISO date; printed total remains canonical | 4/4 | PASS | Date is `2026-09-03`; subtotal, tax, total `$40.41`, payment, items, and pharmacy classification are correct and internally consistent. |
| T2 — Corner Bistro | Tip acknowledged but not folded into printed total | 4/4 | PASS | Printed total remains `$24.30`; `$4.37` tip is explicitly treated as outside that total. Extraction and restaurant classification are correct. |
| T3 — strictly over $50 | Return only receipts with total > $50 | 4/4 | PASS | Correctly returns no matches and shows that `$40.41` and `$24.30` are both below the strict threshold. |
| T4 — duplicate | Detect merchant+date+total duplicate; do not modify ledger | 4/4 | PASS | Duplicate is identified on all three keys and explicitly not stored. |
| T5 — restaurant aggregate | Correct aggregate over stored corpus | 4/4 | PASS | Returns the only restaurant receipt and correct printed-total aggregate of `$24.30`; preserves the tip qualification. |
| G — Target generalization | Accept new merchant/category and answer merchant query | 4/4 | PASS | Target is stored as retail at `$38.31`, then retrieved correctly by merchant query. |

Core preregistered score: **20/20**.

Generalization regression: **4/4**.

Combined descriptive score: **24/24**, not `24/20`. The operator's repeated `24/20` label is a denominator/reporting error. It does not change the per-test outcomes but must be corrected everywhere before publication.

## State-retention verification

The visible outputs are mutually consistent with one within-session ledger:

- R: ledger empty.
- T1: ledger count 1.
- T2: ledger count 2.
- T3: both stored receipts are available to the query.
- T4: duplicate is rejected and ledger declared unchanged.
- T5: the stored restaurant receipt remains available.
- G receipt: ledger count 3.
- G query: the newly stored Target receipt is available.

Disposition: **PASS for within-session state retention**.

Two corrections are required in the operator narrative:

1. T5 did not show a three-receipt ledger. At T5 only two receipts existed; the third was added during G.
2. The evidence demonstrates conversational state retained within one Claude Code session. It does not demonstrate persistence across sessions or durable external storage.

## Protocol and v0.3 amendment assessment

The cwd pre-flight and immediate resume smoke test are sensible safeguards for the observed Claude Code 2.1.170 failure. The re-run evidence supports using a known-good short cwd and verifying resume before substantive tests.

However, v0.3 needs tightening before being treated as validated protocol:

1. **Freeze and authorization:** the amendment says `PROPOSED ... awaiting Frank authorization`, while the rerun proceeded. Record explicit authorization or label the rerun as executed under an unapproved amendment.
2. **No post-failure restart ambiguity:** specify that a failed smoke test terminates that attempt. A new cwd requires a new attempt/session identifier with both attempts preserved; do not describe a restarted R turn as continuation of the same run.
3. **Smoke-test semantics:** use a fixed neutral exchange that cannot modify the application ledger, and define what proves continuation beyond receiving any plausible response. `ping`/`pong` is useful transport evidence but weak evidence of retained application state.
4. **Capture gates:** the v0.2 protocol requires R output >200 bytes and each test output >1 KB. R was 50 bytes and the substantive outputs were approximately 139–676 bytes. The files appear complete, so the thresholds were poorly calibrated, but the run did not satisfy the written gates. Amend the gates prospectively to use structural completeness, nonempty stderr expectations, termination status, and hashes rather than arbitrary minimum sizes.
5. **Deviation handling:** the R size-gate override and all sub-1-KB captures must appear in the final deviation record, not only as a calibration note.

Assessment: **the workaround is operationally supported, but v0.3 is not cleanly validated as written until these protocol discrepancies are resolved.**

## Overall classification

### Functional run

**PASS** — all five core tests pass at 20/20 and G passes at 4/4. The outputs support recovery of the specified Receipt Organizer behavior in a fresh Claude Sonnet 4.6 conversation using the declared artifact set, including within-session state, duplicate handling, aggregation, and one merchant/category generalization.

### Claim boundary

This run does **not** by itself establish that the durability package caused the successful behavior. There is no thin-description or contract-only control, so it cannot distinguish package transmission from baseline frontier-model competence. It also uses one provider, the same model family, the same conversational mechanism, one reconstruction, an unblinded operator, and an informed independent reviewer.

Accordingly, the defensible conclusion is:

> The declared Receipt Organizer artifact set was sufficient for a fresh Claude Sonnet 4.6 session to produce the tested stateful behavior in one conversation.

The stronger statement that "behavioral portability at the stateful/data-producing tier is established" should remain **provisional**, not closed, until at least:

- an ablation/control condition tests whether the package adds measurable fidelity;
- protocol deviations and denominator errors are corrected;
- an evaluator blinded to condition and operator score reviews anonymized outputs; and
- preferably, a second provider or mechanism replicates the result.

## Comparison with Amazing Birthday tier 2

Receipt Organizer probes a more demanding behavioral surface than Amazing Birthday because correctness is visible in normalized fields, arithmetic, duplicate behavior, queries, and evolving state. That makes these outputs less dependent on subjective recognition.

The package does not contain the full AB replication evidence needed to independently recompute the cited `19/19/17` results, so no direct evidentiary equivalence is claimed here. Receipt Organizer provides stronger observable functional checks, while both lines still need controlled ablation to attribute success to their durability packages.

## Final disposition

- Manifest integrity: **PASS — 33/33 hashes**
- Core behavioral tests: **PASS — 20/20**
- Generalization regression: **PASS — 4/4**
- Within-session state retention: **PASS**
- v0.3 operational workaround: **SUPPORTED WITH REQUIRED REVISIONS**
- Stateful behavioral-portability ladder closure: **PROVISIONAL; NOT YET CAUSALLY ESTABLISHED**

