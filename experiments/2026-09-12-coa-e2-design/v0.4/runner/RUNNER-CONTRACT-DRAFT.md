# COA-E2 v0.4.1 Runner Contract

`run_pilot.py --dry-run` validates the package manifest structure, path
confinement, six pairwise-unique nonce keys (with omissions allowed only
when the manifest status is `DRAFT_TEMPLATE`), exact two-profile plan,
fixed predeclared order `CoA-S1, Control-S1` (not counterbalanced),
6-turn/12-turn counts, participant prompt/rubric separation, expected-
action and rubric-leakage scan of every participant prompt, the
`classifier → session-summary → aggregator` synthetic-fixture path, the
ACK field-value comparator against synthetic ACK fixtures, the blank
initial `MEMORY.md`/`USER.md` hash check against synthetic blank fixtures,
and the session-ID parser against synthetic CLI-footer fixtures. It never
creates profiles, invokes Hermes, generates nonces, scores responses, or
freezes the package.

`--execute` requires a `SEALED` manifest with six final unique nonces. It
performs preflight identity/equivalence, blank initial state, and
fresh-profile checks, refuses to execute into a nonempty `--evidence-root`
unless a fresh unique run directory is supplied, then runs one CoA and one
Control session. Every controlling failure writes a structured STOP under
the supplied evidence root before exit.
