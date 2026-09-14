# COA-E2 v0.4.3 Freeze Manifest — DRAFT

At a future freeze, this manifest will list every controlling v0.4.3 file
relative to the declared package root, excluding the manifest itself. The
external freeze record will contain this JSON's SHA-256. It will contain
exactly six final pairwise-unique nonces in a separate runtime manifest
under the keys: `coa-init`, `coa-digest`, `coa-nonce`, `control-init`,
`control-digest`, `control-nonce`. No v0.3 file is controlling. Freeze is
blocked until the mechanism check, dry-run, prompt/rubric separation,
packet token tolerance, two-profile freshness/equivalence, blank initial
memory/user state, six pairwise-unique nonces, ACK field-value
comparison, session-ID parser, and consistency audit pass.
