# COA-E2 v0.4 Runner

`run_pilot.py` is the deterministic operator. It supports `--dry-run` and sealed-manifest `--execute`; it never asks a model to make execution decisions. The draft manifest remains unsealed, has two nonce keys with explicit omissions, and cannot execute.

`verify_manifest.py` resolves every path relative to `--package-root`. `audit_after_turn.py` is fail-closed and writes STOP records. `generate_nonces.py` generates two values only after a future freeze decision.
