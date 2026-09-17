import inspect
from types import SimpleNamespace

import run_formal
from tests import host_runtime


def test_fr13_preflight_requires_exact_pf1_pf14():
    good = [SimpleNamespace(item=f"PF{i}", result="PASS") for i in range(1, 15)]
    assert run_formal.preflight_is_complete_and_passing(good)
    assert not run_formal.preflight_is_complete_and_passing(good[:-1])
    assert not run_formal.preflight_is_complete_and_passing(good + [good[-1]])
    bad = list(good)
    bad[4] = SimpleNamespace(item="PF5", result="FAIL")
    assert not run_formal.preflight_is_complete_and_passing(bad)


def test_fr13_six_literal_frozen_spec_locks_present():
    assert len(run_formal.FROZEN_SPEC_LOCKS) == 6
    assert {x[1] for x in run_formal.FROZEN_SPEC_LOCKS} == {
        "28b4b0a36e7ded946686c0eb45d4ee820a35c2bf",
        "ce6d11cc4a7271fd2cc6b286d2e01b90e5b3edc1",
        "ba1761667260c34ebf9018c6719a9555a8cc34fa",
        "0834105252d8cf0055088eb0d2a572a9c65a17e8",
        "908409107d8404ba6aa58367699a9be91a81e84f",
        "6c4863b031d71c8b0fb0a53bf08e9f7547681d20",
    }


def test_fr13_controller_keybag_loader_does_not_load_private_pem():
    src = inspect.getsource(host_runtime.load_bootstrap_keybag)
    assert "load_ed25519_private_pem" not in src
    assert "_remote(" in src


def test_fr13_remote_signer_is_signature_only_proxy():
    public = {x for x in dir(host_runtime.RemoteEd25519Signer) if not x.startswith("_")}
    assert "sign" in public and "public_key" in public
    assert "private_bytes" not in public
