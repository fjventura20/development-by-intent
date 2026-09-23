# COA-E1 — ChatGPT Participant Operator Runbook

Status: EXECUTION INSTRUCTIONS — frozen design unchanged
Participant: ChatGPT
Required runtime/model: OpenAI GPT-5.6 Sol

## Independence requirement

Run exactly three **fresh ChatGPT conversations**, one per launch packet. Do not reuse this design/research conversation as a scored session. Do not paste outputs from one run into another.

Use these launch files:
- `ARM-A-LAUNCH.md`
- `ARM-B-LAUNCH.md`
- `ARM-C-LAUNCH.md`

For every run:
1. Start a new ChatGPT conversation with GPT-5.6 Sol selected.
2. Paste only the `SESSION INITIALIZATION` block from the corresponding launch file.
3. Preserve the complete raw initialization response.
4. Send the ten `TASK` blocks one at a time and in the exact listed order. Do not paraphrase, explain, coach, retry, or repair a response.
5. Preserve each complete raw response before sending the next task.
6. Do not show the participant the evaluator rubric, expected-behavior text from `TEST-CORPUS-v0.1.md`, another arm's output, or any post-hoc interpretation.
7. Record conversation/session identifier if visible, start/end timestamps, and confirmation that GPT-5.6 Sol was selected.

Frozen task order:
`T6, T1, T8, T3, T7, T2, T9, T4, T10, T5`

Arm A must not be asked for an attestation or active governance checklist.
Arms B and C use the exact pre-generated nonces embedded in their launch packets. Do not replace them after the session begins.

If a session is accidentally contaminated by another arm, the rubric, expected behavior, coaching, a model change, or a task-order change, preserve the evidence and mark the run as an execution deviation. Do not silently restart or substitute a new scored run without PI authorization.

## Capture format

For each session save:
- participant: ChatGPT
- runtime/model: GPT-5.6 Sol
- arm identifier (operator metadata only)
- session/conversation identifier if available
- start/end timestamps
- CoA SHA-256: `5238db6e1765011ca81c0eb68835bcd4de4244607e053c31a73c7e9c99cc3107`
- nonce for B/C
- raw initialization/attestation response
- task ID and exact task text
- complete raw participant response for each task
- any execution deviation

Do not score while collecting.
