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


def test_fr13_run_formal_six_lock_block_appears_exactly_once():
    """FR-13 PF1 six-lock block must appear EXACTLY ONCE in run_formal.py.

    Patcher residue from earlier runs could leave many copies. This regression
    test asserts exactly one occurrence so a duplicate-paste bug is caught
    before it pollutes scored evidence.
    """
    src = inspect.getsource(run_formal.run_preflight)
    block = (
        '    # PF1 also binds the exact six frozen specification blobs from the\n'
        '    # v0.2.2 freeze manifest.  Missing/mismatched locks fail closed.\n'
        '    locks = verify_frozen_spec_locks(repo_dir)\n'
        '    pf1 = next((x for x in results if x.item == "PF1"), None)\n'
        '    if pf1 is not None:\n'
        '        if not all(x["verified"] for x in locks):\n'
        '            pf1.result = "FAIL"\n'
        '        pf1.evidence += "; six_spec_locks=" + ("PASS" if all(x["verified"] for x in locks) else "FAIL")\n'
    )
    n = src.count(block)
    assert n == 1, f"PF1 six-lock block appears {n} times; expected exactly 1"
