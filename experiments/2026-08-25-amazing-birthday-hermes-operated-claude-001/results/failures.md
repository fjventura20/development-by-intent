# Failures — Hermes-Operated Claude Portability 001

This file preserves the material operator-side issues from the Hermes result package. The SHA-bound source record is identified in `hermes-manifest.json`.

## F1 — Frozen source commit absent at run start

The frozen source commit `c369215024c9f8a849daf11bd4b872d7ee566a7a` was not present in the operator's local clone at run start. Hermes proceeded using the two inbound Phase A artifacts. Post-run, Hermes fetched the frozen commit and verified that both Phase A files were byte-identical to the inbound package and that the development-example dates did not overlap the three frozen test dates.

**Operator assessment:** resolved; not material to target behavior.

## F2 — Claude OAuth bearer token stale at start

Initial authentication attempts failed with 401 despite local auth state reporting logged in. OAuth was manually refreshed before the canonical successful target session. Pre-refresh failed attempts did not produce a usable test session.

**Operator assessment:** operational; resolved; not material.

## F3 — Reconstruction prompt re-issued for capture

The first reconstruction/freeze call was displayed in the operator terminal but its JSON was not written to disk. Hermes later re-issued the same reconstruction prompt in the same session to obtain a disk-captured response.

Hermes later added `reconstruction.first-run.md`, describing the first response from terminal scrollback and explicitly stating that the text was reconstructed verbatim from the operator's memory of what was displayed.

**Operator assessment:** no behavioral change; capture-pass rather than repair.

**Independent-review relevance:** this is an evidence-capture deviation because the preregistration required the first outputs to be evidence.

## F4 — Test 1 re-issued for capture

The first `Birthdate November 9, 1989` response was displayed in the operator terminal but its JSON was not written to disk. Hermes re-issued the same test prompt in the same session. The two responses differed in prose: the reported first response opened with the Schabowski press conference; the re-issued response opened with Rostropovich.

Hermes later added `test-1-output.first-run.md`, describing the first response from terminal scrollback and explicitly noting that it was reconstructed verbatim from operator memory rather than recovered as a contemporaneous raw envelope.

**Operator assessment:** both outputs independently score 19/20; no material behavioral repair.

**Independent-review relevance:** the true first Test 1 output is not independently SHA-verifiable. The second output is verifiable but is not the preregistered first output.

## F5 — No web verification

Claude was run with `--allowedTools ''`; factual claims came from model knowledge rather than in-loop verification. This strengthened isolation but reduced factual verification.

## Other recorded issues

- additional inference cost from the capture re-runs;
- `claude doctor` timed out during an environment probe;
- small Haiku usage appeared in one Claude Code routing envelope while substantive generation was Sonnet 4.6.

## Operator / reviewer distinction

Hermes concluded that none of these issues were materially contaminating and retained an operator-level PASS. ChatGPT's independent review evaluates the evidence-capture deviations separately under the frozen experiment-level rule.