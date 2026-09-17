#!/usr/bin/env python3
"""Repair FR-11 host runtime so same-principal UID transitions are re-entrant.

The trusted controller may enter an executor-scoped operation that calls a
connection proxy which is itself executor-scoped. That nested same-principal
call must be a no-op, not an error. Cross-principal switching from a non-root
effective UID remains prohibited.

This script patches the generated tests/host_runtime.py only. It does not run
tests, bootstrap, preflight, or the formal scored run.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "tests" / "host_runtime.py"
text = path.read_text()
old = '''@contextmanager
def as_user(name: str):
    """Temporarily switch effective uid/gid inside a trusted root process."""
    if os.geteuid() != 0:
        raise PermissionError("FR-11 formal host runtime requires root trusted controller")
    pw = pwd.getpwnam(name)
    old_uid, old_gid = os.geteuid(), os.getegid()
    try:
        os.setegid(pw.pw_gid)
        os.seteuid(pw.pw_uid)
        yield
    finally:
        os.seteuid(old_uid)
        os.setegid(old_gid)
'''
new = '''@contextmanager
def as_user(name: str):
    """Temporarily switch effective uid/gid in the trusted controller.

    Re-entrant same-principal calls are allowed: executor code can call an
    executor-scoped connection proxy without trying to regain root first.
    A non-root principal may never switch directly to a different principal.
    """
    pw = pwd.getpwnam(name)
    current_uid, current_gid = os.geteuid(), os.getegid()

    # Already executing as the requested principal: nested scope is a no-op.
    if current_uid == pw.pw_uid:
        yield
        return

    # Only the trusted root controller may cross into another principal.
    if current_uid != 0:
        raise PermissionError(
            f"FR-11 principal switch denied: euid={current_uid} -> {name}({pw.pw_uid})"
        )

    try:
        os.setegid(pw.pw_gid)
        os.seteuid(pw.pw_uid)
        yield
    finally:
        os.seteuid(current_uid)
        os.setegid(current_gid)
'''
if text.count(old) != 1:
    raise SystemExit(f"expected one as_user block; found {text.count(old)}")
path.write_text(text.replace(old, new, 1))
print("FR-11 reentrant UID repair applied: tests/host_runtime.py")
print("Formal scored run remains unauthorized.")
