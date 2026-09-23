# Contributing

Thank you for testing Development by Intent.

This project values **reproducible evidence over advocacy**. You do not need to agree with the thesis to contribute.

## Fastest contribution

If you have about five minutes, start with [`QUICK-VALIDATION.md`](QUICK-VALIDATION.md). It asks for one fresh-environment observation and explicitly welcomes failures.

That path is exploratory evidence rather than a formal replication, but it is useful for discovering external failure modes and deciding which observations deserve stricter follow-up.

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
10. **Evaluation condition** — state who scored the result and whether scoring was operator, independent, blinded, or some combination. Do not use `independent` as a synonym for `blinded`.

## Evidence rules

Please do not report a reconstruction as successful solely because it "looks similar." Use explicit behavioral tests wherever possible.

Do not silently repair a reconstruction before testing it. If intervention is required, record the intervention as part of the result.

Negative results are welcome. A reproducible failure is a research contribution, not a failed contribution.

## Suggested workflow

1. Fork the repository.
2. Choose an existing experiment or open an issue proposing a new one.
3. Create a branch.
4. Add the experiment under `experiments/` or update an example's test evidence.
5. Open a pull request describing what the result supports or contradicts.

## Scope discipline

This repository is studying an experimental software-development pattern and a broader intelligence-native architecture. Avoid broad claims about AI replacing software engineering unless directly supported by reproducible evidence.

## Maintainer expectations

This is a best-effort research project, not a supported product. Opening an issue or pull request does not create an obligation for the maintainer to respond, review, merge, or provide technical support.

To keep the project sustainable, priority is given to contributions that add reproducible evidence, challenge a specific claim, improve an experiment, or materially clarify the methodology. General feature requests and open-ended support requests may be closed without action.