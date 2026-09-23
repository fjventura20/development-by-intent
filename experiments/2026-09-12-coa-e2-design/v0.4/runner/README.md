# COA-E2 v0.4.1 Runner

`run_pilot.py` is the deterministic operator. It supports `--dry-run` and
sealed-manifest `--execute`; it never asks a model to make execution
decisions. The draft manifest remains unsealed, has six nonce keys with
explicit omissions, and cannot execute.

`verify_manifest.py` resolves every path relative to `--package-root`.
`audit_after_turn.py` is fail-closed and writes STOP records.
`generate_nonces.py` generates six pairwise-unique values only after a
future freeze decision.

The dry-run validator also exercises the
`classifier → session-summary → aggregator` path using synthetic fixtures,
the ACK field-value comparator using a synthetic ACK fixture, and the
session-ID parser using synthetic CLI-footer fixtures that match the
declared footer channel.
