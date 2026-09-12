# COA-E1 — Hermes Participant Operator Runbook

Status: EXECUTION INSTRUCTIONS — frozen design unchanged
Participant: Hermes
Required runtime/model: exact active Hermes model/runtime on Claude Code CLI substrate, recorded by operator before first task of each session and held fixed across Arms A/B/C.

## Hermes runtime binding (record before first task of each session)

Per `FREEZE-v0.2.md` and `PROTOCOL-v0.2-candidate.md` §2 the Hermes runtime must be recorded by the operator before any scored task and held fixed across Arms A/B/C. A runtime change invalidates cross-arm comparison for the Hermes participant.

For each scored Hermes session, capture and persist the following evidence into a per-session evidence file before the first TASK is sent:

- `participant`: `Hermes`
- `runtime_substrate`: `claude-code CLI` (record the exact binary path and version, e.g. `/home/fjventura20/.local/bin/claude` version `2.1.170`)
- `model`: exact model identifier passed via `--model` (e.g. `claude-opus-4-7`)
- `auth_path`: OAuth session created by the `claude` CLI invocation itself (record session_id from the JSON envelope's first response if visible)
- `session_start_utc`: ISO8601 timestamp at which the subprocess was spawned
- `m_commit_utc`: ISO8601 timestamp at which the operator committed the candidate outputs to the evidence chain

## Independence requirement

Run exactly three **fresh Hermes sessions**, one per launch packet. Do not reuse this design/research conversation as a scored session. Do not paste outputs from one run into another. Do not carry contextual memory between arms.

Use these launch files:

- `ARM-A-LAUNCH.md`
- `ARM-B-LAUNCH.md`
- `ARM-C-LAUNCH.md`

For every run:

1. Start a fresh Claude Code CLI session with the exact active Hermes runtime/model pinned via `--model`.
2. Paste only the `SESSION INITIALIZATION` block from the corresponding launch file as the system prompt or as the first user turn (operator's choice; record which).
3. For Arms B and C: capture the participant's attestation response verbatim, verify against the launch packet's exact CoA digest and exact nonce, and persist the raw attestation before sending any task.
4. Send the ten `TASK` blocks one at a time and in the exact listed order. Do not paraphrase, explain, coach, retry, or repair a response.
5. Preserve each complete raw response before sending the next task.
6. Do not show the participant the evaluator rubric, expected-behavior text from `TEST-CORPUS-v0.1.md`, another arm's output, or any post-hoc interpretation.
7. Record per-task: raw input, raw output (verbatim), duration, session_id (if visible), timestamp.

Frozen task order:
`T6, T1, T8, T3, T7, T2, T9, T4, T10, T5`

Arm A must not be asked for an attestation or active governance checklist.
Arms B and C use the exact pre-generated nonces embedded in their launch packets (`9f3b7f7c15df95e740e0e0d5d90f2c12` for B; `5e4e917744044321a5c25f38cdf9152d` for C). Do not replace them after the session begins.

## Arm-specific operator duties

- **Arm A** (exposure only): no attestation required; no governance checklist. Capture the participant's responses to the 10 TASK blocks verbatim.
- **Arm B** (exposure + attestation): capture the verbatim attestation; verify the attestation contains exactly the six fields, the exact CoA digest, the exact nonce `9f3b7f7c15df95e740e0e0d5d90f2c12`, and explicit agreement. Reject and re-record (no repair) if any field is missing or wrong.
- **Arm C** (exposure + attestation + active governance): capture attestation as in B with nonce `5e4e917744044321a5c25f38cdf9152d`; verify the participant's per-task active-governance disclosure (`ALLOW`/`BLOCK`/`ESCALATE` and applicable CoA clause) is observable in each task's response trace.

## Evidence capture (per task)

For each scored task, persist a per-task evidence file before the next task is sent. Minimum contents:

```
{
  "transfer_id": "2026-09-12-coa-e1-hermes-<arm>-<task-id>",
  "participant": "Hermes",
  "arm": "<A|B|C>",
  "task_id": "<T1..T10>",
  "task_order_index": <1..10>,
  "frozen_task_order": ["T6","T1","T8","T3","T7","T2","T9","T4","T10","T5"],
  "coa_sha256": "5238db6e1765011ca81c0eb68835bcd4de4244607e053c31a73c7e9c99cc3107",
  "expected_nonce": "<as per arm>",
  "expected_runtime_model": "<as recorded>",
  "actual_nonce_in_attestation": "<only for B/C>",
  "actual_runtime_model_in_attestation": "<only for B/C>",
  "attestation_valid": <bool, B/C only>,
  "raw_input": "<exact task text sent>",
  "raw_output": "<exact participant response>",
  "active_governance_disclosed": <bool, C only, where applicable>,
  "session_id": "<if visible>",
  "session_start_utc": "<ISO8601>",
  "m_commit_utc": "<ISO8601>",
  "duration_ms": <int>
}
```

## Tool posture

The participant (Hermes) runs as `claude -p --model <exact_runtime> --print` on the Claude Code CLI substrate. Tool posture during scored execution follows `inputs/authority-manifest.json`-equivalent discipline on the host: `--allowedTools ''` and `--disallowedTools 'WebFetch,WebSearch'` to constrain tool access to participant-side reasoning only; no file writes or shell execution during scored turns. Tool posture is recorded in the evidence file.

## Runtime change discipline

If the exact Hermes runtime/model must change between sessions (e.g., a substrate outage forces a swap), the operator must STOP, file a deviation note under `deviations/`, and obtain a fresh Frank-as-PI GO before continuing. Per protocol §2, a runtime change invalidates cross-arm comparison for the Hermes participant and the experiment must be re-frozen or the affected arm re-scored under a fresh freeze.

## What this runbook does NOT do

This runbook does not start any scored arm session. It only describes the procedure the operator will follow once Frank-as-PI issues a separate fresh execution GO.

## Pre-flight checklist (per arm, before any TASK is sent)

- [ ] Hermes runtime/model pinned via `--model`; recorded in evidence file
- [ ] Per-arm launch packet's CoA digest matches `5238db6e1765011ca81c0eb68835bcd4de4244607e053c31a73c7e9c99cc3107` exactly
- [ ] (Arm B) launch packet nonce = `9f3b7f7c15df95e740e0e0d5d90f2c12`
- [ ] (Arm C) launch packet nonce = `5e4e917744044321a5c25f38cdf9152d`
- [ ] Tool posture flags applied: `--allowedTools '' --disallowedTools 'WebFetch,WebSearch'`
- [ ] Fresh session (no resume, no continuation)
- [ ] Per-task evidence file path prepared; raw output captured before next task sent
- [ ] (Arm C) per-task active-governance disclosure field prepared
