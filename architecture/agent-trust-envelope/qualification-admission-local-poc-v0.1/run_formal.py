#!/usr/bin/env python3
"""ATE Qualification & Admission Local PoC v0.1 — formal scored runner.

THIS SCRIPT REQUIRES AN EXPLICIT AUTHORIZATION FLAG.

Per the implementation handoff, the formal scored QA-P1..QA-P14 run is
withheld. The runner exists to prove that the implementation supports
the full test matrix; it is gated so that it CANNOT be launched
accidentally.

Usage:

  python3 run_formal.py --formal-run-authorization-token ATE-FORMAL-RUN-AUTHORIZED-BY-FRANK-AS-PI-2026-09-16

Without that flag (or with any other token) the script refuses to
launch and exits 77.

DO NOT modify this script to lower the gate. Per design §33, weakening
the authorization gate is a STOP condition.
"""

from __future__ import annotations

import argparse
import os
import sys

# The literal token must match the implementation-authorization note
# in the handoff. It is a fixed string, NOT a secret.
FORMAL_RUN_TOKEN = "ATE-FORMAL-RUN-AUTHORIZED-BY-FRANK-AS-PI-2026-09-16"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--formal-run-authorization-token",
        default="",
        help="Required literal token to launch the formal scored QA-P1..QA-P14 run.",
    )
    args = parser.parse_args()

    if args.formal_run_authorization_token != FORMAL_RUN_TOKEN:
        print(
            "REFUSED: formal scored QA-P1..QA-P14 run is withheld.\n"
            "Per the implementation handoff and design §33, this runner\n"
            "requires --formal-run-authorization-token "
            f"{FORMAL_RUN_TOKEN!r}.\n"
            "The token is not provided in this handoff. Exiting.",
            file=sys.stderr,
        )
        return 77

    # If ever launched with the correct token: dispatch to the QA matrix
    # test runner (NOT IMPLEMENTED in this handoff because the formal
    # run is withheld).
    print(
        "AUTHORIZED: would launch QA-P1..QA-P14 matrix now, but the\n"
        "matrix runner is not wired into this handoff (formal run is\n"
        "withheld). Exiting cleanly.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
