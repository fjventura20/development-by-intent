# 05 — Reconstruction Procedure

This procedure is designed so another developer can attempt Receipt Organizer
reconstruction without relying on the original project's hidden context.

## A. Choose the experiment mode

Declare one mode before starting:

### Artifact-only

Supply only:

- `../03-behavioral-baseline.md`
- `../04-durable-package/RECONSTRUCTION-PROMPT.md`

Do not provide the original transcript.

### Full-transcript

Supply the verbatim development transcript and whatever additional artifacts the
experiment declaration explicitly permits.

Do not mix artifact sets without recording the change.

## B. Create an isolated environment

Use a fresh chat, project, agent workspace, or equivalent environment that has no
prior Receipt Organizer memory.

Record:

- provider/platform;
- model name;
- model version/date if visible;
- system/project instructions that materially affect behavior;
- tool/script availability;
- memory availability;
- persistence availability;
- execution date.

If prior context may have leaked into the environment, record the run as contaminated
not silently accepting it.

## C. Install the declared artifacts

Give the reconstructing AI only the artifact set declared for the experiment.

For artifact-only reconstruction, provide the behavioral baseline and reconstruction
prompt, then allow the AI to establish the reusable behavior.

Do not provide any of the test receipts. The test should exercise generalization, not
imitation of the development corpus.

## D. Freeze before testing

Once the environment says the application is ready:

1. make no corrective changes;
2. record the reconstruction transcript (the AI's acceptance statement);
3. record the repository commit SHA used;
4. begin the tests.

## E. Run the tests

Use `../tests/behavioral-tests.md`.

For each test receipt, paste it and let the AI respond. For each query test, send
the query after the prior ingestions in the same conversation. Preserve the raw
outputs before scoring them.

Critical: tests must run **in the same conversation** as the reconstruction step. Do
NOT start a fresh chat per test. The application must maintain its ledger across
inputs.

## F. Score independently

Use `../06-validation.md`.

The key question is not whether the AI echoes words from the development transcript.
It is whether the reconstructed application exhibits the same behavioral identity
on inputs it was not built around.

## G. Only then repair

If a test fails, preserve the failure first. A subsequent correction creates a new
experimental phase and should be recorded as such.

The failure is evidence about the durability package; erasing it by immediate
conversational repair defeats the experiment.

## State-management caveat

Unlike Amazing Birthday (stateless), Receipt Organizer is stateful. The
reconstructing environment must retain the running ledger across turns. If the
environment loses state between turns, the experiment is invalid; record this as a
**environment-state-loss failure** rather than a behavioral failure.