# Results

Store public Receipt Organizer reconstruction results here.

Each result should preserve enough information for another person to understand
exactly what was tested.

## Suggested result layout

```text
results/
└── YYYY-MM-DD-provider-model-run-N/
    ├── README.md
    ├── environment.md
    ├── reconstruction-transcript.md
    ├── test-1-output.md
    ├── test-2-output.md
    ├── test-3-output.md
    ├── test-4-output.md
    ├── test-5-output.md
    ├── generalization-output.md
    ├── score.md
    └── ledger-snapshot.md   # full ledger state at end of conversation
```

## Required metadata

Record:

- repository commit SHA;
- reconstruction mode: artifact-only or full-transcript;
- provider/platform;
- model name/version if known;
- execution date;
- tools available;
- memory/project context state;
- exact artifacts supplied;
- any contamination or protocol deviation;
- **environment-state-loss check**: did the ledger persist across turns? Record the
  check explicitly;
- evaluator identity or method;
- raw outputs for each test;
- ledger snapshot at end of conversation;
- rubric scores and final classification.

## Do not report only successes

Failures, partial reconstructions, model variance, and surprising behavior are
valuable evidence. Preserve them.

The repository is intended to test the limits of Development by Intent, not to curate
only favorable demonstrations.