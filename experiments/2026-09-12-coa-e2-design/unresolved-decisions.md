# COA-E2 — Unresolved Decisions Requiring PI Judgment

**Status:** DRAFT — eight decisions need PI adjudication before the protocol can be frozen. Each has a default recommendation; PI may accept the default or override.

## Decision matrix

| # | Decision | Default | Open question / risk | Source |
|---|---|---|---|---|
| D1 | Task set: reuse COA-E1 v0.1 vs. author fresh binding-specific tasks vs. commission ChatGPT | reuse COA-E1 | risk: COA-E1 tasks were authored under broken protocol; may not discriminate between arms. T11/T12/T13 discriminator tasks proposed; not yet adopted. | `PROTOCOL-DRAFT-v0.1.md` §10.1; `proposed-task-set-and-rubric-DRAFT.md` |
| D2 | Runner location: `/tmp` (operator infrastructure) vs. inside experiment repo | `/tmp` (matches COA-E1 precedent) | inside-repo gives version control but adds non-frozen file; `/tmp` matches operator-side discipline | `PROTOCOL-DRAFT-v0.1.md` §10.2; `OPERATOR-RUNBOOK-DRAFT.md` §10 |
| D3 | Per-arm profile MEMORY.md pre-run state | cleared to 1 byte with backup | matches COA-E1; risk: participant may overwrite the cleared MEMORY.md mid-run (as in COA-E1 ARM-C T3); operator must record this as a deviation | `OPERATOR-RUNBOOK-DRAFT.md` §2; `PROTOCOL-DRAFT-v0.1.md` §10.3 |
| D4 | Acknowledgment nonce: required or not | not required (session_id is the binding) | adding nonce adds nothing under persistent-session protocol; omitting simplifies the format | `PROTOCOL-DRAFT-v0.1.md` §5, §10.4 |
| D5 | Scoring rubric: clause-citation vs. behavior-only vs. hybrid | hybrid (`behavior_class` + `clause_citation_present` + `binding_signal_present`) | clause-citation is the strongest discriminator; behavior-only risks CoA-E1's default-compliance confound | `proposed-task-set-and-rubric-DRAFT.md` |
| D6 | Evaluator blinding: package-level vs. turn-level vs. none | package-level (REDACTED-A / REDACTED-B), runtime binding visible | package-level matches COA-E1 v6.3 adjudication precedent ("blinded scoring would add cost without rescuing the causal test" — but COA-E2 fixes the structural failure, so blinding becomes meaningful) | `PROTOCOL-DRAFT-v0.1.md` §10.6; `proposed-task-set-and-rubric-DRAFT.md` |
| D7 | Operator role acceptable on Hermes (gateway profile) given Claude rate-limit concern | yes, but confirm with PI | COA-E1 used Hermes for operator; Claude is rate-limited; the operator is non-rate-limited because the gateway is the long-running service | `PROTOCOL-DRAFT-v0.1.md` §10.7 |
| D8 | Sample size: 1 replicate × 10 tasks vs. 5 replicates × 10 tasks (50 per arm) | 5 replicates × 10 tasks | 1 replicate is too small to discriminate; 5 replicates is the minimum for any meaningful comparison; larger sample = higher cost | `proposed-task-set-and-rubric-DRAFT.md` |

## Decision-by-decision detail (for PI adjudication)

### D1 — Task set provenance

- **Default:** reuse COA-E1 v0.1 task set under the new protocol.
- **Risk:** the tasks were authored to elicit CoA-relevant behaviors under a broken protocol. Under COA-E2's correct binding, the participant's behavior may be the same regardless of arm (because the participant produces CoA-consistent output from defaults anyway, per COA-E1 evidence).
- **Alternative:** author a leaner task set with the same theoretical intent. **Or:** commission ChatGPT to author the task set under the new protocol.
- **T11/T12/T13 discriminator tasks** (proposed in `proposed-task-set-and-rubric-DRAFT.md`) explicitly probe binding rather than just CoA-compliance. If adopted, T11/T12/T13 can supplement or replace the COA-E1 task set.

### D2 — Runner location

- **Default:** `/tmp/coa-e2-runner/run_arm.py` (operator infrastructure, not under freeze).
- **Matches COA-E1 precedent:** the COA-E1 runner at `/tmp/coa-e1-v63-runner/run_arm.py` was operator-side.
- **Risk:** the runner code is not version-controlled. If the runner needs to be re-run after a STOP, the operator must reproduce it from this design document.
- **Alternative:** keep a versioned copy of the runner in the experiment repo's `experiments/2026-09-12-coa-e2-design/runner/` directory.

### D3 — Per-arm profile MEMORY.md pre-run state

- **Default:** cleared to 1 byte (`\n`) with backup at `.bak-pre-coa-e2/MEMORY.md.bak`.
- **Matches COA-E1 precedent:** COA-E1 used the same pattern. The COA-E1 ARM-C run resulted in a +718-byte MEMORY.md write by the participant (per the v6.3 erratum); this was recorded as a deviation.
- **Risk:** the participant may write to MEMORY.md mid-run again. The operator must capture this as a deviation and record the post-run state.
- **Alternative:** lock the per-arm profile's MEMORY.md file as read-only after clearing, so the participant cannot write to it. **Risk:** the participant may refuse to proceed if MEMORY.md is unwritable, or the Hermes CLI may fail to start the session.

### D4 — Acknowledgment nonce

- **Default:** not required.
- **Rationale:** the persistent session already binds the acknowledgment to the session_id. A nonce adds entropy but no binding.
- **Alternative:** keep a nonce for backward compatibility with COA-E1 v6.3's `ATTESTATION-v0.1.md`. **Risk:** adds a fixed-string template that the participant must match exactly; if the participant uses a slightly different nonce format, the attestation is invalidated.

### D5 — Scoring rubric

- **Default:** hybrid (3 dimensions: `behavior_class`, `clause_citation_present`, `binding_signal_present`).
- **Rationale:** behavior-only risks the default-compliance confound (CoA-E1 evidence). Clause-citation-only risks missing behaviors where the participant complies without citing. Hybrid is the strongest discriminator.
- **Alternative:** behavior-only with a separate post-hoc binding analysis (would require de-blinding the evaluator after scoring; not recommended).
- **Alternative:** clause-citation-only (most rigorous; risk of false negatives where the participant complies without citation).

### D6 — Evaluator blinding

- **Default:** package-level blinding with two REDACTED-A / REDACTED-B packages. Runtime binding visible (it's part of the participant identity record, not the arm treatment).
- **Rationale:** package-level matches the COA-E1 v6.3 ChatGPT adjudication precedent (which was structurally invalid for other reasons, but the blinding approach was reasonable). Runtime visibility is required because the evaluator must verify the participant identity claim.
- **Alternative:** turn-level blinding (each turn's evidence has REDACTED-A/B but the per-arm package is unblinded). **Risk:** more complex; less robust.
- **Alternative:** no blinding (the evaluator sees the arm label). **Risk:** the evaluator may bias scoring toward the expected outcome.

### D7 — Operator role

- **Default:** Hermes on the gateway's default profile.
- **Matches COA-E1 precedent:** the COA-E1 operator was Hermes (this conversation).
- **Risk:** if the operator's Hermes session is rate-limited (the default profile's API budget is shared with the gateway), a long COA-E2 run could exhaust the budget.
- **Alternative:** a separate operator profile (`coa-e2-operator`) with its own API budget. **Risk:** the operator profile needs the same `minimax` provider registration and credentials; profile-creation overhead.

### D8 — Sample size

- **Default:** 5 replicates × 10 tasks = 50 scored turns per arm. Total 100 turns across both arms.
- **Rationale:** 1 replicate is too small. 5 replicates is the minimum for any meaningful discrimination. Larger sample = higher cost.
- **COA-E1 cost precedent:** ~$0.90 for 33 turns (per COA-E1 EXECUTION-RESULT-v6.3.md). 100 turns ≈ $2.70 estimated.
- **Alternative:** 10 replicates × 10 tasks = 100 turns per arm = 200 total. Higher statistical power; higher cost (~$5.40).
- **Alternative:** 3 replicates × 10 tasks = 30 turns per arm = 60 total. Lower cost (~$1.60); insufficient for discrimination.

## PI adjudication procedure

For each decision:

1. PI reviews the default and alternatives.
2. PI either accepts the default or specifies an alternative.
3. PI-signed decision recorded in `experiments/2026-09-12-coa-e2-design/DECISIONS-v0.1.md` (drafted at freeze time; not part of this draft).
4. Decisions are binding on the operator; the operator does not deviate from them without a fresh PI GO.

## What this file does NOT do

- Does NOT adjudicate any decision (PI does).
- Does NOT freeze the protocol (the decisions become part of the freeze).
- Does NOT execute anything.

## What this file does

- Surfaces all eight open decisions in one place.
- Provides a default for each, with rationale and risk.
- Provides alternatives where appropriate.
- Documents the PI adjudication procedure.

This is the document PI should review to authorize a v0.2 freeze.
