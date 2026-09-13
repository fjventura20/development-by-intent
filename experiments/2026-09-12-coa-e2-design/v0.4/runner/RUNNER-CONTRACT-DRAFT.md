# COA-E2 v0.4 Runner Contract

`run_pilot.py --dry-run` validates the package manifest structure, path confinement, nonce keys and omissions, exact two-profile plan, counterbalanced order, 6-turn/12-turn counts, participant prompt/rubric separation, required runtime metadata, and canonical packet rule. It never creates profiles or invokes Hermes.

`--execute` requires a SEALED manifest with two final unique nonces. It performs preflight identity/equivalence and fresh-profile checks, then runs one CoA and one Control session. Every controlling failure writes a structured STOP under the supplied evidence root before exit.
