from __future__ import annotations

import dataclasses
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from ate_p1.audit import append_event, verify_chain
from ate_p1.enforcer import Authorization, EnforcementDenied, LocalEnforcer
from ate_p1.resource import ProtectedResource, ResourceDenied
from ate_p1.state import EnforcementState

CAP = "executor-capability-7ddaf4c9"


def make(tmp: Path):
    state = EnforcementState(tmp / "state.db")
    resource = ProtectedResource(CAP)
    return state, resource, LocalEnforcer(state, resource, CAP)


def auth(nonce="n-001", subject="agent-A", value="UPDATED"):
    return Authorization("env-001", subject, nonce, "write", "protected-resource", value)


def test_p1_01_direct_resource_bypass_denied(tmp_path: Path):
    _, resource, _ = make(tmp_path)
    with pytest.raises(ResourceDenied, match="DIRECT_RESOURCE_BYPASS_DENIED"):
        resource.write("caller-does-not-have-capability", "PWNED")
    assert resource.read_for_test() == "INITIAL"


def test_p1_02_executor_credential_separation(tmp_path: Path):
    _, _, enforcer = make(tmp_path)
    request = dataclasses.asdict(auth())
    assert CAP not in repr(request)
    assert not hasattr(enforcer, "executor_credential")


def test_p1_03_durable_nonce_survives_restart(tmp_path: Path):
    state, _, enforcer = make(tmp_path)
    enforcer.execute(auth("restart-nonce"))
    del enforcer, state
    state2 = EnforcementState(tmp_path / "state.db")
    resource2 = ProtectedResource(CAP)
    enforcer2 = LocalEnforcer(state2, resource2, CAP)
    assert state2.nonce_consumed("restart-nonce")
    with pytest.raises(EnforcementDenied, match="NONCE_REPLAY"):
        enforcer2.execute(auth("restart-nonce"))


def test_p1_04_concurrent_replay_exactly_one_winner(tmp_path: Path):
    state = EnforcementState(tmp_path / "state.db")
    def attempt(i: int) -> bool:
        return state.consume_nonce("race-nonce", f"env-{i}")
    with ThreadPoolExecutor(max_workers=12) as pool:
        results = list(pool.map(attempt, range(24)))
    assert sum(results) == 1


def test_p1_05_revocation_checked_at_execution_boundary(tmp_path: Path):
    state, resource, enforcer = make(tmp_path)
    def revoke_after_admission():
        state.revoke("agent-A", "operator revocation")
    with pytest.raises(EnforcementDenied, match="SUBJECT_REVOKED"):
        enforcer.execute(auth("revoked-nonce"), before_reverify=revoke_after_admission)
    assert resource.read_for_test() == "INITIAL"


def test_p1_06_executor_reverification_detects_substitution(tmp_path: Path):
    state, resource, enforcer = make(tmp_path)
    original = auth("substitution-nonce")
    substitute = dataclasses.replace(original, value="ATTACK")
    with pytest.raises(EnforcementDenied, match="EXECUTOR_REVERIFICATION_FAILED"):
        enforcer._verify(substitute, original.digest())
    assert resource.read_for_test() == "INITIAL"


def test_p1_07_audit_chain_detects_payload_tampering(tmp_path: Path):
    state, _, _ = make(tmp_path)
    append_event(state, "A", "env-1", {"x": 1})
    append_event(state, "B", "env-2", {"x": 2})
    assert verify_chain(state)
    with state._connect() as conn:
        conn.execute("UPDATE audit SET payload_json='{}' WHERE sequence=1")
    assert not verify_chain(state)


def test_p1_08_audit_chain_detects_deletion(tmp_path: Path):
    state, _, _ = make(tmp_path)
    append_event(state, "A", "env-1", {"x": 1})
    append_event(state, "B", "env-2", {"x": 2})
    append_event(state, "C", "env-3", {"x": 3})
    with state._connect() as conn:
        conn.execute("DELETE FROM audit WHERE sequence=2")
    assert not verify_chain(state)


def test_p1_09_success_path_is_enforced_and_audited(tmp_path: Path):
    state, resource, enforcer = make(tmp_path)
    assert enforcer.execute(auth("success-nonce", value="AUTHORIZED")) == "EXECUTION_OK"
    assert resource.read_for_test() == "AUTHORIZED"
    assert state.nonce_consumed("success-nonce")
    assert verify_chain(state)
    assert [r["event_type"] for r in state.audit_rows()] == ["ADMISSION_OK", "EXECUTION_OK"]
