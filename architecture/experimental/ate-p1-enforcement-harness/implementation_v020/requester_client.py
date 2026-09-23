"""ATE P1 v0.2 — requester client.

Runs as `ate-requester`. Connects to authority.sock and executor.sock
via Unix domain sockets. Carries NO state of its own.
"""
import json
import os
import socket
import struct
from typing import Any, Dict


def _send(sock_path: str, req: Dict[str, Any]) -> Dict[str, Any]:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock_path)
    payload = (json.dumps(req) + "\n").encode("utf-8")
    s.sendall(payload)
    buf = b""
    while not buf.endswith(b"\n"):
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return json.loads(buf.decode("utf-8"))


def call_authority(sock_path: str, req: Dict[str, Any]) -> Dict[str, Any]:
    return _send(sock_path, req)


def call_executor(sock_path: str, req: Dict[str, Any]) -> Dict[str, Any]:
    return _send(sock_path, req)
