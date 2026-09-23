# Canonical and Historical Artifact Index

The repository intentionally preserves research history. Some older architecture and Value Architecture files remain at their original root paths because frozen manifests, commit references, blob hashes, discussions, and external links may depend on those paths.

Their presence at root does **not** mean every version is current.

## Current public entry points

- [`README.md`](README.md) — orientation and developer entry point.
- [`CURRENT-STATUS.md`](CURRENT-STATUS.md) — authoritative current research posture.
- [`EVIDENCE.md`](EVIDENCE.md) — bounded evidence summary and claim limits.
- [`QUICK-VALIDATION.md`](QUICK-VALIDATION.md) — five-minute external contribution path.
- [`EVOLUTION-FAILURE.md`](EVOLUTION-FAILURE.md) — promoted negative result on targeted behavioral evolution.
- [`REVIEWER-DISCLOSURES.md`](REVIEWER-DISCLOSURES.md) — provenance and independence status of the internal architecture-review chain.

## Current INSA architecture baseline

- [`INSA-ARCHITECTURE-v0.3-FROZEN.md`](INSA-ARCHITECTURE-v0.3-FROZEN.md) — freeze manifest / binding record.
- [`INSA-ARCHITECTURE-v0.3-candidate.md`](INSA-ARCHITECTURE-v0.3-candidate.md) — exact normative source bound by the freeze.

These files are the current frozen architecture baseline for experiments that claim to test INSA v0.3. They must not be edited in place.

## Architecture research history — retained at canonical paths

These are historical inputs and review records, not current architecture baselines:

- [`INSA-ARCHITECTURE-v0.1.md`](INSA-ARCHITECTURE-v0.1.md) — superseded architecture draft.
- [`INSA-ARCHITECTURE-v0.1-ADVERSARIAL-REVIEW.md`](INSA-ARCHITECTURE-v0.1-ADVERSARIAL-REVIEW.md) — internal review, disposition `REVISION_REQUIRED_BEFORE_ARCHITECTURE_FREEZE`.
- [`INSA-ARCHITECTURE-v0.2-candidate.md`](INSA-ARCHITECTURE-v0.2-candidate.md) — superseded candidate.
- [`INSA-ARCHITECTURE-v0.2-FREEZE-REVIEW.md`](INSA-ARCHITECTURE-v0.2-FREEZE-REVIEW.md) — internal review, disposition `REVISION_REQUIRED_BEFORE_FREEZE`.
- [`INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md`](INSA-ARCHITECTURE-v0.3-FINAL-FREEZE-REVIEW.md) — internal review that permitted freezing v0.3 for experimentation; this is a review record, not an independent validation certificate.

See [`REVIEWER-DISCLOSURES.md`](REVIEWER-DISCLOSURES.md) before interpreting the review labels.

## Current Value Architecture standard

- [`VALUE-ARCHITECTURE-STANDARD-v0.2.md`](VALUE-ARCHITECTURE-STANDARD-v0.2.md) — current experimental Value Architecture standard.

Historical predecessor:

- [`VALUE-ARCHITECTURE-STANDARD-v0.1.md`](VALUE-ARCHITECTURE-STANDARD-v0.1.md) — superseded draft retained for research history.

## Evidence hierarchy

Public summaries are navigation aids, not substitutes for frozen evidence.

When documents conflict, use this precedence:

1. frozen experiment inputs, outputs, score records, and provenance;
2. experiment-specific manifests and protocols;
3. evidence indexes and result summaries;
4. `EVIDENCE.md` and `CURRENT-STATUS.md`;
5. README/tutorial explanatory material.

A later summary must not silently rewrite an earlier frozen result.

## Why files are not simply moved into an archive directory

Moving historical files would make the root cleaner but could damage auditability by changing canonical paths or breaking references. The project therefore prefers **explicit status labeling and indexing** over path churn for already-bound research artifacts.

New superseded material should be organized more cleanly where possible, but historical evidence integrity takes priority over cosmetic root reduction.