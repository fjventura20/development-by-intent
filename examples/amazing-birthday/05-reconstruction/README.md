# 05 — Reconstruction Procedure

This procedure is designed so another developer can attempt Amazing Birthday reconstruction without relying on the original project's hidden context.

## A. Choose the experiment mode

Declare one mode before starting:

### Artifact-only

Supply only:

- `03-behavioral-baseline.md`
- `04-durable-package/RECONSTRUCTION-PROMPT.md`

Do not provide the original transcript.

### Full-transcript

Supply the verbatim development transcript and whatever additional artifacts the experiment declaration explicitly permits.

Do not mix artifact sets without recording the change.

## B. Create an isolated environment

Use a fresh chat, project, agent workspace, or equivalent environment that has no prior Amazing Birthday memory.

Record:

- provider/platform;
- model name;
- model version/date if visible;
- system/project instructions that materially affect behavior;
- web/search availability;
- memory availability;
- execution date.

If prior context may have leaked into the environment, record the run as contaminated rather than silently accepting it.

## C. Install the declared artifacts

Give the reconstructing AI only the artifact set declared for the experiment.

For artifact-only reconstruction, provide the behavioral baseline and reconstruction prompt, then allow the AI to establish the reusable behavior.

Do not provide one of the test-date expected narratives. The test should exercise generalization, not imitation.

## D. Freeze before testing

Once the environment says the application is ready:

1. make no corrective changes;
2. record the reconstruction transcript;
3. record the repository commit SHA used;
4. begin the tests.

## E. Run the tests

Use `../tests/behavioral-tests.md`.

Preserve the raw outputs before scoring them.

## F. Score independently

Use `../06-validation.md`.

The key question is not whether wording matches an earlier report. It is whether the reconstructed application exhibits the same behavioral identity on inputs it was not built around.

## G. Only then repair

If a test fails, preserve the failure first. A subsequent correction creates a new experimental phase and should be recorded as such.

The failure is evidence about the durability package; erasing it by immediate conversational repair defeats the experiment.
