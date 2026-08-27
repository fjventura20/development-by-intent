# Amazing Birthday — Reconstruction Results Index

Public reconstruction results for Amazing Birthday live under `experiments/` in the
repository root. This index lists them in chronological order with links to the
preserved raw evidence, the operator scoring, and (where available) the independent
reviewer scoring.

Each experiment is self-contained: it carries its own `MANIFEST.json`, preregistered
protocol, frozen source commit SHA, raw reconstruction transcripts, raw test outputs,
and scoring artifacts. Do not infer a result from a single summary field; open the
preserved outputs and scoring files for the experiment you want to audit.

## Index

| # | Experiment directory | Mode | Provider / Model | Frozen source | Operator score | Independent score | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | [`experiments/2026-08-24-amazing-birthday-clean-room-001/`](../../experiments/2026-08-24-amazing-birthday-clean-room-001/) | artifact-only | ChatGPT (GPT-class) | `c3692150…ee566a7a` | 20 / 20 / 20 | 60 / 60 | **PASS** |
| 2 | [`experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/`](../../experiments/2026-08-25-amazing-birthday-grok-reconstruction-001/) | observational | Grok | (observational; not preregistered clean-room) | (factual regression not independently verified) | — | preliminary |
| 3 | [`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/`](../../experiments/2026-08-25-amazing-birthday-hermes-operated-claude-001/) | artifact-only | Claude / claude-sonnet-4-6 | `c3692150…ee566a7a` | 19 / 20+ repair-defect | 18 / 17 | INDETERMINATE |
| 4 | [`experiments/2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/`](../../experiments/2026-08-25-amazing-birthday-hermes-operated-claude-replication-002/) | artifact-only | Claude / claude-sonnet-4-6 | `c3692150…ee566a7a` | clean replication | 19 / 19 / 17 | **PASS** |
| 5 | [`experiments/2026-08-25-amazing-birthday-hermes-operated-gemini-003/`](../../experiments/2026-08-25-amazing-birthday-hermes-operated-gemini-003/) | artifact-only | Gemini | `c3692150…ee566a7a` | — | — | BLOCKED (no Gemini CLI on host) |
| 6 | [`experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/`](../../experiments/2026-08-26-amazing-birthday-transcript-only-claude-004/) | transcript-only | Claude / claude-sonnet-4-6 | `c3692150…ee566a7a` | 20 / 20 / 20 | (ChatGPT review pending relay) | operator PASS |
| 7 | [`experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/`](../../experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-005/) | transcript-only (capture-discipline v0.2) | Claude / claude-sonnet-4-6 | `c3692150…ee566a7a` | clean capture | (ChatGPT review pending relay) | operator PASS |
| 8 | [`experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-006/`](../../experiments/2026-08-27-amazing-birthday-transcript-only-claude-replication-006/) | transcript-only (freeze-discipline v0.2) | Claude / claude-sonnet-4-6 | `c3692150…ee566a7a` | 20 / 20 / 20 / 20 | (ChatGPT review pending relay) | operator PASS |

## Per-experiment required evidence

For each row above, the experiment directory is expected to contain:

- `MANIFEST.json` — frozen experimental parameters, preregistered tests, model pinning,
  isolation declaration;
- `README.md` — operator narrative and disposition;
- `results/` — preserved raw outputs (`reconstruction-raw.json` or equivalent,
  `test-N-raw.json` for each test), scored outputs, environment record, failures, and
  interpretation;
- For preregistered experiments, a `protocol/` subdirectory carrying the frozen
  procedural documents;
- For transcript-only experiments, an `artifact-record.md` listing the exact byte hash
  of each supplied transcript at execution time.

Open the experiment directory directly to confirm completeness rather than trusting this
index column.

## Results that are NOT yet public

The following are not currently under `experiments/`:

- a deliberate **implementation-freedom** run (two reconstructing environments given the
  same durability package but free to choose language, framework, database, UI);
- a deliberate **stateful / data-producing** run (the Receipt Organizer specimen);
- **variance** evidence under one protocol across many runs.

These are open agenda items; see [`RESEARCH-AGENDA.md`](../../RESEARCH-AGENDA.md).

## Provenance

This index was authored 2026-08-27 against the repository at that time. It is a
catalog of preserved experimental evidence, not a meta-analysis. Verdict column entries
are taken from the operator disposition of each experiment and from any independent
review that has been recorded. If an experiment's verdict is updated (e.g. ChatGPT
independent scoring arrives for a transcript-only run), update this index in the same
commit as the experiment's score file.