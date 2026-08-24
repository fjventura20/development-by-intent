# Results

Store public Amazing Birthday reconstruction results here.

Each result should preserve enough information for another person to understand exactly what was tested.

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
    └── score.md
```

## Required metadata

Record:

- repository commit SHA;
- reconstruction mode: artifact-only or full-transcript;
- provider/platform;
- model name/version if known;
- execution date;
- tools available, especially web/search;
- memory/project context state;
- exact artifacts supplied;
- any contamination or protocol deviation;
- evaluator identity or method;
- raw outputs;
- rubric scores and final classification.

## Do not report only successes

Failures, partial reconstructions, model variance, and surprising behavior are valuable evidence. Preserve them.

The repository is intended to test the limits of Development by Intent, not to curate only favorable demonstrations.
