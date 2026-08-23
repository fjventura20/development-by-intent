# Contributing

Thank you for testing Development by Intent.

This project values **reproducible evidence over advocacy**. You do not need to agree with the thesis to contribute.

## High-value contributions

- reproduce an existing experiment independently
- submit a failed reconstruction with evidence
- run an experiment with a different AI model
- improve behavioral tests
- propose an application that challenges the methodology
- quantify development or modification time
- identify hidden assumptions in the theory
- propose a better durability or preservation mechanism

## Before opening a pull request

For experimental results, include:

1. **Experiment ID** — short unique identifier.
2. **Date** — UTC preferred.
3. **Model/runtime** — provider, model name, and version/date if known.
4. **Inputs** — exactly what artifacts or transcript were supplied.
5. **Procedure** — enough detail for another contributor to repeat it.
6. **Expected behavior** — reference the behavioral test or baseline.
7. **Observed behavior** — include both passes and failures.
8. **Interpretation** — distinguish evidence from hypothesis.
9. **Raw artifacts** — prompts, outputs, test results, or scripts when practical.

## Evidence rules

Please do not report a reconstruction as successful solely because it "looks similar." Use explicit behavioral tests wherever possible.

Do not silently repair a reconstruction before testing it. If intervention is required, record the intervention as part of the result.

Negative results are welcome.

## Suggested workflow

1. Fork the repository.
2. Choose an existing experiment or open an issue proposing a new one.
3. Create a branch.
4. Add the experiment under `experiments/` or update an example's test evidence.
5. Open a pull request describing what the result supports or contradicts.

## Scope discipline

This repository is studying a software-development methodology. Avoid broad claims about AI replacing software engineering unless directly supported by reproducible evidence.
